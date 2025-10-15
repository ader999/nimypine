# Guía de Integración de Flet con APIs de NIMYPINE

Esta guía proporciona instrucciones completas para crear una aplicación Flet que se conecte a las APIs REST del proyecto NIMYPINE, un sistema de gestión para MIPYMES.

## Requisitos Previos

### 1. Entorno de Desarrollo
- Python 3.8 o superior
- Conocimientos básicos de Python y APIs REST
- El servidor Django de NIMYPINE ejecutándose (por defecto en `http://127.0.0.1:8000`)

### 2. Dependencias
Instala las siguientes librerías:

```bash
pip install flet requests
```

## Configuración del Proyecto

### 1. Estructura del Proyecto
Crea la siguiente estructura de directorios:

```
flet_nimypine_app/
├── main.py
├── api_client.py
├── ui/
│   ├── login_screen.py
│   ├── register_screen.py
│   ├── products_screen.py
│   └── __init__.py
├── models/
│   ├── user.py
│   ├── product.py
│   └── __init__.py
└── utils/
    ├── config.py
    └── __init__.py
```

### 2. Configuración Base
Crea `utils/config.py`:

```python
class Config:
    BASE_URL = "http://127.0.0.1:8000"  # Cambia esto para producción
    API_PREFIX = "/api"

    @classmethod
    def get_api_url(cls, endpoint):
        return f"{cls.BASE_URL}{cls.API_PREFIX}{endpoint}"
```

## Cliente API

### 1. Cliente Base
Crea `api_client.py`:

```python
import requests
from utils.config import Config

class APIClient:
    def __init__(self):
        self.session = requests.Session()
        self.token = None

    def set_token(self, token):
        self.token = token
        self.session.headers.update({
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json'
        })

    def clear_token(self):
        self.token = None
        self.session.headers.pop('Authorization', None)

    def _make_request(self, method, endpoint, data=None, **kwargs):
        url = Config.get_api_url(endpoint)
        try:
            if data:
                kwargs['json'] = data
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return None

    def post(self, endpoint, data=None, **kwargs):
        return self._make_request('POST', endpoint, data, **kwargs)

    def get(self, endpoint, **kwargs):
        return self._make_request('GET', endpoint, **kwargs)

# Instancia global del cliente
api_client = APIClient()
```

## Modelos de Datos

### 1. Modelo de Usuario
Crea `models/user.py`:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    mipyme: Optional[dict]
    es_admin_mipyme: bool
    es_creador_contenido: bool
    rol: str
    avatar: Optional[str]
    email_confirmado: bool
    is_active: bool
    date_joined: str

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            username=data.get('username'),
            email=data.get('email'),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            mipyme=data.get('mipyme'),
            es_admin_mipyme=data.get('es_admin_mipyme', False),
            es_creador_contenido=data.get('es_creador_contenido', False),
            rol=data.get('rol'),
            avatar=data.get('avatar'),
            email_confirmado=data.get('email_confirmado', False),
            is_active=data.get('is_active', True),
            date_joined=data.get('date_joined')
        )
```

### 2. Modelo de Producto
Crea `models/product.py`:

```python
from dataclasses import dataclass
from typing import List, Optional
from decimal import Decimal

@dataclass
class Product:
    id: int
    nombre: str
    descripcion: str
    mipyme: int
    mipyme_name: str
    precio_venta: Decimal
    porcentaje_ganancia: Decimal
    stock_actual: int
    peso: Optional[Decimal]
    tamano_largo: Optional[Decimal]
    tamano_ancho: Optional[Decimal]
    tamano_alto: Optional[Decimal]
    presentacion: str
    costo_de_produccion: Decimal
    procesos: List[dict]
    impuestos: List[dict]

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            nombre=data.get('nombre'),
            descripcion=data.get('descripcion', ''),
            mipyme=data.get('mipyme'),
            mipyme_name=data.get('mipyme_name'),
            precio_venta=Decimal(str(data.get('precio_venta', 0))),
            porcentaje_ganancia=Decimal(str(data.get('porcentaje_ganancia', 0))),
            stock_actual=data.get('stock_actual', 0),
            peso=Decimal(str(data.get('peso'))) if data.get('peso') else None,
            tamano_largo=Decimal(str(data.get('tamano_largo'))) if data.get('tamano_largo') else None,
            tamano_ancho=Decimal(str(data.get('tamano_ancho'))) if data.get('tamano_ancho') else None,
            tamano_alto=Decimal(str(data.get('tamano_alto'))) if data.get('tamano_alto') else None,
            presentacion=data.get('presentacion', ''),
            costo_de_produccion=Decimal(str(data.get('costo_de_produccion', 0))),
            procesos=data.get('procesos', []),
            impuestos=data.get('impuestos', [])
        )
```

## Servicios API

### 1. Servicio de Autenticación
Crea `services/auth_service.py`:

```python
from api_client import api_client
from models.user import User

class AuthService:
    @staticmethod
    def register(username, email, first_name, last_name, password, password2, rol='LECTURA', avatar=None):
        data = {
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'password': password,
            'password2': password2,
            'rol': rol
        }
        if avatar:
            data['avatar'] = avatar

        response = api_client.post('/cuentas/register/', data)
        return response

    @staticmethod
    def login(username_or_email, password):
        data = {
            'username': username_or_email,
            'password': password
        }
        response = api_client.post('/cuentas/login/', data)
        if response and 'token' in response:
            api_client.set_token(response['token'])
            user = User.from_dict(response['user'])
            return user, response['token']
        return None, None

    @staticmethod
    def logout():
        response = api_client.post('/cuentas/logout/')
        if response:
            api_client.clear_token()
            return True
        return False
```

### 2. Servicio de Productos
Crea `services/product_service.py`:

```python
from api_client import api_client
from models.product import Product

class ProductService:
    @staticmethod
    def get_products():
        response = api_client.get('/produccion/productos/')
        if response:
            return [Product.from_dict(item) for item in response]
        return []
```

## Interfaz de Usuario con Flet

### 1. Pantalla de Login
Crea `ui/login_screen.py`:

```python
import flet as ft
from services.auth_service import AuthService

class LoginScreen:
    def __init__(self, page, on_login_success):
        self.page = page
        self.on_login_success = on_login_success
        self.username_field = ft.TextField(label="Usuario o Email", width=300)
        self.password_field = ft.TextField(label="Contraseña", password=True, width=300)
        self.error_text = ft.Text()

    def build(self):
        return ft.Container(
            content=ft.Column([
                ft.Text("Iniciar Sesión", size=24, weight=ft.FontWeight.BOLD),
                self.username_field,
                self.password_field,
                self.error_text,
                ft.ElevatedButton(
                    "Iniciar Sesión",
                    on_click=self._handle_login
                ),
                ft.TextButton(
                    "Crear cuenta nueva",
                    on_click=lambda e: self.page.go("/register")
                )
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center
        )

    def _handle_login(self, e):
        username = self.username_field.value
        password = self.password_field.value

        if not username or not password:
            self.error_text.value = "Por favor complete todos los campos"
            self.page.update()
            return

        user, token = AuthService.login(username, password)
        if user:
            self.on_login_success(user)
        else:
            self.error_text.value = "Credenciales inválidas o email no confirmado"
            self.page.update()
```

### 2. Pantalla de Registro
Crea `ui/register_screen.py`:

```python
import flet as ft
from services.auth_service import AuthService

class RegisterScreen:
    def __init__(self, page):
        self.page = page
        self.username_field = ft.TextField(label="Usuario", width=300)
        self.email_field = ft.TextField(label="Email", width=300)
        self.first_name_field = ft.TextField(label="Nombre", width=300)
        self.last_name_field = ft.TextField(label="Apellido", width=300)
        self.password_field = ft.TextField(label="Contraseña", password=True, width=300)
        self.password2_field = ft.TextField(label="Confirmar Contraseña", password=True, width=300)
        self.error_text = ft.Text()
        self.success_text = ft.Text()

    def build(self):
        return ft.Container(
            content=ft.Column([
                ft.Text("Crear Cuenta", size=24, weight=ft.FontWeight.BOLD),
                self.username_field,
                self.email_field,
                self.first_name_field,
                self.last_name_field,
                self.password_field,
                self.password2_field,
                self.error_text,
                self.success_text,
                ft.ElevatedButton(
                    "Crear Cuenta",
                    on_click=self._handle_register
                ),
                ft.TextButton(
                    "Ya tengo cuenta",
                    on_click=lambda e: self.page.go("/login")
                )
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center
        )

    def _handle_register(self, e):
        data = {
            'username': self.username_field.value,
            'email': self.email_field.value,
            'first_name': self.first_name_field.value,
            'last_name': self.last_name_field.value,
            'password': self.password_field.value,
            'password2': self.password2_field.value
        }

        if not all(data.values()):
            self.error_text.value = "Por favor complete todos los campos"
            self.page.update()
            return

        if data['password'] != data['password2']:
            self.error_text.value = "Las contraseñas no coinciden"
            self.page.update()
            return

        response = AuthService.register(**data)
        if response and 'message' in response:
            self.success_text.value = "Cuenta creada exitosamente. Revisa tu email para confirmar."
            self.error_text.value = ""
            # Limpiar campos
            for field in [self.username_field, self.email_field, self.first_name_field,
                         self.last_name_field, self.password_field, self.password2_field]:
                field.value = ""
        else:
            self.error_text.value = "Error al crear la cuenta"
            self.success_text.value = ""

        self.page.update()
```

### 3. Pantalla de Productos
Crea `ui/products_screen.py`:

```python
import flet as ft
from services.product_service import ProductService

class ProductsScreen:
    def __init__(self, page, user):
        self.page = page
        self.user = user
        self.products = []
        self.products_list = ft.Column(scroll=ft.ScrollMode.AUTO)

    def build(self):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(f"Bienvenido, {self.user.first_name}!", size=20),
                    ft.ElevatedButton("Cerrar Sesión", on_click=self._handle_logout)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text("Mis Productos", size=24, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton("Actualizar", on_click=self._load_products),
                self.products_list
            ]),
            padding=20
        )

    def _load_products(self, e=None):
        self.products = ProductService.get_products()
        self._render_products()
        self.page.update()

    def _render_products(self):
        self.products_list.controls.clear()
        if not self.products:
            self.products_list.controls.append(
                ft.Text("No hay productos disponibles", italic=True)
            )
        else:
            for product in self.products:
                self.products_list.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text(product.nombre, size=18, weight=ft.FontWeight.BOLD),
                                ft.Text(f"Precio: ${product.precio_venta}", size=16),
                                ft.Text(f"Stock: {product.stock_actual}", size=14),
                                ft.Text(product.descripcion, size=12, color=ft.colors.GREY)
                            ]),
                            padding=10
                        )
                    )
                )

    def _handle_logout(self, e):
        from services.auth_service import AuthService
        if AuthService.logout():
            self.page.go("/login")
```

## Aplicación Principal

### 1. Archivo Principal
Crea `main.py`:

```python
import flet as ft
from ui.login_screen import LoginScreen
from ui.register_screen import RegisterScreen
from ui.products_screen import ProductsScreen

def main(page: ft.Page):
    page.title = "NIMYPINE - Gestión MIPYMES"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 800
    page.window_height = 600

    current_user = None

    def route_change(e):
        nonlocal current_user
        page.views.clear()

        if page.route == "/login" or page.route == "/":
            login_screen = LoginScreen(page, on_login_success)
            page.views.append(
                ft.View(
                    "/login",
                    [login_screen.build()]
                )
            )
        elif page.route == "/register":
            register_screen = RegisterScreen(page)
            page.views.append(
                ft.View(
                    "/register",
                    [register_screen.build()]
                )
            )
        elif page.route == "/products" and current_user:
            products_screen = ProductsScreen(page, current_user)
            page.views.append(
                ft.View(
                    "/products",
                    [products_screen.build()]
                )
            )
            # Cargar productos automáticamente
            products_screen._load_products()
        else:
            page.go("/login")

        page.update()

    def on_login_success(user):
        nonlocal current_user
        current_user = user
        page.go("/products")

    page.on_route_change = route_change
    page.go("/login")

if __name__ == "__main__":
    ft.app(target=main)
```

## Ejecutar la Aplicación

1. Asegúrate de que el servidor Django esté ejecutándose:
```bash
cd /ruta/al/proyecto/nimypine
python manage.py runserver
```

2. Ejecuta la aplicación Flet:
```bash
python main.py
```

## Mejores Prácticas

### 1. Manejo de Errores
- Siempre verifica las respuestas de la API
- Muestra mensajes de error amigables al usuario
- Implementa manejo de excepciones para conexiones fallidas

### 2. Seguridad
- Nunca almacenes tokens en texto plano
- Usa HTTPS en producción
- Implementa timeout en las solicitudes HTTP

### 3. Experiencia de Usuario
- Muestra indicadores de carga durante las operaciones
- Implementa validación de formularios del lado cliente
- Usa navegación consistente

### 4. Arquitectura
- Separa la lógica de negocio de la UI
- Usa modelos de datos para mantener consistencia
- Implementa servicios para centralizar las llamadas a la API

## Solución de Problemas

### Problema: "Las credenciales de autenticación no se proveyeron"
- Asegúrate de que el token esté configurado correctamente en el cliente API
- Verifica que el usuario esté autenticado antes de hacer llamadas protegidas

### Problema: "Email not confirmed"
- El usuario debe confirmar su email antes de poder iniciar sesión
- Implementa funcionalidad para reenviar email de confirmación

### Problema: Lista de productos vacía
- Verifica que el usuario tenga una MIPYME asociada
- Asegúrate de que existan productos en la base de datos

Esta guía proporciona una base sólida para integrar Flet con las APIs de NIMYPINE. Puedes extenderla agregando más funcionalidades como crear/editar productos, gestión de MIPYMES, etc.