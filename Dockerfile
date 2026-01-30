# Utiliser Python 3.11 léger
FROM python:3.11-slim

# Installer FFmpeg (Indispensable pour assembler la vidéo)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Dossier de travail dans le conteneur
WORKDIR /app

# Copier les besoins et installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout ton code
COPY . .

# Ouvrir le port 5000
EXPOSE 5000

# Lancer l'app
CMD ["python", "app.py"]