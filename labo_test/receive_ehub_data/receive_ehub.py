import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 8765

print("Démarrage du récepteur de données eHub...")
print(f"Écoute sur {UDP_IP}:{UDP_PORT}")

# Création d'un objet de socket
sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP
sock.bind((UDP_IP, UDP_PORT))

print("En attente de données eHub...")

# Réception continue de packets UDP
while True:
    try:
        data, addr = sock.recvfrom(64*1024)  # buffer size is 64KB
        print(f"\n--- Données reçues de {addr} ---")
        print(f"Données brutes: {data}")
        print(f"Taille: {len(data)} bytes")
        
        # Tentative de décodage en UTF-8 si possible
        try:
            decoded_data = data.decode('utf-8')
            print(f"Données décodées: {decoded_data}")
        except UnicodeDecodeError:
            print("Données binaires (non décodables en UTF-8)")
            
    except KeyboardInterrupt:
        print("\nArrêt du récepteur...")
        break
    except Exception as e:
        print(f"Erreur: {e}")

sock.close()
print("Socket fermé.")