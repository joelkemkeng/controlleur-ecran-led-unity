#!/usr/bin/env python3
"""
🧪 TEST ÉTAPE 2 : Décodage eHub Intégré
Test complet de l'intégration: Réception + Config + Décodage
"""

import sys
import os
import time
import threading
import socket
import gzip
import struct

# Ajouter les chemins
sys.path.append('/home/joel/projet_ecran/controlleur-ecran-led-unity/FINAL-DEV/etape-02-decodage-ehub')

from ehub_complete_pipeline_decoder import EHubDecoder, EHubEntity, EHubPacket

def create_test_ehub_message() -> bytes:
    """
    Crée un message eHub de test valide selon la spécification officielle
    Format header: "eHuB" + type(1) + universe(1) + entity_count(2) + payload_size(2) = 10 bytes
    Format entités: entity_id(2) + r(1) + g(1) + b(1) + w(1) = 6 bytes par entité
    """
    # 1. Créer des entités de test selon format spécification officielle
    entities_data = b''
    test_entities = [
        (100, 255, 0, 0, 0),    # Rouge
        (101, 0, 255, 0, 0),    # Vert
        (102, 0, 0, 255, 0),    # Bleu
        (200, 255, 255, 255, 100)  # Blanc
    ]
    
    for entity_id, r, g, b, w in test_entities:
        # Format selon spécification: entity_id(2 bytes) + RGBW(4 bytes) = 6 bytes par entité
        entity_bytes = struct.pack('<H', entity_id) + bytes([r, g, b, w])  # H = unsigned short (2 bytes)
        entities_data += entity_bytes
    
    # 2. Compresser les données
    compressed_data = gzip.compress(entities_data)
    
    # 3. Créer le header selon spécification officielle
    signature = b'eHuB'           # 4 bytes
    packet_type = 2               # 1 byte - UPDATE
    universe = 1                  # 1 byte - Numéro univers
    entity_count = len(test_entities)  # 2 bytes - Nombre d'entités
    payload_size = len(compressed_data)  # 2 bytes - Taille payload compressé
    
    # Assemblage header (10 bytes total)
    header = signature                              # 4 bytes
    header += bytes([packet_type])                  # 1 byte
    header += bytes([universe])                     # 1 byte
    header += struct.pack('<H', entity_count)       # 2 bytes
    header += struct.pack('<H', payload_size)       # 2 bytes
    
    # 4. Message complet
    return header + compressed_data

def test_integration_complete():
    """
    Test 1: Intégration complète des 3 modules
    """
    print("🔧 Test 1: Intégration complète...")
    
    # Initialisation décodeur
    decoder = EHubDecoder(port=8772)
    
    success = decoder.initialize()
    
    if success and decoder.receiver and decoder.screen_config:
        print("✅ Intégration réussie")
        print(f"   📡 Récepteur: OK")
        print(f"   🗺️  Config: {len(decoder.screen_config.mappings)} mappings")
        decoder.stop()
        return True
    else:
        print("❌ Échec intégration")
        if decoder.receiver:
            decoder.stop()
        return False

def test_ehub_decoding():
    """
    Test 2: Décodage message eHub
    """
    print("🔬 Test 2: Décodage message eHub...")
    
    decoder = EHubDecoder(port=8773)
    
    if not decoder.initialize():
        print("❌ Impossible d'initialiser le décodeur")
        return False
    
    # Thread pour envoyer un message test
    def sender_worker():
        time.sleep(1)
        
        test_message = create_test_ehub_message()
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sender.sendto(test_message, ("127.0.0.1", 8773))
        sender.close()
        
        print(f"📤 Message eHub test envoyé ({len(test_message)} bytes)")
    
    # Démarrer l'envoi
    sender_thread = threading.Thread(target=sender_worker)
    sender_thread.start()
    
    # Attendre et décoder
    packet_decoded = None
    start_time = time.time()
    
    while time.time() - start_time < 5:
        message = decoder.receiver.receive_message(timeout=1.0)
        
        if message:
            packet_decoded = decoder.decode_ehub_packet(message)
            break
    
    decoder.stop()
    sender_thread.join()
    
    if packet_decoded:
        print("✅ Décodage réussi")
        print(f"   📋 Signature: {packet_decoded.signature}")
        print(f"   📋 Type: {packet_decoded.packet_type}")
        print(f"   📋 Entités: {len(packet_decoded.entities)}")
        
        # Vérifier quelques entités
        if len(packet_decoded.entities) >= 3:
            entity1 = packet_decoded.entities[0]
            print(f"   🔸 Entité 1: ID={entity1.entity_id} RGB=({entity1.red},{entity1.green},{entity1.blue})")
            
            if entity1.entity_id == 100 and entity1.red == 255:
                print("   ✅ Données décodées correctement")
                return True
            else:
                print("   ❌ Données décodées incorrectement")
                return False
        else:
            print("   ⚠️ Pas assez d'entités décodées")
            return False
    else:
        print("❌ Aucun paquet décodé")
        return False

def test_mapping_integration():
    """
    Test 3: Intégration avec mapping écran
    """
    print("🗺️  Test 3: Intégration mapping écran...")
    
    decoder = EHubDecoder(port=8774)
    
    if not decoder.initialize():
        print("❌ Impossible d'initialiser le décodeur")
        return False
    
    # Test mapping direct
    mapping_100 = decoder.get_led_mapping(100)
    mapping_999999 = decoder.get_led_mapping(999999)  # Entité inexistante
    
    decoder.stop()
    
    if mapping_100:
        print("✅ Mapping trouvé pour entité 100")
        print(f"   🎯 Entité 100 → {mapping_100.controller_ip}:u{mapping_100.universe}:ch{mapping_100.channel}")
        
        if mapping_999999 is None:
            print("✅ Entité inexistante correctement gérée")
            return True
        else:
            print("❌ Entité inexistante retourne un mapping")
            return False
    else:
        print("❌ Aucun mapping trouvé pour entité 100")
        return False

def test_error_handling():
    """
    Test 4: Gestion d'erreurs décodage
    """
    print("⚠️  Test 4: Gestion d'erreurs...")
    
    decoder = EHubDecoder(port=8775)
    
    if not decoder.initialize():
        print("❌ Impossible d'initialiser le décodeur")
        return False
    
    # Thread pour envoyer des messages corrompus
    def sender_worker():
        time.sleep(1)
        
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Message 1: Signature incorrecte
        bad_msg1 = b"XXXX" + b"\x02\x01\x00\x00\x10\x00\x00\x00" + b"corrupted_data"
        sender.sendto(bad_msg1, ("127.0.0.1", 8775))
        
        time.sleep(0.1)
        
        # Message 2: Trop court
        bad_msg2 = b"eHuB\x02"
        sender.sendto(bad_msg2, ("127.0.0.1", 8775))
        
        sender.close()
    
    sender_thread = threading.Thread(target=sender_worker)
    sender_thread.start()
    
    # Attendre et tenter décodage
    errors_handled = 0
    start_time = time.time()
    
    while time.time() - start_time < 3 and errors_handled < 2:
        message = decoder.receiver.receive_message(timeout=1.0)
        
        if message:
            packet = decoder.decode_ehub_packet(message)
            if packet is None:
                errors_handled += 1
    
    decoder.stop()
    sender_thread.join()
    
    if errors_handled >= 1:
        print("✅ Erreurs de décodage correctement gérées")
        return True
    else:
        print("❌ Gestion d'erreurs défaillante")
        return False

def test_etape_2():
    """
    Test complet de l'étape 2
    """
    print("🧪 === TEST ÉTAPE 2 : DÉCODAGE eHUB INTÉGRÉ ===")
    print()
    
    tests = [
        ("Intégration complète", test_integration_complete),
        ("Décodage eHub", test_ehub_decoding),
        ("Mapping écran", test_mapping_integration),
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
        print("🎉 === ÉTAPE 2 VALIDÉE ! ===")
        print("✅ Intégration Réception + Config + Décodage")
        print("✅ Messages eHub correctement décodés")
        print("✅ Mapping écran opérationnel")
        print("✅ Gestion d'erreurs robuste")
        print("✅ Prêt pour l'étape 3 (Mapping DMX)")
        return True
    else:
        print("❌ === CORRECTIONS NÉCESSAIRES ===")
        return False

if __name__ == "__main__":
    success = test_etape_2()
    if success:
        print("\n🚀 Étape 2 validée ! Vous pouvez passer à l'étape 3 !")
        exit(0)
    else:
        print("\n❌ Des corrections sont nécessaires")
        exit(1)
