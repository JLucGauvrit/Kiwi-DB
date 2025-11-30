# Dockerfile pour Nginx
FROM nginx:alpine

# Copier la configuration Nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Créer les répertoires pour les certificats et les logs
RUN mkdir -p /etc/letsencrypt/live/certs && \
    mkdir -p /var/log/nginx

# Exposer les ports HTTP et HTTPS
EXPOSE 80 443

# Utiliser la configuration par défaut de nginx
CMD ["nginx", "-g", "daemon off;"]
