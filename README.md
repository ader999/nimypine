# 🏭 Nimypine - Plataforma de Gestión Productiva para MIPYMEs

![Django](https://img.shields.io/badge/Django-5.1.4-green.svg)
![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Descripción del Proyecto

**Nimypine** es una plataforma web integral diseñada para empoderar a las micro, pequeñas y medianas empresas (MIPYMEs) en sectores productivos como textil y vestuario, madera y muebles, cuero y productos derivados, así como alimentos y bebidas.

La aplicación permite a las MIPYMEs:
- ✅ Estandarizar sus procesos productivos
- 💰 Gestionar costos de producción de manera precisa
- 📊 Controlar desperdicios e insumos
- 🧮 Calcular proporciones y cantidades para diferentes lotes
- 🛒 Acceder a un marketplace de recursos especializados
- 🤖 Recibir asistencia inteligente para optimizar procesos

## 🎯 Propósito

Nimypine nace como respuesta a los desafíos que enfrentan las MIPYMEs en la gestión de sus procesos productivos:

1. **Falta de estandarización**: Dificultad para mantener consistencia en productos
2. **Control de costos**: Desconocimiento del costo real de producción
3. **Gestión de desperdicios**: Pérdidas económicas por falta de control
4. **Acceso a conocimiento**: Limitado acceso a recursos y mejores prácticas
5. **Escalabilidad**: Dificultad para calcular necesidades al aumentar producción

La plataforma proporciona herramientas digitales que profesionalizan las operaciones, optimizan recursos y mejoran la competitividad de las pequeñas empresas.

## 🚀 Características Principales

### 1. 🏢 Gestión de Sectores y Productos
- Clasificación por sectores económicos
- Registro de productos con especificaciones detalladas
- Configuración de parámetros según el sector

### 2. 📝 Formulaciones y Procesos
- Creación de recetas y formulaciones estandarizadas
- Gestión de procesos de producción paso a paso
- Control de porcentajes de desperdicio por proceso
- Múltiples unidades de medida (kg, g, L, mL, metros, yardas, etc.)

### 3. 🧮 Calculadora de Lotes
- Cálculo automático de cantidades para diferentes lotes
- Ajuste proporcional de todos los insumos
- Consideración de desperdicios en los cálculos
- Estimación de costos por lote

### 4. 💵 Gestión de Costos e Insumos
- Control de inventario de insumos
- Registro de costos unitarios
- Cálculo automático de costos de producción
- Configuración de márgenes de ganancia
- Precio de venta sugerido

### 5. 🛍️ Marketplace de Recursos
- Compartir y vender plantillas, patrones y moldes
- Recursos gratuitos y de pago
- Sistema de creadores de contenido
- Gestión de compras y descargas

### 6. 🤖 Asistente Virtual
- Sugerencias para mejorar estandarización
- Guías contextuales según el sector
- Recomendaciones personalizadas
- Análisis de formulaciones y costos

### 7. 📈 Gestión de Ventas
- Registro de ventas con múltiples productos
- Historial completo de transacciones
- Análisis de rentabilidad
- Seguimiento de productos más vendidos

### 8. 👥 Gestión de Equipos
- Múltiples usuarios por empresa
- Roles diferenciados (administrador, operador)
- Control de acceso según permisos

## 🛠️ Tecnologías Utilizadas

- **Backend**: Django 5.1.4
- **Base de datos**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript
- **Autenticación**: Django Authentication System
- **Despliegue**: Compatible con Heroku/Railway

## 📦 Instalación y Configuración

### Requisitos Previos

- Python 3.12 o superior
- PostgreSQL (o SQLite para desarrollo)
- pip (gestor de paquetes de Python)
- Virtualenv (recomendado)

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/nimypine.git
cd nimypine
```

2. **Crear y activar entorno virtual**
```bash
python -m venv venv

# En Linux/Mac:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**

Crea un archivo `.env` en la raíz del proyecto:
```env
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/nimypine
```

5. **Ejecutar migraciones**
```bash
python manage.py migrate
```

6. **Crear superusuario**
```bash
python manage.py createsuperuser
```

7. **Iniciar servidor de desarrollo**
```bash
python manage.py runserver
```

8. **Acceder a la aplicación**

Abre tu navegador en: `http://localhost:8000`

## 📖 Guía de Uso

### Para Empresas (MIPYMEs)

#### 1. Registro Inicial
1. Accede a la página principal
2. Selecciona "Registrar MIPYME"
3. Completa la información de tu empresa
4. Selecciona tu sector económico

#### 2. Configuración de Productos
1. Ve al panel de producción
2. Crea tus productos con nombre, descripción y sector
3. Define las características específicas (peso, tamaño, etc.)

#### 3. Gestión de Insumos
1. Accede a "Insumos"
2. Registra cada materia prima o insumo
3. Especifica: nombre, unidad de medida, costo unitario y stock

#### 4. Crear Formulaciones
1. Selecciona un producto
2. Crea un proceso de producción
3. Agrega pasos con sus insumos y cantidades
4. Define porcentajes de desperdicio por paso

#### 5. Usar la Calculadora de Lotes
1. Selecciona un producto con formulación
2. Ingresa la cantidad de lotes deseada
3. Obtén automáticamente:
   - Cantidades exactas de cada insumo
   - Costo total de producción
   - Precio de venta sugerido

#### 6. Registrar Ventas
1. Ve a "Registrar Venta"
2. Selecciona productos y cantidades
3. El sistema calculará automáticamente el total
4. Consulta el historial en cualquier momento

#### 7. Gestionar Equipo
1. Accede a "Gestión de Equipo"
2. Invita usuarios con correo electrónico
3. Asigna roles (administrador u operador)
4. Controla permisos de acceso

### Para Creadores de Contenido

#### 1. Registro como Creador
1. Selecciona "Registrar como Creador"
2. Completa tu perfil profesional
3. Asocia o crea una MIPYME

#### 2. Subir Recursos al Marketplace
1. Accede al Marketplace
2. Selecciona "Subir Plantilla"
3. Completa información:
   - Título y descripción
   - Sector económico
   - Archivo (Excel, PDF, etc.)
   - Precio (o gratis)
4. Publica tu recurso

#### 3. Gestionar Ventas
1. Ve a tu perfil de creador
2. Consulta estadísticas de descargas
3. Revisa ingresos por ventas

### Usando el Asistente Virtual

1. Accede al "Asistente Virtual"
2. Describe tu consulta o problema
3. Recibe sugerencias personalizadas sobre:
   - Optimización de formulaciones
   - Reducción de desperdicios
   - Mejores prácticas del sector
   - Estandarización de procesos

## 📁 Estructura del Proyecto

```
nimypine/
├── asistente/          # Módulo del asistente virtual
├── cuentas/            # Gestión de usuarios y MIPYMEs
├── marketplace/        # Marketplace de recursos
├── produccion/         # Gestión de producción y costos
├── templates/          # Plantillas HTML
├── mipymes_project/    # Configuración principal
├── manage.py           # Script de gestión Django
├── requirements.txt    # Dependencias del proyecto
└── README.md          # Este archivo
```

## 🔐 Seguridad

- Autenticación requerida para todas las operaciones
- Control de acceso basado en roles
- Protección CSRF en formularios
- Validación de datos en backend
- Separación de datos por empresa

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👥 Equipo

Desarrollado como parte del reto "Plataforma de herramientas digitales para procesos productivos" dirigido a MIPYMEs en sectores productivos.

## 📞 Soporte

Para soporte o consultas:
- 📧 Email: soporte@nimypine.com
- 🐛 Issues: [GitHub Issues](https://github.com/tu-usuario/nimypine/issues)

## 🗺️ Roadmap

- [ ] Integración con sistemas de pago
- [ ] App móvil nativa
- [ ] Reportes avanzados con gráficos
- [ ] Integración con APIs de proveedores
- [ ] Sistema de notificaciones en tiempo real
- [ ] Exportación de datos a Excel/PDF

---

**Nimypine** - Empoderando a las MIPYMEs con tecnología 🚀
