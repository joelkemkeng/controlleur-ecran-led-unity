#!/usr/bin/env python3
"""
🎬 Script de lancement rapide - Étape 4
Lance le pipeline complet avec paramètres par défaut
"""

import sys
from pathlib import Path

# Ajouter le chemin du module
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from ehub_complete_pipeline_send_artnet import EHubArtNetPipeline, LedMode

def main():
    """Lance le pipeline complet rapidement"""
    print("🚀 === LANCEMENT RAPIDE ÉTAPE 4 ===")
    print("🎭 Pipeline complet eHuB → BC216")
    print()
    
    # Configuration rapide
    led_mode = LedMode.PRODUCTION
    listen_port = 8765
    
    # Créer et lancer le pipeline
    pipeline = EHubArtNetPipeline(led_mode, listen_port)
    
    try:
        if pipeline.initialize():
            print("✅ Pipeline initialisé - En attente Unity...")
            pipeline.start_listening(8765)
        else:
            print("❌ Échec initialisation")
            return 1
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé")
    finally:
        pipeline.close()
    
    return 0

if __name__ == "__main__":
    exit(main())
