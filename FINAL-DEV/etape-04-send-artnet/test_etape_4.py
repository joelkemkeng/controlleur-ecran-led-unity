#!/usr/bin/env python3
"""
🧪 Test Étape 4 - Pipeline complet avec envoi ArtNet
Test rapide du pipeline eHuB → DMX → ArtNet → BC216
"""

import sys
import time
import socket
import threading
from pathlib import Path

# Ajouter le chemin du module
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from ehub_complete_pipeline_send_artnet import EHubArtNetPipeline, LedMode

def create_test_ehub_packet():
    """Crée un paquet eHuB de test avec quelques entités colorées"""
    import struct
    import gzip
    
    # Header eHuB (10 bytes)
    header = bytearray(10)
    header[0:4] = b'eHuB'  # Magic
    header[4] = 1          # Version
    header[5] = 0          # Flags
    
    # Créer quelques entités de test
    entities_data = bytearray()
    
    # Entité 1: Rouge à la position (10, 10)
    entities_data.extend(struct.pack('<HHH', 10*128+10, 255, 0))  # ID, R, G
    entities_data.extend(struct.pack('<H', 0))                     # B
    
    # Entité 2: Vert à la position (20, 20) 
    entities_data.extend(struct.pack('<HHH', 20*128+20, 0, 255))  # ID, R, G
    entities_data.extend(struct.pack('<H', 0))                     # B
    
    # Entité 3: Bleu à la position (30, 30)
    entities_data.extend(struct.pack('<HHH', 30*128+30, 0, 0))    # ID, R, G
    entities_data.extend(struct.pack('<H', 255))                   # B
    
    # Entité 4: Blanc à la position (50, 50)
    entities_data.extend(struct.pack('<HHH', 50*128+50, 255, 255)) # ID, R, G
    entities_data.extend(struct.pack('<H', 255))                   # B
    
    # Compresser les entités
    compressed_entities = gzip.compress(entities_data)
    
    # Taille compressée dans le header
    compressed_size = len(compressed_entities)
    header[6:10] = struct.pack('<I', compressed_size)
    
    # Assembler le paquet complet
    packet = header + compressed_entities
    return bytes(packet)

def test_pipeline_with_fake_data():
    """Test le pipeline avec des données simulées"""
    print("🧪 === TEST PIPELINE ÉTAPE 4 ===")
    print("📡 Test avec données eHuB simulées")
    print()
    
    # Créer le pipeline en mode production
    pipeline = EHubArtNetPipeline(LedMode.PRODUCTION, 8765)
    
    try:
        # Initialiser
        if not pipeline.initialize():
            print("❌ Échec initialisation")
            return False
        
        print("✅ Pipeline initialisé")
        
        # Créer un paquet de test
        test_packet = create_test_ehub_packet()
        print(f"📦 Paquet de test créé: {len(test_packet)} bytes")
        
        # Traiter le paquet plusieurs fois pour tester
        print("🔄 Test de traitement...")
        
        for i in range(5):
            success = pipeline.process_ehub_packet(test_packet)
            if success:
                print(f"   ✅ Test {i+1}/5: Paquet traité et envoyé vers BC216")
            else:
                print(f"   ❌ Test {i+1}/5: Échec traitement")
            
            time.sleep(0.5)  # Pause entre les envois
        
        # Afficher les stats
        stats = pipeline.artnet_sender.get_stats()
        print(f"\n📊 Statistiques finales:")
        print(f"   📤 Paquets ArtNet envoyés: {stats['packets_sent']}")
        print(f"   🎬 Frames envoyées: {stats['frames_sent']}")
        print(f"   ❌ Erreurs: {stats['errors']}")
        
        return stats['packets_sent'] > 0
        
    except Exception as e:
        print(f"❌ Erreur durant le test: {e}")
        return False
    finally:
        pipeline.close()

def test_direct_artnet_send():
    """Test d'envoi ArtNet direct (comme dans test_simple_artnet.py)"""
    print("\n🎯 === TEST ENVOI ARTNET DIRECT ===")
    print("📤 Test d'envoi direct vers BC216 (validation)")
    
    try:
        # Socket UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Contrôleurs BC216
        controllers = [
            ('192.168.1.45', 6454),
            ('192.168.1.46', 6454),
            ('192.168.1.47', 6454),
            ('192.168.1.48', 6454),
        ]
        
        # Couleur de test: rouge faible
        r, g, b = 50, 0, 0
        
        print(f"🎨 Envoi couleur test RGB({r},{g},{b}) pendant 2s...")
        
        packets_sent = 0
        start_time = time.time()
        
        while time.time() - start_time < 2.0:
            # Envoyer vers tous les contrôleurs
            for ctrl_idx, (ip, port) in enumerate(controllers):
                base_universe = ctrl_idx * 32
                
                # Quelques univers par contrôleur pour test
                for universe_offset in range(8):  # Seulement 8 univers pour test rapide
                    universe = base_universe + universe_offset
                    
                    # Header ArtNet
                    packet = bytearray([
                        ord('A'), ord('r'), ord('t'), ord('-'),
                        ord('N'), ord('e'), ord('t'), 0,  # "Art-Net\0"
                        0x00, 0x50,  # OpCode
                        0, 14,       # Version
                        0, 0,        # Sequence, Physical
                        universe & 0xFF, (universe >> 8) & 0xFF,  # Universe
                        0x02, 0x00,  # Length (512)
                    ])
                    
                    # Données DMX (512 bytes)
                    dmx_data = bytearray(512)
                    
                    # Remplir avec la couleur test (170 LEDs × 3 canaux = 510 canaux)
                    for led in range(170):
                        if led * 3 + 2 < 512:
                            dmx_data[led * 3] = r      # R
                            dmx_data[led * 3 + 1] = g  # G
                            dmx_data[led * 3 + 2] = b  # B
                    
                    packet.extend(dmx_data)
                    
                    # Envoyer
                    try:
                        sock.sendto(packet, (ip, port))
                        packets_sent += 1
                    except Exception as e:
                        print(f"❌ Erreur {ip}: {e}")
            
            time.sleep(0.1)  # 10 FPS pour test
        
        sock.close()
        print(f"✅ Test direct terminé: {packets_sent} paquets envoyés")
        return packets_sent > 0
        
    except Exception as e:
        print(f"❌ Erreur test direct: {e}")
        return False

def main():
    """Lance les tests de l'Étape 4"""
    print("🚀 === TESTS ÉTAPE 4: ENVOI ARTNET ===")
    print("🎭 Validation du pipeline complet")
    print()
    
    success_count = 0
    total_tests = 2
    
    # Test 1: Pipeline avec données simulées
    if test_pipeline_with_fake_data():
        print("✅ Test 1: Pipeline complet - RÉUSSI")
        success_count += 1
    else:
        print("❌ Test 1: Pipeline complet - ÉCHOUÉ")
    
    # Test 2: Envoi ArtNet direct
    if test_direct_artnet_send():
        print("✅ Test 2: Envoi ArtNet direct - RÉUSSI")
        success_count += 1
    else:
        print("❌ Test 2: Envoi ArtNet direct - ÉCHOUÉ")
    
    # Résumé
    print(f"\n📊 RÉSULTATS: {success_count}/{total_tests} tests réussis")
    
    if success_count == total_tests:
        print("🎉 Tous les tests sont passés!")
        print("🚀 L'Étape 4 est fonctionnelle!")
        return 0
    else:
        print("⚠️ Certains tests ont échoué")
        return 1

if __name__ == "__main__":
    exit(main())
