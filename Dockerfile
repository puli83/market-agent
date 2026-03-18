# =============================================================================
# Dockerfile — Agent d'analyse de marché e-commerce
# =============================================================================
# Construction:   docker build -t market-agent .
# Lancement:      docker run -p 8000:8000 --env-file .env market-agent
# Ou via compose: docker-compose up --build
# =============================================================================

FROM python:3.13-slim

# Empêche les fichiers .pyc et force les logs en temps réel
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Installer les dépendances d'abord (profite du cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Port exposé par l'API
EXPOSE 8000

# Commande de démarrage
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8010"]
