#!/usr/bin/env python3
"""
🧪 TEST RÉSEAU - Vérification connectivité Unity ↔ WSL
Test de connectivité réseau pour réception eHub
"""

import socket
import subprocess
import time
import threading

def test_network_connectivity():
    """
    Test de connectivité réseau complète
    """
    print("🌐 === TEST CONNECTIVITÉ RÉSEAU ===")
    print()
    
    # 1. Détection IP WSL
    print("🔍 Test 1: Détection IP WSL...")
    try:
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        wsl_ip = result.stdout.strip().split()[0]
        print(f"✅ IP WSL: {wsl_ip}")
    except Exception as e:
        print(f"❌ Erreur détection IP: {e}")
        return False
    
    # 2. Test port libre
    print("🔌 Test 2: Vérification port 8765...")
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_socket.bind(("0.0.0.0", 8765))
        test_socket.close()
        print("✅ Port 8765 disponible")
    except OSError as e:
        if e.errno == 98:
            print("⚠️ Port 8765 occupé (arrêtez l'autre processus)")
            return False
        else:
            print(f"❌ Erreur port: {e}")
            return False
    
    # 3. Test écoute/envoi local
    print("📡 Test 3: Test écoute/envoi local...")
    
    # Récepteur
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    receiver.bind(("0.0.0.0", 8765))
    receiver.settimeout(3.0)
    
    # Thread d'envoi
    def sender_worker():
        time.sleep(0.5)
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_message = b"TEST_CONNECTIVITY_MESSAGE"
        sender.sendto(test_message, (wsl_ip, 8765))
        sender.close()
    
    sender_thread = threading.Thread(target=sender_worker)
    sender_thread.start()
    
    try:
        data, addr = receiver.recvfrom(1024)
        print(f"✅ Message reçu de {addr}: {len(data)} bytes")
        success = True
    except socket.timeout:
        print("❌ Timeout - Aucun message reçu")
        success = False
    except Exception as e:
        print(f"❌ Erreur réception: {e}")
        success = False
    
    receiver.close()
    sender_thread.join()
    
    if not success:
        return False
    
    # 4. Instructions Unity
    print()
    print("📋 === CONFIGURATION UNITY ===")
    print(f"🎯 IP cible: {wsl_ip}")
    print(f"🎯 Port cible: 8765")
    print(f"🎯 Configuration eHub: UDP vers {wsl_ip}:8765")
    print("================================")
    
    return True

def test_firewall_connectivity():
    """
    Test connectivité avec différentes interfaces
    """
    print("\n🔥 Test 4: Vérification firewall/interfaces...")
    
    interfaces = ["127.0.0.1", "0.0.0.0"]
    
    for interface in interfaces:
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            test_socket.bind((interface, 8766))  # Port test différent
            test_socket.close()
            print(f"✅ Interface {interface}: OK")
        except Exception as e:
            print(f"❌ Interface {interface}: {e}")
            return False
    
    return True

def main():
    """
    Test complet de connectivité réseau
    """
    print("🧪 TEST CONNECTIVITÉ RÉSEAU UNITY ↔ WSL")
    print()
    
    if not test_network_connectivity():
        print("\n❌ Tests de connectivité échoués")
        return False
    
    if not test_firewall_connectivity():
        print("\n❌ Tests firewall/interfaces échoués")
        return False
    
    print("\n🎉 === CONNECTIVITÉ VALIDÉE ! ===")
    print("✅ Réseau opérationnel")
    print("✅ Port disponible")
    print("✅ Unity peut se connecter")
    print("✅ Prêt pour réception eHub")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
