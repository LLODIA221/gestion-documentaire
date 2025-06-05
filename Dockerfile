FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY gestion_doc/ ./gestion_doc/

WORKDIR /app/gestion_doc

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 