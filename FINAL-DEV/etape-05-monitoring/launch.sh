#!/bin/bash
"""
🚀 Script de lancement eHub Monitor
Activate venv et lance l'application moderne
"""

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 eHub Monitor - Lancement Application${NC}"
echo -e "${BLUE}==========================================${NC}"

# Aller dans le répertoire de l'application
cd "$(dirname "$0")"

# Vérifier si le venv existe
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Environnement virtuel non trouvé !${NC}"
    echo -e "${YELLOW}💡 Créez-le d'abord avec: python3 -m venv venv${NC}"
    exit 1
fi

# Activer l'environnement virtuel
echo -e "${BLUE}🔧 Activation environnement virtuel...${NC}"
source venv/bin/activate

# Vérifier les dépendances
echo -e "${BLUE}📦 Vérification des dépendances...${NC}"
if ! python -c "import customtkinter" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  CustomTkinter non installé, installation...${NC}"
    pip install -r requirements.txt
fi

# Lancer l'application
echo -e "${GREEN}✅ Lancement de l'application moderne !${NC}"
echo -e "${GREEN}🎨 Interface graphique avec thèmes${NC}"
echo -e "${GREEN}🧭 Navigation sidebar moderne${NC}"
echo ""

python main.py

echo -e "${BLUE}👋 Application fermée${NC}"