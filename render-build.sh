#!/usr/bin/env bash
# Build script para Render (plan free, entorno nativo sobre Ubuntu 22.04).
# Render no trae preinstalado el driver ODBC de Microsoft para SQL Server,
# asi que hay que instalarlo antes de "pip install pyodbc" o la conexion
# a la BD va a fallar en runtime.
set -o errexit

# La version del driver se decide segun DB_DRIVER (la misma variable de
# entorno que usa la app para conectarse, configurada en el dashboard de
# Render). Si no se puede determinar, se usa la 18 por defecto porque es
# la mejor soportada en Ubuntu 22.
if [[ "$DB_DRIVER" == *"17"* ]]; then
    ODBC_VERSION="17"
else
    ODBC_VERSION="18"
fi

echo "==> Instalando msodbcsql${ODBC_VERSION} (Ubuntu 22.04)..."

curl -sSL https://packages.microsoft.com/keys/microsoft.asc | tee /etc/apt/trusted.gpg.d/microsoft.asc > /dev/null
curl -sSL https://packages.microsoft.com/config/ubuntu/22.04/prod.list | tee /etc/apt/sources.list.d/mssql-release.list > /dev/null

apt-get update
ACCEPT_EULA=Y apt-get install -y --no-install-recommends "msodbcsql${ODBC_VERSION}" unixodbc-dev

echo "==> Instalando dependencias de Python..."
pip install -r requirements.txt

echo "==> Build completo (driver msodbcsql${ODBC_VERSION})."
