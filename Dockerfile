# Utiliser une image de base Python
FROM python:3.9-slim

# Définir le répertoire de travail dans le container
WORKDIR /app

# Copier les fichiers nécessaires dans le container
COPY . /app

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer un port si nécessaire (par exemple, pour une API ou un service web)
# EXPOSE 8080

# Commande pour exécuter le script
CMD ["python", "toorna.py"]