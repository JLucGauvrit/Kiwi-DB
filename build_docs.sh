#!/usr/bin/env bash
# Installation et build de la documentation
# Usage: ./build_docs.sh

set -e

echo "=========================================="
echo "🚀 Documentation Sphinx - BDD Fédérée"
echo "=========================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Installer les dépendances
echo -e "${BLUE}1️⃣  Installation des dépendances...${NC}"
pip install -r docs/requirements.txt --quiet
echo -e "${GREEN}✅ Dépendances installées${NC}"
echo ""

# 2. Nettoyer les builds précédents
echo -e "${BLUE}2️⃣  Nettoyage des builds précédents...${NC}"
cd docs
make clean > /dev/null 2>&1 || true
echo -e "${GREEN}✅ Nettoyage effectué${NC}"
echo ""

# 3. Générer la documentation
echo -e "${BLUE}3️⃣  Génération de la documentation...${NC}"
sphinx-build -W --keep-going -b html . _build/html
echo -e "${GREEN}✅ Documentation générée${NC}"
echo ""

# 4. Informations finales
echo "=========================================="
echo -e "${GREEN}✨ Documentation créée avec succès !${NC}"
echo "=========================================="
echo ""
echo "📖 Pour servir localement :"
echo -e "${YELLOW}  cd docs${NC}"
echo -e "${YELLOW}  python -m http.server 8000 -d _build/html${NC}"
echo ""
echo "🌐 Puis ouvrir : http://localhost:8000"
echo ""
echo "📤 Pour publier sur GitHub :"
echo -e "${YELLOW}  git add .${NC}"
echo -e "${YELLOW}  git commit -m 'docs: mise à jour documentation'${NC}"
echo -e "${YELLOW}  git push origin main${NC}"
echo ""
echo "Documentation disponible à :"
echo -e "${BLUE}  https://<username>.github.io/<repo>/${NC}"
echo ""
echo "=========================================="
