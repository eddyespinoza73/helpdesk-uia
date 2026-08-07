# Fijado a bookworm (Debian 12) a proposito: python:3.11-slim paso a
# apuntar a Debian 13 (trixie), que rechaza las firmas SHA1 con las que
# packages.microsoft.com firma su repo. El .deb que se instala mas abajo
# es especificamente el de debian/12, asi que la imagen tiene que quedar
# fija en bookworm hasta que Microsoft actualice sus firmas.
FROM python:3.11-slim-bookworm

# Dependencias de sistema necesarias para agregar el repo de Microsoft
# e instalar el driver ODBC.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    apt-transport-https \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Repo oficial de Microsoft para Debian 12 + driver ODBC 18 para SQL Server
# (doc oficial: https://learn.microsoft.com/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server)
RUN curl -sSL -O https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && rm packages-microsoft-prod.deb \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar solo requirements primero: si el codigo cambia pero las
# dependencias no, Docker reusa esta capa en el proximo build.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD gunicorn run:app --bind 0.0.0.0:$PORT
