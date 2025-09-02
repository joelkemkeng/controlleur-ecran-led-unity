#!/usr/bin/env python3
"""
🚀 ÉTAPE 3 - PIPELINE COMPLET eHub → ArtNet → BC216
Test de validation finale avec Unity
"""

import sys
import time
import signal

# Ajouter le chemin vers l'étape 3
sys.path.append('/home/joel/projet_ecran/controlleur-ecran-led-unity/FINAL-DEV/etape-03-mapping-dmx')

from ehub_complete_pipeline_artnet import EHubArtNetPipeline

def signal_handler(sig, frame):
    """Gestionnaire pour arrêt propre"""
    print("\n🛑 [MAIN] Arrêt demandé par l'utilisateur...")
    sys.exit(0)

def main():
    """
    Lance le pipeline complet eHub → ArtNet
    """
    print("🚀 === PIPELINE COMPLET eHub → ArtNet → BC216 ===")
    print()
    
    # Configuration du gestionnaire de signal
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialiser le pipeline
    print("🔧 [MAIN] Initialisation du pipeline complet...")
    pipeline = EHubArtNetPipeline(port=8776)
    
    if not pipeline.initialize():
        print("❌ [MAIN] Échec de l'initialisation")
        return False
    
    print("✅ [MAIN] Pipeline initialisé avec succès !")
    print()
    
    # Afficher les informations de connexion
    print("📋 === CONFIGURATION UNITY ===")
    print(f"📡 IP WSL détectée automatiquement")
    print(f"🔌 Port cible: {pipeline.port}")
    print("🎮 Contrôleurs BC216 configurés:")
    for ip in pipeline.controllers.keys():
        print(f"   • {ip}")
    print("================================")
    print()
    
    print("👂 [MAIN] En écoute des messages Unity...")
    print("💡 [MAIN] Conseil: Dans Unity, configurer eHuB pour envoyer vers:")
    print(f"   IP: (détectée automatiquement)")
    print(f"   Port: {pipeline.port}")
    print()
    print("🛑 [MAIN] Appuyez sur Ctrl+C pour arrêter")
    print()
    
    try:
        # Lancer le pipeline en mode continu
        pipeline.run_continuous()
        
    except KeyboardInterrupt:
        print("\n🛑 [MAIN] Interruption clavier détectée")
    except Exception as e:
        print(f"\n❌ [MAIN] Erreur inattendue: {e}")
        return False
    finally:
        print("🔌 [MAIN] Arrêt du pipeline...")
        pipeline.stop()
        print("✅ [MAIN] Pipeline arrêté proprement")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
