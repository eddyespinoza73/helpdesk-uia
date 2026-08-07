# Help Desk UIA

Sistema de mesa de ayuda (login, gestión de tickets y reportes) desarrollado con Flask y SQL Server. Incluye autenticación con bcrypt y procedimiento almacenado, control de acceso por rol, cambio de estado de tickets con historial transaccional, y 2 reportes (por estado/prioridad y cumplimiento de SLA).

## Stack

- **Backend:** Python 3 + Flask
- **Base de datos:** SQL Server (probado en SQL Server 2022 y Azure SQL Database)
- **Conector:** pyodbc (SQL crudo, sin ORM)
- **Autenticación:** bcrypt + procedimiento almacenado `sp_procesar_login` (maneja intentos fallidos y bloqueo de cuenta)
- **Frontend:** HTML + Jinja + CSS propio

## Requisitos previos

- Python 3.11+
- SQL Server con la base de datos `helpdesk_uia` ya creada (11 tablas) y el procedimiento `sp_procesar_login` instalado
- ODBC Driver 17 (o compatible) para SQL Server instalado en la máquina
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
Procfile                  Deploy en Render (gunicorn)
app/
  config.py               Configuracion cargada desde .env
  db.py                   Conexion a SQL Server via pyodbc
  routes/                 auth.py, tickets.py, reportes.py
  models/                 Consultas SQL: usuario.py, ticket.py, reporte.py
  utils/decoradores.py    login_requerido
  templates/               Vistas Jinja (login, dashboard, tickets, reportes, errores)
  static/css/              estilo.css
```

## Deploy

Pensado para Render (`Procfile` con `gunicorn`) + Azure SQL como base de datos en la nube. Antes de desplegar, actualizar las variables de entorno en el servicio de hosting con los datos de la instancia de Azure SQL y **no** commitear nunca el archivo `.env`.

## Nota de curso

Proyecto final del curso **Implementación y Mantenimiento de Software** — Universidad Interamericana de Costa Rica (UIA).
