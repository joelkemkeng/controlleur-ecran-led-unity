#!/usr/bin/env python3
"""
Test simple UDP serveur/client sur le même script
"""

import socket
import threading
import time

def server_thread(port):
    """Thread serveur"""
    print(f"🟢 Serveur: Démarrage sur port {port}")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', port))
    
    print(f"🟢 Serveur: En écoute sur 0.0.0.0:{port}")
    
    try:
        for i in range(5):  # Attend 5 paquets
            data, addr = sock.recvfrom(1024)
            print(f"🟢 Serveur: Reçu '{data.decode()}' de {addr}")
    except Exception as e:
        print(f"🔴 Serveur: Erreur {e}")
    finally:
        sock.close()
        print("🟢 Serveur: Fermé")

def client_thread(port):
    """Thread client"""
    time.sleep(1)  # Attend que le serveur démarre
    
    print(f"🔵 Client: Démarrage")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        for i in range(5):
            message = f"Message {i+1}"
            sock.sendto(message.encode(), ('127.0.0.1', port))
            print(f"🔵 Client: Envoyé '{message}'")
            time.sleep(0.5)
    except Exception as e:
        print(f"🔴 Client: Erreur {e}")
    finally:
        sock.close()
        print("🔵 Client: Fermé")

def main():
    port = 8766  # Port différent pour éviter les conflits
    
    print("=== Test UDP Local ===")
    
    # Lance serveur et client en parallèle
    server = threading.Thread(target=server_thread, args=(port,))
    client = threading.Thread(target=client_thread, args=(port,))
    
    server.start()
    client.start()
    
    server.join()
    client.join()
    
    print("=== Test terminé ===")

if __name__ == "__main__":
    main()
