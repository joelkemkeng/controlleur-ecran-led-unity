#!/usr/bin/env python3
"""
🧪 Test synchronisé Pipeline + Simulateur Unity
Lance le pipeline et envoie des données test
"""

import subprocess
import time
import signal
import sys
import os

def test_pipeline_mapping():
    """
    Test du pipeline mapping DMX avec envoi automatique de données
    """
    print("🎭 === TEST PIPELINE MAPPING DMX ===")
    print()
    
    # Démarrer le pipeline en arrière-plan
    print("🚀 Démarrage du pipeline mapping DMX...")
    pipeline_process = subprocess.Popen(
        ['python3', 'ehub_complete_pipeline_mapping_dmx.py'],
        cwd='/home/joel/projet_ecran/controlleur-ecran-led-unity/FINAL-DEV/etape-03-mapping-dmx',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Attendre que le pipeline s'initialise
    print("⏳ Attente initialisation pipeline (10s)...")
    time.sleep(10)
    
    try:
        # Vérifier que le pipeline fonctionne
        if pipeline_process.poll() is None:
            print("✅ Pipeline démarré, envoi de données test...")
            
            # Envoyer des données test
            result = subprocess.run(
                ['python3', 'test_unity_simulator.py'],
                cwd='/home/joel/projet_ecran/controlleur-ecran-led-unity/FINAL-DEV/etape-03-mapping-dmx',
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Données test envoyées avec succès")
                print(result.stdout)
            else:
                print("❌ Erreur envoi données test")
                print(result.stderr)
            
            # Attendre un peu pour voir les résultats
            print("⏳ Attente traitement (5s)...")
            time.sleep(5)
            
        else:
            print("❌ Le pipeline s'est arrêté prématurément")
            stdout, stderr = pipeline_process.communicate()
            print("STDOUT:", stdout)
            print("STDERR:", stderr)
    
    finally:
        # Arrêter le pipeline proprement
        print("🔌 Arrêt du pipeline...")
        if pipeline_process.poll() is None:
            pipeline_process.send_signal(signal.SIGINT)
            try:
                pipeline_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pipeline_process.terminate()
                pipeline_process.wait()
        
        print("✅ Test terminé")

if __name__ == "__main__":
    test_pipeline_mapping()
