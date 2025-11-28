# Seguridad y Usabilidad en Nimypine

La seguridad y la usabilidad son pilares fundamentales en el desarrollo de Nimypine. A continuación, se detallan las medidas implementadas para garantizar un entorno seguro y fácil de usar para nuestros usuarios.

## Medidas Mínimas de Seguridad

### 1. Validación de Entradas (Input Validation)

La validación de entradas es nuestra primera línea de defensa contra datos maliciosos o incorrectos. Nos aseguramos de que toda la información enviada por el usuario a través de formularios cumpla con los formatos y restricciones esperados antes de ser procesada por el servidor.

**Herramientas Utilizadas:**

*   **Formularios de Django (`django.forms`):** Es la herramienta principal para la validación de datos. Cada formulario en la aplicación define explícitamente los campos esperados, sus tipos de datos (ej. `CharField`, `EmailField`, `IntegerField`), longitudes máximas y mínimas, y si son requeridos. Django se encarga de validar automáticamente los datos recibidos contra estas reglas. Si un dato no es válido, el formulario no se procesa y se devuelve un error claro al usuario.

**Medidas Implementadas:**

*   **Validación de Tipos de Datos:** Se asegura que un campo numérico reciba solo números, un campo de correo electrónico tenga un formato válido, etc.
*   **Restricciones de Longitud:** Campos como nombres de usuario o contraseñas tienen límites de longitud para prevenir ataques de desbordamiento de búfer.
*   **Validadores Personalizados:** Para reglas de negocio específicas (ej. un nombre de producto no puede existir previamente para la misma MiPyme), se han creado validadores personalizados que se ejecutan junto con las validaciones estándar.
*   **Validación en el Lado del Cliente:** Aunque la validación principal es en el backend, se utilizan atributos HTML5 (`required`, `minlength`, `type="email"`) para proporcionar retroalimentación instantánea al usuario, mejorando la usabilidad.

### 2. Sanitización de Entradas (Input Sanitization)

La sanitización es el proceso de limpiar los datos de entrada para eliminar o neutralizar caracteres o código potencialmente dañino (como scripts de JavaScript o sentencias SQL).

**Herramientas Utilizadas:**

*   **Motor de Plantillas de Django:** Por defecto, el motor de plantillas de Django escapa automáticamente todas las variables que se renderizan en las plantillas HTML. Esto convierte caracteres como `<`, `>`, `&` en sus equivalentes de entidad HTML (`&lt;`, `&gt;`, `&amp;`), neutralizando eficazmente los ataques de Cross-Site Scripting (XSS).
*   **ORM de Django (Object-Relational Mapper):** Al interactuar con la base de datos, utilizamos exclusivamente el ORM de Django. Este sistema utiliza consultas parametrizadas, lo que significa que los valores de entrada de los usuarios nunca se insertan directamente en las sentencias SQL. En su lugar, se tratan como parámetros, eliminando por completo el riesgo de ataques de inyección SQL.

**Medidas Implementadas:**

*   **Prevención de XSS:** Gracias al auto-escaping de Django, cualquier intento de inyectar un script en un campo de un formulario (por ejemplo, en la descripción de un producto) resultará en que el script se muestre como texto plano en la página, en lugar de ejecutarse.
*   **Prevención de Inyección SQL:** Todas las consultas a la base de datos se realizan a través de métodos del ORM como `.filter()`, `.get()` y `.create()`. El ORM se encarga de construir las consultas SQL de forma segura, garantizando que los datos del usuario no puedan alterar la lógica de la consulta.

En resumen, el uso riguroso de los formularios, el ORM y el motor de plantillas de Django nos permite implementar una estrategia de seguridad robusta basada en la validación y sanitización de todas las entradas del usuario.