# Help Desk UIA

**App en producción:** https://helpdesk-uia.onrender.com — probar con `ana.ramirez@empresa.cr` / `Demo123!` (ver más credenciales en [Credenciales de prueba](#credenciales-de-prueba)).

Sistema de mesa de ayuda (login, gestión de tickets y reportes) desarrollado con Flask y SQL Server. Incluye autenticación con bcrypt y procedimiento almacenado, control de acceso por rol, cambio de estado de tickets con historial transaccional, y 2 reportes (por estado/prioridad y cumplimiento de SLA).

## Funcionalidades

- Login validado (campos vacíos, credenciales incorrectas, bloqueo por 3 intentos fallidos, cuenta inactiva)
- Gestión completa de tickets (crear, listar, ver detalle)
- Cambio de estado de tickets con historial transaccional (auditoría automática)
- Asignación y reasignación de técnicos con registro en historial
- 2 reportes: tickets por estado/prioridad y cumplimiento de SLA por técnico
- Control de acceso por rol (Administrador, Técnico, Usuario)
- Retry automático de conexión para Azure SQL serverless
- Manejo de errores con páginas 404 y 500 personalizadas

## Stack

- **Backend:** Python 3 + Flask
- **Base de datos:** SQL Server (probado en SQL Server 2022 y Azure SQL Database)
- **Conector:** pyodbc (SQL crudo, sin ORM)
- **Autenticación:** bcrypt + procedimiento almacenado `sp_procesar_login` (maneja intentos fallidos y bloqueo de cuenta)
- **Frontend:** HTML + Jinja + CSS propio

## Requisitos previos

- Python 3.11+
- SQL Server con la base de datos `helpdesk_uia` ya creada (11 tablas) y el procedimiento `sp_procesar_login` instalado
- ODBC Driver 17 **o** 18 para SQL Server instalado en la máquina (cualquiera de los dos sirve en local — Render usa 18 porque es el que instala el `Dockerfile`, ver sección Deploy)
- Un usuario de SQL Server con acceso a `helpdesk_uia` (`db_datareader`, `db_datawriter`, `EXECUTE` sobre `sp_procesar_login`)

## Instalación

1. Clonar el repositorio y entrar a la carpeta del proyecto:
   ```
   git clone https://github.com/eddyespinoza73/helpdesk-uia.git
   cd helpdesk-uia
   ```
2. Crear y activar un entorno virtual:
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Linux/Mac
   ```
3. Instalar las dependencias:
   ```
   pip install -r requirements.txt
   ```
4. Crear el archivo `.env` a partir de `.env.example` y completar los valores reales:
   ```
   DB_SERVER=localhost\SQL2022
   DB_NAME=helpdesk_uia
   DB_USER=app_helpdesk
   DB_PASSWORD=tu_password
   DB_DRIVER={ODBC Driver 17 for SQL Server}
   SECRET_KEY=una_clave_larga_y_aleatoria
   FLASK_DEBUG=False
   ```
   `DB_DRIVER` acepta `{ODBC Driver 17 for SQL Server}` o `{ODBC Driver 18 for SQL Server}` — usá el que tengas instalado local. En Render (Docker) esta variable siempre va con **18**, porque es el único que el `Dockerfile` instala en la imagen.
5. (Opcional, solo la primera vez) Fijar las contraseñas de los usuarios de prueba con hash bcrypt real:
   ```
   python seed_passwords.py
   ```

## Correr el proyecto localmente

```
python run.py
```

La app queda disponible en **http://127.0.0.1:5000**.

### Credenciales de prueba

- Correo: `ana.ramirez@empresa.cr`
- Contraseña: `Demo123!`

(Los otros 5 usuarios de prueba usan la misma contraseña; ver `seed_passwords.py` para la lista completa y sus roles.)

## Estructura del proyecto

```
run.py                    Punto de entrada (python run.py)
seed_passwords.py         Fija hashes bcrypt de los usuarios demo
requirements.txt
Dockerfile                Imagen para deploy en Render (instala msodbcsql18 + gunicorn)
Procfile                  Sin uso mientras el deploy sea con Docker (queda de referencia)
app/
  config.py               Configuracion cargada desde .env
  db.py                   Conexion a SQL Server via pyodbc
  routes/                 auth.py, tickets.py (CRUD + cambio de estado y asignación de técnico), reportes.py
  models/                 Consultas SQL: usuario.py, ticket.py, reporte.py
  utils/decoradores.py    login_requerido
  templates/               Vistas Jinja (login, dashboard, tickets, reportes, errores)
  static/css/              estilo.css
```

## Deploy

Pensado para Render (deploy con **Docker**) + Azure SQL como base de datos en la nube. Antes de desplegar, actualizar las variables de entorno en el servicio de hosting con los datos de la instancia de Azure SQL y **no** commitear nunca el archivo `.env`.

### Deploy en Render (Docker)

El runtime nativo de Python en Render tiene el filesystem en solo lectura y no permite `apt-get install`, así que no se puede instalar ahí el driver ODBC de Microsoft (`msodbcsql18`) que pyodbc necesita para hablar con SQL Server. Por eso el deploy usa el `Dockerfile` del repo, que instala el driver dentro de la imagen antes de correr la app.

Con Docker, Render **detecta el `Dockerfile` automáticamente** — no hace falta configurar Build Command ni Start Command a mano (esos campos ni siquiera aparecen; el build corre `docker build` sobre el `Dockerfile` y el arranque es el `CMD` que ya está definido ahí). El viejo `render-build.sh` (para el runtime nativo) ya no se usa y se borró del repo.

Pasos manuales en [render.com](https://render.com):

1. **New + → Web Service** y conectar el repo `eddyespinoza73/helpdesk-uia`.
2. Render va a detectar el `Dockerfile` solo y va a mostrar **Runtime: Docker**. No tocar Build/Start Command — quedan fijados por el `Dockerfile`.
3. Elegir **Plan: Free**.
4. En la sección **Environment**, agregar estas variables (mismas llaves que `.env.example`):

   | Variable       | Valor |
   |----------------|-------|
   | `SECRET_KEY`   | una clave larga y aleatoria (no reutilizar la de local) |
   | `DB_SERVER`    | endpoint de Azure SQL, ej. `helpdesk-uia.database.windows.net` |
   | `DB_NAME`      | `helpdesk_uia` |
   | `DB_USER`      | usuario de BD (ej. `app_helpdesk`) |
   | `DB_PASSWORD`  | password de ese usuario |
   | `DB_DRIVER`    | `{ODBC Driver 18 for SQL Server}` (el `Dockerfile` instala la versión 18, que es la que hay que declarar acá) |
   | `FLASK_DEBUG`  | `False` |

   `PORT` la define Render solo (no hace falta agregarla) — el contenedor escucha en `0.0.0.0:$PORT` según el `CMD` del `Dockerfile`.
5. **Create Web Service**. Render construye la imagen (instala `msodbcsql18` + `pip install -r requirements.txt`) y arranca con `gunicorn run:app --bind 0.0.0.0:$PORT`.
6. Verificar en la pestaña **Logs** que el build de Docker termine bien y que gunicorn levante sin errores de conexión a la BD.

**Nota:** si `DB_SERVER` apunta a una instancia de Azure SQL Database serverless (no siempre activa), el primer request después de un período de inactividad puede tardar unos segundos en responder mientras la base "despierta" — es esperado.

## Nota de curso

Proyecto final del curso **Implementación y Mantenimiento de Software** — Universidad Internacional de las Américas (UIA).
