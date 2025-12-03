#!/bin/sh
set -e

CERT_DIR="/etc/letsencrypt/live/certs"
FULLCHAIN="$CERT_DIR/fullchain.pem"
PRIVKEY="$CERT_DIR/privkey.pem"

echo "➡️  Vérification des certificats SSL..."

if [ ! -f "$FULLCHAIN" ] || [ ! -f "$PRIVKEY" ]; then
  echo "⚠️  Aucun certificat trouvé, génération d'un certificat auto-signé..."
  mkdir -p "$CERT_DIR"

  openssl req -x509 -newkey rsa:4096 -nodes \
    -keyout "$PRIVKEY" \
    -out "$FULLCHAIN" \
    -days 365 \
    -subj "/C=FR/ST=France/L=Local/O=Procom/CN=localhost"

  echo "✅ Certificat auto-signé généré dans $CERT_DIR"
else
  echo "✅ Certificats trouvés, pas de régénération."
fi

echo "🚀 Démarrage de Nginx..."
exec nginx -g "daemon off;"
