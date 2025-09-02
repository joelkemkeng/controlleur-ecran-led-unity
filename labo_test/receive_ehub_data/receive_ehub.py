import socket

UDP_IP = "0.0.0.0"  # Écoute sur toutes les interfaces pour recevoir depuis Windows
UDP_PORT = 8765

print("Démarrage du récepteur de données eHub...")
print(f"Écoute sur {UDP_IP}:{UDP_PORT}")
print("Pour Unity/Windows, envoyez vers l'IP WSL visible ci-dessous:")

# Affiche l'IP WSL pour que Unity puisse s'y connecter
import subprocess
try:
    result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
    wsl_ip = result.stdout.strip().split()[0]
    print(f"IP WSL: {wsl_ip}:{UDP_PORT}")
except:
    print("IP WSL: [non détectée]")

# Création d'un objet de socket
sock = socket.socket(socket.AF_INET,  # Internet
                     socket.SOCK_DGRAM)  # UDP

# Permet de réutiliser l'adresse si elle était récemment utilisée
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    sock.bind((UDP_IP, UDP_PORT))
except OSError as e:
    if e.errno == 98:  # Address already in use
        print(f"Erreur: Le port {UDP_PORT} est déjà utilisé.")
        print("Arrêtez l'autre processus ou attendez quelques secondes.")
        exit(1)
    else:
        raise

print("En attente de données eHub...")

# Réception continue de packets UDP suivi de leur traitement et retransmission via Artnet
while True:
    try:
        data, addr = sock.recvfrom(64*1024)  # buffer size is 64KB
        print(f"\n\n\n\n\n----la data recue direct du reseau: {data}")
        print(f"Reçu de: {addr}")
        print(f"Taille: {len(data)} bytes")
        
        # Ici vous pouvez ajouter votre traitement comme dans le script Windows:
        # entities_list = ehub.get_entities_list(data)
        # etc.
        
    except KeyboardInterrupt:
        print("\nArrêt du récepteur...")
        break
    except Exception as e:
        print(f"Erreur: {e}")

sock.close()
print("Socket fermé.")