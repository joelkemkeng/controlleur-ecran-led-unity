#!/bin/bash
# Script de test rapide pour Unity UDP depuis WSL

echo "=== Test de connexion Unity UDP depuis WSL ==="

# Récupère l'IP Windows
WINDOWS_IP=$(ip route show default | grep -oP 'via \K[\d.]+')
PORT=${1:-8765}

echo "IP Windows détectée: $WINDOWS_IP"
echo "Port Unity: $PORT"

# Test rapide de connectivité
if ping -c 1 -W 2 $WINDOWS_IP > /dev/null 2>&1; then
    echo "✓ Ping vers Windows réussi"
else
    echo "✗ Ping vers Windows échoué - vérifiez la connectivité"
    exit 1
fi

echo "Lancement du client UDP..."
echo "Assurez-vous que Unity est lancé et que le serveur UDP est actif sur le port $PORT"
echo ""

# Lance le client UDP
python3 test_client_udp_wsl.py $PORT $WINDOWS_IP
