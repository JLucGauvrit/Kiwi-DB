# Dockerfile pour Nginx
FROM nginx:1-alpine-slim 

# Openssl pour générer le certificat
RUN apk add --no-cache openssl

# Répertoires nécessaires
RUN mkdir -p /etc/letsencrypt/live/certs \
    && mkdir -p /var/log/nginx

# Copier la conf Nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Copier le script d'entrypoint custom
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80 443

CMD ["/entrypoint.sh"]
