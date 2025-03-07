FROM python:3.13.1-slim

RUN apt-get update && \
    apt-get install -y \
    wget \
    gnupg && \
    echo "deb [signed-by=/usr/share/keyrings/postgresql.gpg] http://apt.postgresql.org/pub/repos/apt/ bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    wget -qO- https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /usr/share/keyrings/postgresql.gpg && \
    apt-get update && \
    apt-get install -y postgresql-client-17 && \
    apt-get purge -y wget gnupg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /src

COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY ./app .

CMD [ "fastapi", "run", "main.py" ]
