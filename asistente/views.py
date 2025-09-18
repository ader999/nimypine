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
from cuentas.models import Mipyme
from produccion.models import Producto, Insumo, Venta, VentaItem
from .models import Conversacion, Mensaje
import openai
import google.generativeai as genai

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
                'stock_actual': p.stock_actual
            } for p in Producto.objects.filter(mipyme=mipyme)
        ],
        'insumos': [
            {
                'nombre': i.nombre,
                'costo_unitario': float(i.costo_unitario) if i.costo_unitario else None,
                'stock_actual': float(i.stock_actual) if i.stock_actual else None
            } for i in Insumo.objects.filter(mipyme=mipyme)
        ],
        'ventas': [
            {
                'fecha': str(v.fecha),
                'total': float(v.total) if v.total else None
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
def asistente_view(request):
    if not hasattr(request.user, 'mipyme') or not request.user.mipyme:
        return redirect('cuentas:no_mipyme_asociada')

    conversacion, created = Conversacion.objects.get_or_create(
        usuario=request.user,
        defaults={'titulo': 'Nueva conversación'}
    )

    if request.method == 'POST':
        mensaje_usuario = request.POST.get('mensaje')
        modelo_seleccionado = request.POST.get('modelo', 'openai')
        if mensaje_usuario:
            # Guardar mensaje del usuario
            Mensaje.objects.create(conversacion=conversacion, contenido=mensaje_usuario, es_usuario=True)

            # Procesar el mensaje
            respuesta = procesar_mensaje(mensaje_usuario, request.user, modelo_seleccionado)

            # Guardar respuesta del asistente
            Mensaje.objects.create(conversacion=conversacion, contenido=respuesta, es_usuario=False)

            return JsonResponse({'respuesta': respuesta})

    mensajes = conversacion.mensajes.all().order_by('fecha')
    return render(request, 'asistente/asistente.html', {'mensajes': mensajes})

def procesar_mensaje(mensaje, user, model='openai'):
    mensaje_lower = mensaje.lower()

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

    else:
        # Respuesta general con AI
        data = get_company_data(user)
        prompt = f"Responde como asistente para mipymes. Datos de la empresa: {json.dumps(data)}. Mensaje del usuario: {mensaje}"
        return get_ai_response(prompt, model)
