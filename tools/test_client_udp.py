#!/usr/bin/env python3
"""
Client de test UDP pour recevoir les données eHub
"""

import socket
import sys

def main():
    # Port par défaut ou spécifié en argument
    port = 8765
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Port invalide, utilisation du port 8766")
    
    host = '0.0.0.0'
    
    # Crée le socket client UDP
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        # Envoie un message initial pour "s'enregistrer" auprès du serveur
        client_sock.sendto(b"CONNECT", (host, port))
        print(f"Connexion au serveur {host}:{port}")
        
        # Boucle de réception
        while True:
            try:
                data, addr = client_sock.recvfrom(4096)
                print(f"Reçu {len(data)} bytes de {addr}")
                print(f"Données: {data[:50]}..." if len(data) > 50 else f"Données: {data}")
                print("-" * 50)
                
            except KeyboardInterrupt:
                print("\nArrêt du client")
                break
            except Exception as e:
                print(f"Erreur réception: {e}")
                
    except Exception as e:
        print(f"Erreur client: {e}")
    finally:
        client_sock.close()

if __name__ == "__main__":
    main()