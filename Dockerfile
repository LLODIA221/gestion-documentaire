FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances système si nécessaire
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le contenu de gestion_doc dans /app
COPY gestion_doc/ ./

# Créer les dossiers pour les fichiers statiques et media
RUN mkdir -p /app/staticfiles /app/media

EXPOSE 8000

# Le manage.py est maintenant directement dans /app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]