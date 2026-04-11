#!/bin/bash
# scripts/deploy_azure.sh
# Script de déploiement sur Azure VM (Ubuntu 22.04)
# Usage : bash scripts/deploy_azure.sh

set -e

echo "=================================================="
echo "  StudyBuddy — Déploiement Azure VM"
echo "=================================================="

# ── 1. Mise à jour système ──
echo ""
echo "[1/7] Mise à jour du système..."
sudo apt-get update -qq
sudo apt-get install -y python3-pip python3-venv git curl -qq

# ── 2. Environnement virtuel ──
echo ""
echo "[2/7] Création de l'environnement virtuel Python..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# ── 3. Dépendances ──
echo ""
echo "[3/7] Installation des dépendances Python..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# ── 4. Téléchargement du modèle d'embeddings ──
echo ""
echo "[4/7] Téléchargement du modèle d'embeddings (première fois seulement)..."
python3 -c "
from sentence_transformers import SentenceTransformer
print('Téléchargement...')
SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
print('Modèle téléchargé ✅')
"

# ── 5. Initialisation de la base de données ──
echo ""
echo "[5/7] Initialisation de la base de données..."
python3 -c "
import sys; sys.path.insert(0, '.')
from backend.database import init_db
init_db()
"

# ── 6. Vérification .env ──
echo ""
echo "[6/7] Vérification de la configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️  Fichier .env non trouvé. Création depuis le template..."
    cp .env .env.backup 2>/dev/null || true
fi

if grep -q "VOTRE_CLE_ICI" .env; then
    echo ""
    echo "⚠️  IMPORTANT : Configure ta clé API Anthropic dans le fichier .env"
    echo "   Édite le fichier : nano .env"
    echo "   Change : ANTHROPIC_API_KEY=sk-ant-VOTRE_CLE_ICI"
    echo ""
fi

# ── 7. Ouverture du port firewall (Azure NSG doit aussi être configuré) ──
echo ""
echo "[7/7] Configuration du firewall local..."
sudo ufw allow 8501/tcp 2>/dev/null || true

# ── Instructions finales ──
echo ""
echo "=================================================="
echo "  ✅ Déploiement terminé !"
echo "=================================================="
echo ""
echo "Pour lancer StudyBuddy :"
echo ""
echo "  source venv/bin/activate"
echo "  streamlit run app.py --server.port 8501 --server.address 0.0.0.0"
echo ""
echo "Pour lancer en arrière-plan (production) :"
echo ""
echo "  nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > logs/app.log 2>&1 &"
echo "  echo \$! > studybuddy.pid"
echo ""
echo "Accès depuis le navigateur :"
echo "  http://[IP_PUBLIQUE_AZURE]:8501"
echo ""
echo "N'oublie pas d'ouvrir le port 8501 dans les règles NSG Azure !"
echo "  Azure Portal → VM → Networking → Add inbound port rule → Port 8501"
