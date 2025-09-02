#!/usr/bin/env python3
"""
🧪 TEST ÉTAPE 3 : Pipeline Complet eHub → ArtNet
Test de l'intégration complète: Réception + Décodage + ArtNet + BC216
"""

import sys
import os
import time
import threading
import socket
import struct
import gzip

# Ajouter les chemins
sys.path.append('/home/joel/projet_ecran/controlleur-ecran-led-unity/FINAL-DEV/etape-03-mapping-dmx')

from ehub_complete_pipeline_artnet import EHubArtNetPipeline, ArtNetSender, ArtNetPacket

def create_test_ehub_message() -> bytes:
    """
    Crée un message eHub de test pour validation ArtNet
    """
    # Entités de test ciblant différents contrôleurs
    test_entities = [
        (100, 255, 0, 0, 0),      # Rouge → 192.168.1.45
        (101, 0, 255, 0, 0),      # Vert → 192.168.1.45
        (4000, 0, 0, 255, 0),     # Bleu → 192.168.1.45
        (8000, 255, 255, 0, 0),   # Jaune → 192.168.1.46
        (12000, 255, 0, 255, 0),  # Magenta → 192.168.1.47
        (16000, 0, 255, 255, 0),  # Cyan → 192.168.1.48
    ]
    
    # Créer données entités (format 6 bytes par entité)
    entities_data = b''
    for entity_id, r, g, b, w in test_entities:
        entity_bytes = struct.pack('<H', entity_id) + bytes([r, g, b, w])
        entities_data += entity_bytes
    
    # Compresser
    compressed_data = gzip.compress(entities_data)
    
    # Header eHub
    header = b'eHuB'                                # Signature (4)
    header += bytes([2])                            # Type UPDATE (1)
    header += bytes([1])                            # Universe (1)
    header += struct.pack('<H', len(test_entities)) # Entity count (2)
    header += struct.pack('<H', len(compressed_data)) # Payload size (2)
    
    return header + compressed_data

def test_pipeline_initialization():
    """
    Test 1: Initialisation pipeline complet
    """
    print("🔧 Test 1: Initialisation pipeline complet...")
    
    pipeline = EHubArtNetPipeline(port=8776)
    
    success = pipeline.initialize()
    
    if success:
        print("✅ Pipeline initialisé")
        print(f"   📡 Récepteur UDP: OK")
        print(f"   🗺️  Config écran: {len(pipeline.screen_config.mappings)} mappings")
        print(f"   🎭 ArtNet sender: OK")
        print(f"   🎮 Contrôleurs: {len(pipeline.controllers)}")
        
        # Vérifier contrôleurs attendus
        expected_ips = ['192.168.1.45', '192.168.1.46', '192.168.1.47', '192.168.1.48']
        found_ips = list(pipeline.controllers.keys())
        
        if all(ip in found_ips for ip in expected_ips):
            print("   ✅ Tous les contrôleurs BC216 détectés")
            pipeline.stop()
            return True
        else:
            print(f"   ⚠️ Contrôleurs manquants: {set(expected_ips) - set(found_ips)}")
            pipeline.stop()
            return False
    else:
        print("❌ Échec initialisation pipeline")
        return False

def test_artnet_packet_generation():
    """
    Test 2: Génération paquets ArtNet
    """
    print("🎭 Test 2: Génération paquets ArtNet...")
    
    sender = ArtNetSender()
    
    if not sender.initialize():
        print("❌ Impossible d'initialiser ArtNet sender")
        return False
    
    # Test création paquet ArtNet
    test_dmx = bytearray(512)
    test_dmx[0] = 255  # Canal 1 = Rouge
    test_dmx[1] = 128  # Canal 2 = Vert
    test_dmx[2] = 64   # Canal 3 = Bleu
    
    artnet_packet = sender.create_artnet_packet(universe=5, dmx_data=bytes(test_dmx))
    
    # Vérifications format ArtNet
    if len(artnet_packet) == 530:  # 18 + 512
        print("✅ Taille paquet ArtNet correcte (530 bytes)")
        
        # Vérifier header
        if artnet_packet[0:8] == b"Art-Net\0":
            print("✅ Signature ArtNet correcte")
            
            # Vérifier OpCode DMX
            opcode = struct.unpack('<H', artnet_packet[8:10])[0]
            if opcode == 0x5000:
                print("✅ OpCode DMX correct (0x5000)")
                
                # Vérifier univers
                universe = struct.unpack('<H', artnet_packet[14:16])[0]
                if universe == 5:
                    print("✅ Univers correct (5)")
                    
                    # Vérifier données DMX
                    dmx_data = artnet_packet[18:18+512]
                    if dmx_data[0] == 255 and dmx_data[1] == 128 and dmx_data[2] == 64:
                        print("✅ Données DMX correctes")
                        sender.close()
                        return True
    
    print("❌ Format paquet ArtNet invalide")
    sender.close()
    return False

def test_ehub_to_artnet_integration():
    """
    Test 3: Intégration eHub → ArtNet
    """
    print("🔄 Test 3: Intégration eHub → ArtNet...")
    
    pipeline = EHubArtNetPipeline(port=8777)
    
    if not pipeline.initialize():
        print("❌ Impossible d'initialiser pipeline")
        return False
    
    # Capturer les paquets ArtNet envoyés (mock)
    sent_packets = []
    original_send = pipeline.artnet_sender.send_to_controller
    
    def mock_send(controller_ip, universe, dmx_data):
        sent_packets.append((controller_ip, universe, dmx_data))
        return True
    
    pipeline.artnet_sender.send_to_controller = mock_send
    
    # Thread pour envoyer message eHub test
    def sender_worker():
        time.sleep(1)
        
        test_message = create_test_ehub_message()
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sender.sendto(test_message, ("127.0.0.1", 8777))
        sender.close()
        
        print(f"📤 Message eHub test envoyé ({len(test_message)} bytes)")
    
    # Démarrer envoi
    sender_thread = threading.Thread(target=sender_worker)
    sender_thread.start()
    
    # Attendre et traiter
    start_time = time.time()
    packet_processed = False
    
    while time.time() - start_time < 5:
        message = pipeline.receiver.receive_message(timeout=1.0)
        
        if message:
            packet = pipeline.decode_ehub_packet(message)
            if packet:
                pipeline.process_packet(packet)
                packet_processed = True
                break
    
    pipeline.stop()
    sender_thread.join()
    
    if packet_processed and sent_packets:
        print(f"✅ Paquet eHub traité et {len(sent_packets)} paquets ArtNet générés")
        
        # Vérifier que différents contrôleurs sont ciblés
        unique_controllers = set(packet[0] for packet in sent_packets)
        print(f"   🎮 Contrôleurs ciblés: {len(unique_controllers)}")
        
        # Vérifier quelques mappings
        for controller_ip, universe, dmx_data in sent_packets[:3]:
            print(f"   📡 {controller_ip}:u{universe} → {len(dmx_data)} bytes DMX")
        
        if len(unique_controllers) >= 2:  # Au moins 2 contrôleurs différents
            print("✅ Mapping multi-contrôleurs fonctionnel")
            return True
        else:
            print("⚠️ Pas assez de contrôleurs différents ciblés")
            return False
    else:
        print("❌ Aucun paquet ArtNet généré")
        return False

def test_performance_basic():
    """
    Test 4: Performance basique
    """
    print("⚡ Test 4: Performance basique...")
    
    pipeline = EHubArtNetPipeline(port=8778)
    
    if not pipeline.initialize():
        print("❌ Impossible d'initialiser pipeline")
        return False
    
    # Simuler traitement de plusieurs paquets
    start_time = time.time()
    packets_to_process = 10
    
    # Mock ArtNet pour éviter réseau
    sent_count = 0
    def mock_send(controller_ip, universe, dmx_data):
        nonlocal sent_count
        sent_count += 1
        return True
    
    pipeline.artnet_sender.send_to_controller = mock_send
    
    # Envoyer plusieurs paquets
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    for i in range(packets_to_process):
        test_message = create_test_ehub_message()
        sender.sendto(test_message, ("127.0.0.1", 8778))
        
        # Traiter immédiatement
        message = pipeline.receiver.receive_message(timeout=0.1)
        if message:
            packet = pipeline.decode_ehub_packet(message)
            if packet:
                pipeline.process_packet(packet)
    
    sender.close()
    
    # Calculer performance
    elapsed = time.time() - start_time
    packets_per_second = packets_to_process / elapsed if elapsed > 0 else 0
    
    pipeline.stop()
    
    print(f"✅ Performance: {packets_per_second:.1f} paquets/seconde")
    print(f"   📊 {packets_to_process} paquets en {elapsed:.3f}s")
    print(f"   🎭 {sent_count} paquets ArtNet générés")
    
    if packets_per_second >= 20:  # Minimum acceptable
        print("✅ Performance acceptable (>20 paquets/s)")
        return True
    else:
        print("⚠️ Performance insuffisante (<20 paquets/s)")
        return False

def test_error_handling():
    """
    Test 5: Gestion d'erreurs
    """
    print("⚠️ Test 5: Gestion d'erreurs...")
    
    pipeline = EHubArtNetPipeline(port=8779)
    
    if not pipeline.initialize():
        print("❌ Impossible d'initialiser pipeline")
        return False
    
    # Test avec entités non mappées
    from ehub_complete_pipeline_decoder import EHubEntity, EHubPacket
    
    fake_packet = EHubPacket(
        signature="eHuB",
        packet_type=2,
        entity_count=2,
        universe=1,
        entities=[
            EHubEntity(999999, 255, 0, 0, 0),  # Entité inexistante
            EHubEntity(100, 0, 255, 0, 0),     # Entité valide
        ]
    )
    
    # Compter les paquets ArtNet générés
    sent_count = 0
    def mock_send(controller_ip, universe, dmx_data):
        nonlocal sent_count
        sent_count += 1
        return True
    
    pipeline.artnet_sender.send_to_controller = mock_send
    
    # Traiter paquet avec entités invalides
    pipeline.process_packet(fake_packet)
    
    pipeline.stop()
    
    if sent_count > 0:
        print("✅ Entités valides traitées malgré entités invalides")
        print(f"   📊 {sent_count} paquets ArtNet générés")
        return True
    else:
        print("❌ Aucun paquet généré")
        return False

def test_etape_3():
    """
    Test complet de l'étape 3
    """
    print("🧪 === TEST ÉTAPE 3 : PIPELINE COMPLET eHub → ArtNet ===")
    print()
    
    tests = [
        ("Initialisation pipeline", test_pipeline_initialization),
        ("Génération ArtNet", test_artnet_packet_generation),
        ("Intégration eHub→ArtNet", test_ehub_to_artnet_integration),
        ("Performance basique", test_performance_basic),
        ("Gestion erreurs", test_error_handling)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🎯 {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
            print(f"{'✅' if success else '❌'} {test_name}: {'RÉUSSI' if success else 'ÉCHOUÉ'}")
        except Exception as e:
            print(f"❌ {test_name}: ERREUR - {e}")
            results.append((test_name, False))
        print()
    
    # Résumé
    print("📊 === RÉSUMÉ DES TESTS ===")
    all_passed = True
    for test_name, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
        print(f"{status} - {test_name}")
        if not success:
            all_passed = False
    
    print()
    
    if all_passed:
        print("🎉 === ÉTAPE 3 VALIDÉE ! ===")
        print("✅ Pipeline complet eHub → ArtNet opérationnel")
        print("✅ Génération paquets ArtNet correcte")
        print("✅ Intégration multi-contrôleurs BC216")
        print("✅ Performance temps réel acceptable")
        print("✅ Gestion d'erreurs robuste")
        print("🎭 Prêt pour validation sur écran LED réel !")
        return True
    else:
        print("❌ === CORRECTIONS NÉCESSAIRES ===")
        return False

if __name__ == "__main__":
    success = test_etape_3()
    if success:
        print("\n🚀 Étape 3 validée ! Pipeline complet opérationnel !")
        exit(0)
    else:
        print("\n❌ Des corrections sont nécessaires")
        exit(1)
