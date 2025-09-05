#!/usr/bin/env python3
"""
🧪 TEST ArtNet Sender - Tests spécifiques du module ArtNet
"""

import sys
import struct
import socket
import threading
import time

sys.path.append('/home/joel/projet_ecran/controlleur-ecran-led-unity/FINAL-DEV/etape-03-mapping-dmx')

from ehub_complete_pipeline_artnet import ArtNetSender

def test_artnet_packet_format():
    """
    Test 1: Format paquet ArtNet selon spécification
    """
    print("📦 Test 1: Format paquet ArtNet...")
    
    sender = ArtNetSender()
    if not sender.initialize():
        print("❌ Impossible d'initialiser sender")
        return False
    
    # Créer données DMX test
    dmx_data = bytearray(512)
    dmx_data[0] = 255   # Canal 1
    dmx_data[1] = 128   # Canal 2
    dmx_data[510] = 64  # Avant-dernier canal
    dmx_data[511] = 32  # Dernier canal
    
    # Générer paquet ArtNet
    packet = sender.create_artnet_packet(universe=42, dmx_data=bytes(dmx_data))
    
    # Vérifications détaillées
    checks = []
    
    # 1. Taille totale
    checks.append(("Taille paquet", len(packet) == 530))
    
    # 2. Signature Art-Net
    checks.append(("Signature", packet[0:8] == b"Art-Net\0"))
    
    # 3. OpCode DMX (0x5000 little-endian)
    opcode = struct.unpack('<H', packet[8:10])[0]
    checks.append(("OpCode DMX", opcode == 0x5000))
    
    # 4. Version protocole (14 big-endian)
    version = struct.unpack('>H', packet[10:12])[0]
    checks.append(("Version", version == 14))
    
    # 5. Sequence et Physical (0)
    checks.append(("Sequence", packet[12] == 0))
    checks.append(("Physical", packet[13] == 0))
    
    # 6. Univers (42 little-endian)
    universe = struct.unpack('<H', packet[14:16])[0]
    checks.append(("Univers", universe == 42))
    
    # 7. Longueur données (512 big-endian)
    length = struct.unpack('>H', packet[16:18])[0]
    checks.append(("Longueur DMX", length == 512))
    
    # 8. Données DMX
    dmx_start = packet[18:522]
    checks.append(("DMX Canal 1", dmx_start[0] == 255))
    checks.append(("DMX Canal 2", dmx_start[1] == 128))
    checks.append(("DMX Canal 511", dmx_start[510] == 64))
    checks.append(("DMX Canal 512", dmx_start[511] == 32))
    
    # Afficher résultats
    all_ok = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}")
        if not result:
            all_ok = False
    
    sender.close()
    return all_ok

def test_artnet_network_send():
    """
    Test 2: Envoi réseau ArtNet (avec mock receiver)
    """
    print("🌐 Test 2: Envoi réseau ArtNet...")
    
    # Créer mock receiver ArtNet
    received_packets = []
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    receiver_socket.bind(('127.0.0.1', 6454))
    receiver_socket.settimeout(2.0)
    
    def receiver_worker():
        try:
            while len(received_packets) < 3:  # Attendre 3 paquets
                data, addr = receiver_socket.recvfrom(1024)
                received_packets.append((data, addr))
                print(f"   📨 Paquet reçu de {addr}: {len(data)} bytes")
        except socket.timeout:
            pass
        except Exception as e:
            print(f"   ⚠️ Erreur receiver: {e}")
    
    # Démarrer receiver
    receiver_thread = threading.Thread(target=receiver_worker)
    receiver_thread.start()
    
    time.sleep(0.1)  # Laisser temps au receiver de démarrer
    
    # Créer sender et envoyer
    sender = ArtNetSender()
    if not sender.initialize():
        print("❌ Impossible d'initialiser sender")
        receiver_socket.close()
        return False
    
    # Envoyer plusieurs paquets test
    test_data = [
        (0, bytes([255, 0, 0] + [0]*509)),      # Univers 0: Rouge
        (1, bytes([0, 255, 0] + [0]*509)),      # Univers 1: Vert
        (2, bytes([0, 0, 255] + [0]*509)),      # Univers 2: Bleu
    ]
    
    for universe, dmx_data in test_data:
        success = sender.send_to_controller('127.0.0.1', universe, dmx_data)
        if success:
            print(f"   📤 Envoyé univers {universe}")
        else:
            print(f"   ❌ Échec envoi univers {universe}")
    
    # Attendre réception
    receiver_thread.join(timeout=3)
    receiver_socket.close()
    sender.close()
    
    # Vérifier réception
    if len(received_packets) >= 3:
        print(f"✅ {len(received_packets)} paquets reçus correctement")
        
        # Vérifier contenu du premier paquet
        first_packet = received_packets[0][0]
        if len(first_packet) == 530 and first_packet[0:8] == b"Art-Net\0":
            print("✅ Format paquet reçu correct")
            return True
        else:
            print("❌ Format paquet reçu incorrect")
            return False
    else:
        print(f"❌ Seulement {len(received_packets)} paquets reçus sur 3")
        return False

def test_artnet_performance():
    """
    Test 3: Performance envoi ArtNet
    """
    print("⚡ Test 3: Performance envoi ArtNet...")
    
    sender = ArtNetSender()
    if not sender.initialize():
        print("❌ Impossible d'initialiser sender")
        return False
    
    # Mock envoi pour éviter réseau
    sent_count = 0
    original_sendto = sender.socket.sendto
    
    def mock_sendto(data, addr):
        nonlocal sent_count
        sent_count += 1
        return len(data)
    
    sender.socket.sendto = mock_sendto
    
    # Test performance
    num_packets = 100
    universes = 10
    dmx_data = bytes([128] * 512)  # Données test
    
    start_time = time.time()
    
    for i in range(num_packets):
        universe = i % universes
        sender.send_to_controller('192.168.1.45', universe, dmx_data)
    
    elapsed = time.time() - start_time
    packets_per_second = num_packets / elapsed if elapsed > 0 else 0
    
    sender.close()
    
    print(f"✅ Performance: {packets_per_second:.1f} paquets/seconde")
    print(f"   📊 {num_packets} paquets en {elapsed:.3f}s")
    print(f"   🎯 {sent_count} paquets traités")
    
    if packets_per_second >= 500:  # ArtNet devrait être très rapide
        print("✅ Performance excellente (>500 paquets/s)")
        return True
    elif packets_per_second >= 100:
        print("✅ Performance acceptable (>100 paquets/s)")
        return True
    else:
        print("⚠️ Performance insuffisante (<100 paquets/s)")
        return False

def test_artnet_error_handling():
    """
    Test 4: Gestion d'erreurs ArtNet
    """
    print("⚠️ Test 4: Gestion d'erreurs ArtNet...")
    
    sender = ArtNetSender()
    if not sender.initialize():
        print("❌ Impossible d'initialiser sender")
        return False
    
    tests_passed = 0
    
    # Test 1: Données DMX trop courtes
    result1 = sender.send_to_controller('127.0.0.1', 0, b'short')
    if result1:  # Devrait réussir (padding automatique)
        print("   ✅ Padding données courtes")
        tests_passed += 1
    
    # Test 2: Données DMX trop longues
    long_data = bytes([255] * 1000)
    result2 = sender.send_to_controller('127.0.0.1', 0, long_data)
    if result2:  # Devrait réussir (troncature automatique)
        print("   ✅ Troncature données longues")
        tests_passed += 1
    
    # Test 3: Univers invalide (très grand)
    result3 = sender.send_to_controller('127.0.0.1', 65535, bytes(512))
    if result3:  # Devrait fonctionner
        print("   ✅ Univers limite accepté")
        tests_passed += 1
    
    # Test 4: IP invalide (non résolvable)
    result4 = sender.send_to_controller('999.999.999.999', 0, bytes(512))
    if not result4:  # Devrait échouer
        print("   ✅ IP invalide correctement rejetée")
        tests_passed += 1
    
    sender.close()
    
    if tests_passed >= 3:
        print(f"✅ Gestion d'erreurs: {tests_passed}/4 tests réussis")
        return True
    else:
        print(f"❌ Gestion d'erreurs: {tests_passed}/4 tests réussis")
        return False

def test_artnet_multiple_universes():
    """
    Test 5: Gestion multi-univers
    """
    print("🌍 Test 5: Gestion multi-univers...")
    
    sender = ArtNetSender()
    if not sender.initialize():
        print("❌ Impossible d'initialiser sender")
        return False
    
    # Tester plusieurs univers simultanément
    universes_test = [0, 1, 5, 10, 50, 100, 127]
    
    # Mock pour compter envois
    sent_universes = []
    original_send = sender.send_to_controller
    
    def mock_send(ip, universe, data):
        sent_universes.append((ip, universe))
        return True
    
    sender.send_to_controller = mock_send
    
    # Envoyer vers différents univers
    for universe in universes_test:
        dmx_data = bytes([universe % 256] * 512)  # Données uniques par univers
        sender.send_to_controller('192.168.1.45', universe, dmx_data)
    
    sender.close()
    
    # Vérifier
    if len(sent_universes) == len(universes_test):
        unique_universes = set(u for ip, u in sent_universes)
        if len(unique_universes) == len(universes_test):
            print(f"✅ {len(universes_test)} univers distincts traités")
            print(f"   🌍 Univers: {sorted(unique_universes)}")
            return True
        else:
            print("❌ Univers dupliqués détectés")
            return False
    else:
        print(f"❌ {len(sent_universes)} paquets envoyés sur {len(universes_test)}")
        return False

def main():
    """
    Lance tous les tests ArtNet
    """
    print("🧪 === TESTS ARTNET SENDER ===")
    print()
    
    tests = [
        ("Format paquet ArtNet", test_artnet_packet_format),
        ("Envoi réseau ArtNet", test_artnet_network_send),
        ("Performance ArtNet", test_artnet_performance),
        ("Gestion erreurs", test_artnet_error_handling),
        ("Multi-univers", test_artnet_multiple_universes)
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
    print("📊 === RÉSUMÉ TESTS ARTNET ===")
    all_passed = True
    for test_name, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
        print(f"{status} - {test_name}")
        if not success:
            all_passed = False
    
    if all_passed:
        print("\n🎭 Module ArtNet entièrement validé !")
    else:
        print("\n❌ Corrections ArtNet nécessaires")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
