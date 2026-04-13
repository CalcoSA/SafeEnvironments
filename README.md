# Formulario de Reporte de Conductas de Acoso Sexual

## Descripción general

Este proyecto corresponde a un sistema web para la recepción, gestión y trazabilidad de reportes relacionados con posibles conductas de acoso sexual en el entorno laboral.

El objetivo principal de la aplicación es proporcionar un canal formal, confidencial y seguro para que las personas puedan reportar situaciones vividas o presenciadas, activando la ruta institucional de atención definida por la organización. La información registrada debe ser tratada con enfoque de protección, debida diligencia, respeto y control de acceso.

El sistema contempla el diligenciamiento del formulario por parte de la persona reportante, el almacenamiento estructurado de la información en base de datos, la gestión de evidencias adjuntas, la generación de soportes en PDF y el envío de notificaciones internas por correo electrónico a las áreas autorizadas.

---

## Objetivo del sistema

Implementar una solución web que permita:

- Registrar reportes de forma estructurada y confidencial.
- Gestionar la información de quien reporta y de la persona señalada.
- Clasificar la conducta reportada, frecuencia, impacto, nivel de riesgo y solicitud de acompañamiento.
- Adjuntar evidencias de forma segura.
- Generar documentos PDF asociados al caso.
- Notificar a las áreas responsables mediante SMTP.
- Operar por ambientes separados de desarrollo, pruebas y producción.
- Aplicar controles de seguridad para proteger información sensible.

---

## Alcance funcional inicial

El sistema contempla las siguientes secciones funcionales:

1. **Información de quien reporta**
2. **Información de la persona señalada**
3. **Tipo de conducta**
4. **Relato de los hechos**
5. **Frecuencia**
6. **Pruebas / evidencias**
7. **Impacto**
8. **Seguridad actual**
9. **Acompañamiento psicológico**
10. **Gestión administrativa del caso**
11. **Generación de PDF**
12. **Notificaciones por correo**
13. **Bitácora y trazabilidad**

---

## Stack tecnológico

### Backend
- Python 3.10+ o superior
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-WTF
- SQLAlchemy
- PyMySQL
- python-dotenv

### Generación de PDF
- WeasyPrint

### Base de datos
- MySQL / MariaDB

### Seguridad
- CSRF con Flask-WTF
- Variables de entorno por ambiente
- Cookies seguras
- Control de sesiones
- Restricción de acceso a panel administrativo
- Almacenamiento privado de evidencias

### Correo
- SMTP corporativo

---

## Dependencias actuales

```txt
bcrypt==5.0.0
blinker==1.9.0
brotli==1.2.0
cffi==2.0.0
click==8.3.1
colorama==0.4.6
cssselect2==0.9.0
dnspython==2.8.0
email-validator==2.3.0
Flask==3.1.3
Flask-Login==0.6.3
Flask-SQLAlchemy==3.1.1
Flask-WTF==1.2.2
fonttools==4.62.1
greenlet==3.3.2
idna==3.11
itsdangerous==2.2.0
Jinja2==3.1.6
MarkupSafe==3.0.3
pillow==12.1.1
pycparser==3.0
pydyf==0.12.1
PyMySQL==1.1.2
pyphen==0.17.2
python-dotenv==1.2.2
SQLAlchemy==2.0.48
tinycss2==1.5.1
tinyhtml5==2.1.0
typing_extensions==4.15.0
weasyprint==68.1
webencodings==0.5.1
Werkzeug==3.1.7
WTForms==3.2.1
zopfli==0.4.1

Estructura sugerida del proyecto

FORMULARIOACOSOSEXUAL/
│
├── .venv/
├── app/
│   ├── controllers/
│   ├── domain/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   ├── static/
│   ├── templates/
│   ├── config.py
│   └── extensions.py
│
├── generated_pdfs/
├── .env
├── .env.example
├── requirements.txt

Descripción de carpetas
app/controllers/: controladores o rutas de la aplicación.
app/domain/: lógica de dominio y reglas del negocio.
app/models/: modelos ORM con SQLAlchemy.
app/repositories/: acceso a datos y consultas a base de datos.
app/services/: servicios auxiliares, como PDF, correo, seguridad o almacenamiento.
app/static/: archivos estáticos públicos.
app/templates/: plantillas HTML.
generated_pdfs/: salida de documentos PDF generados.
.env: configuración sensible del ambiente actual.
requirements.txt: dependencias del proyecto.

Configuración por ambientes

El sistema debe manejar tres ambientes independientes:

development: desarrollo local
testing: pruebas funcionales y QA
production: ambiente productivo

La configuración se centraliza en app/config.py y se complementa con variables de entorno cargadas desde archivos .env.

Variables de entorno requeridas

Ejemplo base en .env.example:

APP_NAME=Formulario de Reporte de Acoso Sexual
APP_ENV=development

SECRET_KEY=CAMBIAR_ESTA_LLAVE
WTF_CSRF_SECRET_KEY=CAMBIAR_ESTA_LLAVE_CSRF

DB_DRIVER=mysql+pymysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=formulario_acoso
DB_USER=root
DB_PASSWORD=secret
DATABASE_URL=

MAIL_HOST=smtp.office365.com
MAIL_PORT=587
MAIL_USERNAME=notificaciones@empresa.com
MAIL_PASSWORD=secret
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_FROM_EMAIL=notificaciones@empresa.com
MAIL_FROM_NAME=Canal Confidencial
CASE_NOTIFICATION_EMAILS=talento.humano@empresa.com,comite@empresa.com

PRIVATE_STORAGE_PATH=./private_storage
EVIDENCE_UPLOAD_DIR=./private_storage/evidencias
PDF_OUTPUT_DIR=./generated_pdfs
MAX_CONTENT_LENGTH=10485760
ALLOWED_FILE_EXTENSIONS=pdf,png,jpg,jpeg,doc,docx

SESSION_COOKIE_SECURE=false
REMEMBER_COOKIE_SECURE=false
SESSION_COOKIE_SAMESITE=Lax
SESSION_LIFETIME_MINUTES=30
WTF_CSRF_TIME_LIMIT=3600
AUDIT_LOG_ENABLED=true
LOG_LEVEL=INFO

Configuración principal (config.py)

El archivo config.py debe centralizar:

nombre de la aplicación
ambiente de ejecución
llaves secretas
conexión a base de datos
parámetros de SMTP
rutas de almacenamiento privado
tamaño máximo de archivos
extensiones permitidas
seguridad de cookies y sesiones
parámetros de trazabilidad y logging

También debe definir clases por ambiente, por ejemplo:

DevelopmentConfig
TestingConfig
ProductionConfig

Esto permite cambiar el comportamiento del sistema sin modificar el código fuente.

Inicialización de extensiones (extensions.py)

El archivo extensions.py debe contener la inicialización de las extensiones de Flask utilizadas por la aplicación, por ejemplo:

SQLAlchemy para persistencia
LoginManager para autenticación administrativa
CSRFProtect para protección de formularios

Este archivo no debe contener lógica de negocio, consultas SQL ni reglas funcionales del sistema.

Consideraciones de seguridad

Este proyecto maneja datos sensibles, por lo cual deben aplicarse controles mínimos desde la primera versión:

No almacenar secretos dentro del código.
Cargar configuración solo desde variables de entorno.
Habilitar protección CSRF en formularios.
Guardar evidencias fuera de static/.
Renombrar archivos cargados usando UUID.
Validar extensión, tamaño y tipo de archivo.
No exponer rutas internas de almacenamiento.
Activar SESSION_COOKIE_SECURE en producción.
Utilizar HttpOnly en cookies de sesión.
Separar bases de datos por ambiente.
Restringir acceso al módulo administrativo.
Mantener bitácora de accesos y cambios.
No exponer identificadores internos directamente en la interfaz pública.
Flujo general esperado
La persona diligencia el formulario.
El sistema valida la información.
Se registra el caso en base de datos.
Se almacenan las evidencias en una ruta privada.
Se asocian las conductas e impactos seleccionados.
Se genera el soporte en PDF, si aplica.
Se notifica por correo a las áreas autorizadas.
El equipo administrativo gestiona el caso desde el panel interno.
Todas las acciones relevantes quedan trazadas.
Instalación en desarrollo
1. Crear entorno virtual
python -m venv .venv
2. Activar entorno virtual

En Windows:

.venv\Scripts\activate

En Linux/Mac:

source .venv/bin/activate
3. Instalar dependencias
pip install -r requirements.txt
4. Configurar variables de entorno

Crear archivo .env basado en .env.example y ajustar:

conexión a base de datos
credenciales SMTP
rutas locales
llaves secretas
5. Crear base de datos

Crear la base de datos correspondiente al ambiente local, por ejemplo:

CREATE DATABASE formulario_acoso_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
6. Ejecutar la aplicación

Según la estructura de arranque del proyecto:

flask run

o mediante un archivo principal tipo run.py / app.py, según se defina en la implementación.

Recomendaciones para pruebas

En ambiente de pruebas se recomienda:

base de datos independiente
cuentas de correo exclusivas de QA
rutas de archivos separadas
datos ficticios, no reales
validación de notificaciones y generación de PDF
pruebas de carga de evidencias
verificación de permisos de acceso
Recomendaciones para producción

En producción se recomienda:

usar HTTPS obligatorio
proteger archivos .env
activar cookies seguras
restringir permisos del sistema de archivos
almacenar evidencias fuera del directorio público del servidor web
realizar backups cifrados
definir política de retención de datos
limitar acceso administrativo por roles
registrar auditoría de acciones
monitorear errores y accesos
Estado inicial del proyecto

Este repositorio corresponde a la fase inicial de construcción del sistema. En esta etapa se define principalmente:

estructura del proyecto
configuración base
manejo de ambientes
seguridad de configuración
modelo de datos normalizado
lineamientos para persistencia, evidencias y notificaciones

Las siguientes fases incluirán la implementación de modelos, controladores, servicios, formularios, panel administrativo y procesos de generación documental.

Autor / equipo responsable

Proyecto orientado a la gestión confidencial de reportes internos de conductas de acoso sexual, bajo lineamientos de protección de datos, seguridad de la información y trazabilidad institucional.


También te dejo una versión corta del nombre del proyecto, por si la quieres usar como título del repo:

```md
# formulario-acoso-sexual

Y una descripción breve para GitHub:

Sistema web en Flask para la recepción, gestión y trazabilidad confidencial de reportes de conductas de acoso sexual, con soporte para evidencias, PDF, SMTP y manejo por ambientes.

Puedo dejarte ahora el README más técnico, incluyendo instalación, estructura real de archivos y comandos exactos de ejecución para tu proyecto Flask.