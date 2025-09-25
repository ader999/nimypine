import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import connection
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.files.storage import default_storage
from cuentas.models import Mipyme
from produccion.models import Producto, Insumo, Venta, VentaItem, Proceso, PasoDeProduccion, Formulacion
from .models import Conversacion, Mensaje, GuiaUsuario
import openai
import google.generativeai as genai
import markdown

# Configurar APIs
openai.api_key = os.getenv('OPENAI_API_KEY')
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def get_ai_response(prompt, model='openai'):
    try:
        if model == 'openai':
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        elif model == 'gemini':
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text
        elif model == 'deepseek':
            # For DeepSeek, use requests
            import requests
            url = "https://api.deepseek.com/chat/completions"
            headers = {
                "Authorization": f"Bearer {os.getenv('deepseek_API_KEY')}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}]
            }
            response = requests.post(url, headers=headers, json=data)
            return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Error con {model}: {str(e)}"

def get_company_data(user):
    mipyme = user.mipyme
    data = {
        'nombre': mipyme.nombre,
        'telefono': mipyme.numero_telefono,
        'correo': mipyme.correo,
        'tipo': mipyme.tipo.nombre if mipyme.tipo else None,
        'sector': mipyme.sector.nombre if mipyme.sector else None,
        'productos': [
            {
                'nombre': p.nombre,
                'precio_venta': float(p.precio_venta) if p.precio_venta else None,
                'stock_actual': p.stock_actual,
                'formulacion': [
                    {
                        'insumo': f.insumo.nombre,
                        'unidad': f.insumo.unidad.abreviatura,
                        'cantidad': float(f.cantidad),
                        'porcentaje_desperdicio': float(f.porcentaje_desperdicio)
                    } for f in Formulacion.objects.filter(producto=p)
                ],
                'pasos_produccion': [
                    {
                        'proceso': pdp.proceso.nombre,
                        'tiempo_minutos': pdp.tiempo_en_minutos
                    } for pdp in PasoDeProduccion.objects.filter(producto=p)
                ]
            } for p in Producto.objects.filter(mipyme=mipyme)
        ],
        'insumos': [
            {
                'nombre': i.nombre,
                'costo_unitario': float(i.costo_unitario) if i.costo_unitario else None,
                'stock_actual': float(i.stock_actual) if i.stock_actual else None
            } for i in Insumo.objects.filter(mipyme=mipyme)
        ],
        'procesos': [
            {
                'nombre': pr.nombre,
                'costo_por_hora': float(pr.costo_por_hora)
            } for pr in Proceso.objects.filter(mipyme=mipyme)
        ],
        'ventas': [
            {
                'fecha': str(v.fecha),
                'total': float(v.total) if v.total else None,
                'items': [
                    {
                        'producto': vi.producto.nombre,
                        'cantidad': vi.cantidad,
                        'precio_unitario': float(vi.precio_unitario),
                        'subtotal': float(vi.subtotal)
                    } for vi in VentaItem.objects.filter(venta=v)
                ]
            } for v in Venta.objects.filter(mipyme=mipyme)
        ],
    }
    return data

def execute_sql_query(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
    return columns, results

def execute_code(code):
    # Ejecutar código de forma segura (limitada)
    try:
        exec_globals = {'pd': pd, 'plt': plt}
        exec(code, exec_globals)
        return "Código ejecutado exitosamente."
    except Exception as e:
        return f"Error: {str(e)}"

def generate_graph(code):
    try:
        exec(code)
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        return image_base64
    except Exception as e:
        return f"Error generando gráfico: {str(e)}"

@login_required
def asistente_view(request, conversacion_id=None):
    if not hasattr(request.user, 'mipyme') or not request.user.mipyme:
        if request.user.is_superuser:
            return redirect('admin:index')
        return redirect('cuentas:no_mipyme_asociada')

    conversacion = None
    if conversacion_id:
        conversacion = get_object_or_404(Conversacion, id=conversacion_id, usuario=request.user)

    if request.method == 'POST':
        mensaje_usuario = request.POST.get('mensaje')
        modelo_seleccionado = request.POST.get('modelo', 'openai')
        if mensaje_usuario:
            if not conversacion:
                # Crear una nueva conversación solo cuando se envía el primer mensaje
                conversacion = Conversacion.objects.create(
                    usuario=request.user,
                    titulo=mensaje_usuario[:20] + '...' if len(mensaje_usuario) > 50 else mensaje_usuario
                )

            # Guardar mensaje del usuario
            Mensaje.objects.create(conversacion=conversacion, contenido=mensaje_usuario, es_usuario=True)

            # Procesar el mensaje
            respuesta = procesar_mensaje(mensaje_usuario, request.user, modelo_seleccionado)

            # Guardar respuesta del asistente
            Mensaje.objects.create(conversacion=conversacion, contenido=respuesta, es_usuario=False)

            return JsonResponse({'respuesta': respuesta})

    mensajes = conversacion.mensajes.all().order_by('fecha') if conversacion else []
    # Procesar mensajes para convertir Markdown a HTML en respuestas del asistente
    mensajes_procesados = []
    for m in mensajes:
        if not m.es_usuario:
            m.contenido = markdown.markdown(m.contenido, extensions=['extra'])
        mensajes_procesados.append(m)
    # Solo mostrar conversaciones que tengan al menos un mensaje
    conversaciones = Conversacion.objects.filter(
        usuario=request.user,
        mensajes__isnull=False
    ).distinct().order_by('-fecha_inicio')
    avatar_url = default_storage.url('nimypine/material/sinfotouser.png')
    return render(request, 'asistente/asistente.html', {
        'mensajes_procesados': mensajes_procesados,
        'conversaciones': conversaciones,
        'conversacion_actual': conversacion,
        'avatar_url': avatar_url,
        'nombrepine': request.user.mipyme.nombre
    })

def procesar_mensaje(mensaje, user, model='openai'):
    mensaje_lower = mensaje.lower()

    # Validación previa: verificar si el mensaje está relacionado con temas de mipymes
    palabras_clave = [
        'produccion', 'insumo', 'venta', 'proceso', 'formulacion', 'producto', 'mipyme',
        'empresa', 'ventas', 'facturacion', 'estandarizar', 'sql', 'codigo', 'grafico',
        'agregar', 'registrar', 'crear', 'materia prima', 'materias primas', 'pasos produccion',
        'produccion pasos', 'datos empresa'
    ]
    if not any(kw in mensaje_lower for kw in palabras_clave):
        return "Lo siento, solo puedo ayudarte con temas relacionados con la gestión de tu mipyme, como producción, ventas, insumos o procesos. ¿En qué puedo asistirte en esos aspectos?"

    if 'estandarizar' in mensaje_lower:
        data = get_company_data(user)
        prompt = f"Sugerencias para estandarizar productos basadas en estos datos: {json.dumps(data)}"
        return get_ai_response(prompt, model)

    elif 'datos empresa' in mensaje_lower or 'empresa' in mensaje_lower:
        data = get_company_data(user)
        return json.dumps(data, indent=2)

    elif 'productos' in mensaje_lower and 'ultima venta' in mensaje_lower:
        # Última venta y sus productos
        ultima_venta = Venta.objects.filter(mipyme=user.mipyme).order_by('-fecha').first()
        if ultima_venta:
            items = VentaItem.objects.filter(venta=ultima_venta)
            productos = '\n'.join([f"{item.producto.nombre}: {item.cantidad} x ${item.precio_unitario}" for item in items])
            return f"Productos de la última venta (#{ultima_venta.id} - {ultima_venta.fecha}):\n{productos}"
        else:
            return "No hay ventas registradas."

    elif 'productos' in mensaje_lower:
        productos = Producto.objects.filter(mipyme=user.mipyme)
        return '\n'.join([f"{p.nombre}: ${p.precio_venta}" for p in productos])

    elif 'insumos' in mensaje_lower:
        insumos = Insumo.objects.filter(mipyme=user.mipyme)
        return '\n'.join([f"{i.nombre}: ${i.costo_unitario}" for i in insumos])

    elif 'ventas' in mensaje_lower or 'facturacion' in mensaje_lower:
        ventas = Venta.objects.filter(mipyme=user.mipyme)
        return '\n'.join([f"Venta #{v.id}: ${v.total} - {v.fecha}" for v in ventas])

    elif 'procesos' in mensaje_lower:
        procesos = Proceso.objects.filter(mipyme=user.mipyme)
        return '\n'.join([f"{p.nombre}: ${p.costo_por_hora}/hora" for p in procesos])

    elif 'formulacion' in mensaje_lower:
        productos = Producto.objects.filter(mipyme=user.mipyme)
        response = ""
        for p in productos:
            response += f"\nProducto: {p.nombre}\n"
            formulaciones = Formulacion.objects.filter(producto=p)
            for f in formulaciones:
                response += f"  - {f.insumo.nombre}: {f.cantidad} {f.insumo.unidad.abreviatura} (desperdicio: {f.porcentaje_desperdicio}%)\n"
        return response

    elif 'pasos produccion' in mensaje_lower or 'produccion pasos' in mensaje_lower:
        productos = Producto.objects.filter(mipyme=user.mipyme)
        response = ""
        for p in productos:
            response += f"\nProducto: {p.nombre}\n"
            pasos = PasoDeProduccion.objects.filter(producto=p)
            for paso in pasos:
                response += f"  - {paso.proceso.nombre}: {paso.tiempo_en_minutos} minutos\n"
        return response

    elif 'sql' in mensaje_lower:
        # Extraer query SQL del mensaje
        query = mensaje.split('sql')[1].strip()
        columns, results = execute_sql_query(query)
        return f"Columnas: {columns}\nResultados: {results}"

    elif 'codigo' in mensaje_lower or 'code' in mensaje_lower:
        code = mensaje.split('codigo')[1].strip()
        return execute_code(code)

    elif 'grafico' in mensaje_lower or 'graph' in mensaje_lower:
        code = mensaje.split('grafico')[1].strip()
        return generate_graph(code)

    elif any(kw in mensaje_lower for kw in ['agregar', 'agrego', 'añadir', 'registrar', 'crear']) and any(kw in mensaje_lower for kw in ['insumo', 'insumos', 'materia prima', 'materias primas']):
        # Buscar guía para agregar insumo
        guia = GuiaUsuario.objects.filter(activo=True, palabras_clave__icontains='agregar insumo').first()
        if guia:
            return f"{guia.descripcion}\n\nPasos:\n{guia.pasos}"
        else:
            return "Lo siento, no tengo una guía específica para agregar insumos en este momento."

    else:
        # Respuesta general con AI
        data = get_company_data(user)
        prompt = f"Eres un asistente virtual especializado en ayudar con la gestión de mipymes. Solo responde preguntas relacionadas con producción, ventas, insumos, procesos y datos de la empresa. Si la pregunta no está relacionada con estos temas, responde cortésmente que no puedes ayudar con eso y sugiere volver al tema principal. Datos de la empresa: {json.dumps(data)}. Mensaje del usuario: {mensaje}"
        respuesta = get_ai_response(prompt, model)
        return markdown.markdown(respuesta, extensions=['extra'])
