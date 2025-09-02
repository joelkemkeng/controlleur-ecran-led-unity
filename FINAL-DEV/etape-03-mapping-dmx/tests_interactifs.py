#!/usr/bin/env python3
"""
🧪 TESTS INTERACTIFS - ÉTAPE 3
Script pour tester le pipeline avec des données simulées
"""

import sys
import time
import threading
import socket
import struct
import gzip

# Ajouter le chemin vers l'étape 3
sys.path.append('/home/joel/projet_ecran/controlleur-ecran-led-unity/FINAL-DEV/etape-03-mapping-dmx')

from ehub_complete_pipeline_artnet import EHubArtNetPipeline

def create_test_ehub_message(entities_data):
    """
    Créer un message eHuB test avec les données fournies
    Format: [(entity_id, r, g, b), ...]
    """
    # Créer les données d'entités (6 bytes par entité)
    entity_bytes = bytearray()
    for entity_id, r, g, b in entities_data:
        entity_bytes.extend(struct.pack('<H', entity_id))  # Entity ID (2 bytes, little-endian)
        entity_bytes.extend(bytes([r, g, b, 0]))           # RGBW (4 bytes)
    
    # Compresser avec gzip
    compressed = gzip.compress(entity_bytes)
    
    # Créer le header eHuB (10 bytes)
    header = bytearray()
    header.extend(b'eHuB')                                  # Signature (4 bytes)
    header.append(2)                                        # Packet type: update (1 byte)
    header.append(1)                                        # Universe (1 byte)
    header.extend(struct.pack('<H', len(entities_data)))    # Entity count (2 bytes, little-endian)
    header.extend(struct.pack('<H', len(compressed)))       # Payload size (2 bytes, little-endian)
    
    # Assembler le message complet
    return bytes(header + compressed)

def send_test_message(port, entities_data, delay=0.1):
    """
    Envoyer un message eHuB test
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        message = create_test_ehub_message(entities_data)
        
        print(f"📤 [TEST] Envoi message test: {len(entities_data)} entités")
        for entity_id, r, g, b in entities_data:
            print(f"   🔸 Entité {entity_id}: R={r} G={g} B={b}")
        
        sock.sendto(message, ('127.0.0.1', port))
        sock.close()
        
        time.sleep(delay)
        return True
        
    except Exception as e:
        print(f"❌ [TEST] Erreur envoi: {e}")
        return False

def test_scenario_1(port):
    """
    Scénario 1: Test simple avec quelques entités
    """
    print("🧪 === SCÉNARIO 1: Test simple ===")
    
    entities = [
        (100, 255, 0, 0),     # Rouge
        (101, 0, 255, 0),     # Vert  
        (102, 0, 0, 255),     # Bleu
    ]
    
    return send_test_message(port, entities)

def test_scenario_2(port):
    """
    Scénario 2: Test multi-contrôleurs
    """
    print("🧪 === SCÉNARIO 2: Test multi-contrôleurs ===")
    
    entities = [
        (100, 255, 0, 0),     # Contrôleur 1
        (4000, 0, 255, 0),    # Contrôleur 2  
        (8000, 0, 0, 255),    # Contrôleur 3
        (12000, 255, 255, 0), # Contrôleur 4
    ]
    
    return send_test_message(port, entities)

def test_scenario_3(port):
    """
    Scénario 3: Test animation rainbow
    """
    print("🧪 === SCÉNARIO 3: Test animation rainbow ===")
    
    colors = [
        (255, 0, 0),    # Rouge
        (255, 127, 0),  # Orange
        (255, 255, 0),  # Jaune
        (0, 255, 0),    # Vert
        (0, 0, 255),    # Bleu
        (75, 0, 130),   # Indigo
        (148, 0, 211),  # Violet
    ]
    
    base_entities = [100, 200, 300, 400, 500, 600, 700]
    
    for i, (r, g, b) in enumerate(colors):
        entities = [(base_entities[j], r if j == i else 0, 
                    g if j == i else 0, b if j == i else 0) 
                   for j in range(len(base_entities))]
        
        print(f"   🌈 Frame {i+1}: {['Rouge', 'Orange', 'Jaune', 'Vert', 'Bleu', 'Indigo', 'Violet'][i]}")
        send_test_message(port, entities, delay=0.5)

def run_interactive_tests():
    """
    Lance les tests interactifs
    """
    print("🧪 === TESTS INTERACTIFS ÉTAPE 3 ===")
    print()
    
    # Initialiser le pipeline
    print("🔧 [TEST] Initialisation du pipeline...")
    pipeline = EHubArtNetPipeline(port=8776)
    
    if not pipeline.initialize():
        print("❌ [TEST] Échec de l'initialisation")
        return False
    
    print("✅ [TEST] Pipeline initialisé !")
    print()
    
    # Démarrer le pipeline en arrière-plan
    print("🚀 [TEST] Démarrage du pipeline...")
    
    def run_pipeline():
        try:
            pipeline.run_continuous()
        except:
            pass
    
    pipeline_thread = threading.Thread(target=run_pipeline)
    pipeline_thread.daemon = True
    pipeline_thread.start()
    
    time.sleep(1)  # Laisser le temps au pipeline de démarrer
    
    # Menu interactif
    while True:
        print("\n🎮 === MENU TESTS ===")
        print("1. Scénario 1: Test simple (3 entités)")
        print("2. Scénario 2: Test multi-contrôleurs (4 entités)")
        print("3. Scénario 3: Animation rainbow (7 frames)")
        print("4. Test personnalisé")
        print("5. Afficher statistiques")
        print("q. Quitter")
        print()
        
        choice = input("📋 Votre choix: ").strip()
        
        if choice == '1':
            test_scenario_1(8776)
        elif choice == '2':
            test_scenario_2(8776)
        elif choice == '3':
            test_scenario_3(8776)
        elif choice == '4':
            print("🔧 Test personnalisé:")
            try:
                entity_id = int(input("   Entity ID: "))
                r = int(input("   Rouge (0-255): "))
                g = int(input("   Vert (0-255): "))
                b = int(input("   Bleu (0-255): "))
                
                entities = [(entity_id, r, g, b)]
                send_test_message(8776, entities)
                
            except ValueError:
                print("❌ Valeurs invalides")
        elif choice == '5':
            print("📊 === STATISTIQUES PIPELINE ===")
            print(f"📡 Messages reçus: {pipeline.receiver.message_count}")
            print(f"🔬 Paquets décodés: {pipeline.packets_decoded}")
            print(f"🎮 Contrôleurs actifs: {len(pipeline.controllers)}")
            for ip, state in pipeline.controllers.items():
                print(f"   • {ip}: {state.packets_sent} paquets ArtNet envoyés")
        elif choice.lower() == 'q':
            break
        else:
            print("❌ Choix invalide")
    
    # Arrêter le pipeline
    print("\n🔌 [TEST] Arrêt du pipeline...")
    pipeline.stop()
    print("✅ [TEST] Tests terminés !")
    
    return True

if __name__ == "__main__":
    success = run_interactive_tests()
    exit(0 if success else 1)
