#!/bin/bash
# Script pour libérer le port 8765 si nécessaire

echo "=== Nettoyage du port 8765 ==="

# Recherche des processus utilisant le port 8765
PROCESSES=$(lsof -t -i :8765 2>/dev/null)

if [ -z "$PROCESSES" ]; then
    echo "✓ Port 8765 libre"
else
    echo "Processus trouvés utilisant le port 8765:"
    lsof -i :8765
    echo ""
    echo "Arrêt des processus..."
    
    for PID in $PROCESSES; do
        echo "Arrêt du processus $PID"
        kill $PID 2>/dev/null
        sleep 1
        
        # Vérification si le processus est toujours actif
        if kill -0 $PID 2>/dev/null; then
            echo "Arrêt forcé du processus $PID"
            kill -9 $PID 2>/dev/null
        fi
    done
    
    echo "✓ Port 8765 libéré"
fi

echo ""
echo "Vous pouvez maintenant lancer receive_ehub.py"
