FROM python:3.10-slim

# Installation des dépendances système (simule un environnement Linux pro)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copie des fichiers
COPY . .

# Installation des dépendances Python
RUN pip3 install -r requirements.txt

# Port Streamlit
EXPOSE 8501

# Vérification de santé (Healthcheck)
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Lancement de l'application
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
