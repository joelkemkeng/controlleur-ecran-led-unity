#!/usr/bin/env python3
"""
Client de test UDP pour recevoir les données eHub depuis WSL vers Windows
"""

import socket
import sys
import subprocess
import re

def get_windows_ip():
    """Récupère l'IP de l'hôte Windows depuis WSL"""
    try:
        # Méthode 1: Via /etc/resolv.conf (WSL2)
        with open('/etc/resolv.conf', 'r') as f:
            content = f.read()
            match = re.search(r'nameserver\s+(\d+\.\d+\.\d+\.\d+)', content)
            if match:
                return match.group(1)
    except:
        pass
    
    try:
        # Méthode 2: Via route par défaut
        result = subprocess.run(['ip', 'route', 'show', 'default'], 
                              capture_output=True, text=True)
        match = re.search(r'via\s+(\d+\.\d+\.\d+\.\d+)', result.stdout)
        if match:
            return match.group(1)
    except:
        pass
    
    # Fallback
    return "172.17.0.1"  # IP par défaut WSL2

def main():
    # Port par défaut ou spécifié en argument
    port = 8765
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Port invalide, utilisation du port 8765")
    
    # Détection automatique de l'IP Windows
    windows_ip = get_windows_ip()
    
    # Possibilité de spécifier une IP manuellement
    if len(sys.argv) > 2:
        windows_ip = sys.argv[2]
    
    print(f"IP Windows détectée: {windows_ip}")
    print(f"Port Unity: {port}")
    
    # Crée le socket client UDP
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_sock.settimeout(5.0)  # Timeout de 5 secondes
    
    try:
        print(f"Tentative de connexion à Unity sur {windows_ip}:{port}")
        
        # Test de connectivité avec un ping
        ping_result = subprocess.run(['ping', '-c', '1', '-W', '2', windows_ip], 
                                   capture_output=True)
        if ping_result.returncode != 0:
            print(f"ATTENTION: L'IP {windows_ip} ne répond pas au ping")
        else:
            print(f"Ping vers {windows_ip} réussi")
        
        # Envoie un message initial pour "s'enregistrer" auprès du serveur
        client_sock.sendto(b"CONNECT_FROM_WSL", (windows_ip, port))
        print(f"Message de connexion envoyé")
        
        # Boucle de réception
        print("En attente de données Unity...")
        print("Appuyez sur Ctrl+C pour arrêter")
        print("-" * 50)
        
        while True:
            try:
                data, addr = client_sock.recvfrom(4096)
                print(f"✓ Reçu {len(data)} bytes de {addr}")
                print(f"Données: {data[:100]}..." if len(data) > 100 else f"Données: {data}")
                print("-" * 50)
                
            except socket.timeout:
                print(".", end="", flush=True)  # Indicateur de vie
                continue
            except KeyboardInterrupt:
                print("\n\nArrêt du client")
                break
            except Exception as e:
                print(f"Erreur réception: {e}")
                break
                
    except Exception as e:
        print(f"Erreur client: {e}")
        print("\nSolutions possibles:")
        print("1. Vérifiez que Unity est bien lancé")
        print("2. Vérifiez le port utilisé par Unity")
        print("3. Vérifiez le pare-feu Windows")
        print(f"4. Essayez avec une IP différente: python3 {sys.argv[0]} {port} <IP_WINDOWS>")
    finally:
        client_sock.close()

if __name__ == "__main__":
    print("=== Client UDP WSL -> Windows/Unity ===")
    main()
