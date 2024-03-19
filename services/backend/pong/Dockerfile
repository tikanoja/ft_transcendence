# Building Python based applications is EXTREMELY slow on Alpine...
# Using latest stable slim python debian. Remove slim if need more tools. Build from plain bookworm/slim if required...
FROM python:3.12.2-slim-bookworm

#RUN apt-get update && apt-get install -y \
#	sqlite3 \
#    libsqlite3-dev
#	libpq-dev \
#	openssl

WORKDIR /

#RUN /usr/bin/sqlite3 /db/app.db
#RUN chmod +rwx /
#RUN touch data.db
#RUN chmod +rwx data.db
#COPY create_tables.sql .
##RUN chmod +rwx create_tables.sql
#RUN sqlite3 data.db < create_tables.sql
#RUN cat data.db > output.txt

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python3", "-u", "-m", "flask", "run", "--host=0.0.0.0", "--port=8080"]


#CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]
