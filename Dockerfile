# Utiliser une image Python légère
FROM python:3.11-slim

# Définir le dossier de travail
WORKDIR /app

# 1. Installer FFmpeg (CRUCIAL pour l'assemblage vidéo)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# 2. Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copier tout le code du projet
COPY . .

# 4. Créer les dossiers nécessaires s'ils n'existent pas
RUN mkdir -p static/outputs

# 5. Exposer le port 5000
EXPOSE 5000

# 6. Lancer l'application
# Note: Assure-toi que ton app.py écoute sur 0.0.0.0 pour Docker
CMD ["python", "app.py"]