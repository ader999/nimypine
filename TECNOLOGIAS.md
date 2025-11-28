# Definición de Tecnologías Seleccionadas - NIMYPINE

Este documento define las tecnologías seleccionadas para el proyecto NIMYPINE y proporciona una breve justificación de su elección, abarcando lenguajes de programación, frameworks, gestor de base de datos y sistema operativo.

## Justificación de la Elección Tecnológica

La selección de tecnologías para NIMYPINE se basó en los siguientes principios:

- **Escalabilidad y Rendimiento:** Utilizar herramientas probadas que puedan crecer con la plataforma y manejar una carga de trabajo creciente.
- **Ecosistema y Comunidad:** Optar por tecnologías con un ecosistema maduro, amplio soporte comunitario y abundancia de librerías.
- **Productividad del Desarrollador:** Elegir frameworks y lenguajes que permitan un desarrollo rápido, eficiente y mantenible.
- **Multiplataforma:** Ofrecer soluciones tanto web como de escritorio/móvil desde una base de código coherente.

---

## Aplicación Web Principal

La plataforma central de NIMYPINE está construida con un stack tecnológico robusto y escalable.

### Arquitectura y Justificación
- **Sistema Operativo (Desarrollo):** Pop!_OS (basado en Linux). Se eligió por su estabilidad, herramientas orientadas a desarrolladores y su compatibilidad nativa con Docker, lo que facilita la creación de entornos de desarrollo consistentes con la producción.
- **Lenguaje (Backend):** Python 3.10+. Seleccionado por su sintaxis clara, su vasto ecosistema de librerías (especialmente en ciencia de datos e IA) y su enfoque en la productividad.
- **Framework (Backend):** Django 4.2+. Ofrece una arquitectura "baterías incluidas" que acelera el desarrollo con componentes robustos para ORM, autenticación, administración y seguridad.
- **Gestor de Base de Datos:** PostgreSQL. Es un sistema de gestión de bases de datos objeto-relacional potente, de código abierto y altamente escalable, ideal para aplicaciones complejas que requieren integridad de datos.
- **API:** Django REST Framework. Es la herramienta estándar de la industria para construir APIs RESTful en Django, proporcionando flexibilidad y herramientas de serialización potentes.
- **Frontend:** HTML5, CSS3 (Bootstrap 5), y JavaScript (ES6+). Un stack clásico y ligero que garantiza la máxima compatibilidad y un buen rendimiento sin la complejidad de frameworks pesados de JavaScript, adecuado para una aplicación orientada a la gestión.

### Librerías Clave del Backend
- **`djangorestframework`**: Para construir la API RESTful.
- **`django-minio-storage`** y **`minio`**: Para la integración con el servidor de almacenamiento de objetos MinIO, gestionando archivos como logos y avatares.
- **`google-generativeai`** y **`openai`**: Para la conexión con servicios de inteligencia artificial generativa, potenciando funcionalidades avanzadas dentro de la aplicación.
- **`psycopg2-binary`**: Adaptador de PostgreSQL para Python.
- **`gunicorn`**: Servidor WSGI para producción.
- **`argon2-cffi`**: Para el hashing seguro de contraseñas.

### Infraestructura y Despliegue
- **Contenerización:** Docker y Docker Compose para crear entornos de desarrollo y producción consistentes.
- **Plataforma de Despliegue:** Adaptable a cualquier proveedor de nube (AWS, Google Cloud, Azure) o servidor privado que soporte contenedores Docker.
- **Almacenamiento de Archivos:** MinIO para un almacenamiento de objetos compatible con S3.

---

## Aplicaciones de Escritorio y Móvil (Flet)

Para ofrecer una experiencia nativa en múltiples plataformas, se ha desarrollado una aplicación de escritorio y móvil utilizando el framework Flet.

### Tecnologías y Justificación
- **Framework:** Flet (basado en Flutter). Elegido por permitir el desarrollo de aplicaciones multiplataforma (Windows, macOS, Linux, Android, iOS, Web) utilizando Python, lo que mantiene la consistencia del lenguaje en todo el proyecto y acelera el desarrollo.
- **Lenguaje:** Python. Permite reutilizar la lógica de negocio y el conocimiento del equipo de desarrollo del backend.
- **Comunicación con el Backend:** API RESTful a través de la librería `requests`.

### Arquitectura de la Aplicación Flet
La aplicación sigue una arquitectura limpia, separando la lógica de negocio de la interfaz de usuario:

- **Cliente API (`api_client.py`):** Un cliente centralizado para gestionar todas las comunicaciones con la API de NIMYPINE.
- **Modelos de Datos (`models/`):** Clases que representan las entidades de la API para un manejo de datos consistente.
- **Servicios (`services/`):** Centralizan la lógica para interactuar con los endpoints de la API.
- **Interfaz de Usuario (`ui/`):** Componentes de Flet organizados en pantallas para construir la interfaz gráfica.
- **Utilidades (`utils/`):** Módulos de configuración y helpers.

Esta estructura permite una alta cohesión y bajo acoplamiento, facilitando el mantenimiento y la escalabilidad de la aplicación cliente.
