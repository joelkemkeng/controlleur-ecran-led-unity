#!/usr/bin/env python3
"""
Script de test pour envoyer des données vers WSL (simule Unity)
À lancer depuis Windows ou pour tester la connectivité
"""

import socket
import time
import sys

def test_send_to_wsl():
    """Envoie des données de test vers le serveur WSL"""
    
    # IP WSL (celle affichée par le serveur)
    WSL_IP = "172.26.223.135"
    WSL_PORT = 8765
    
    if len(sys.argv) > 1:
        WSL_IP = sys.argv[1]
    if len(sys.argv) > 2:
        WSL_PORT = int(sys.argv[2])
    
    print(f"=== Test d'envoi vers WSL ===")
    print(f"Cible: {WSL_IP}:{WSL_PORT}")
    
    try:
        # Création du socket client
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Test de connectivité
        test_data = b"TEST_UNITY_TO_WSL"
        sock.sendto(test_data, (WSL_IP, WSL_PORT))
        print(f"✓ Données de test envoyées: {test_data}")
        
        # Envoi de données simulées en continu
        packet_num = 0
        while packet_num < 10:  # Envoie 10 paquets de test
            packet_num += 1
            
            # Simule des données Unity/eHub
            fake_data = f"UNITY_DATA_PACKET_{packet_num}".encode() + b"_" + b"X" * 100
            
            sock.sendto(fake_data, (WSL_IP, WSL_PORT))
            print(f"📤 Paquet #{packet_num} envoyé ({len(fake_data)} bytes)")
            
            time.sleep(1)  # Pause entre les paquets
        
        print("✓ Test terminé")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("Vérifiez que:")
        print("1. Le serveur WSL est en cours d'exécution")
        print("2. L'IP WSL est correcte")
        print("3. Le pare-feu Windows autorise les connexions sortantes")
    finally:
        sock.close()

if __name__ == "__main__":
    test_send_to_wsl()
