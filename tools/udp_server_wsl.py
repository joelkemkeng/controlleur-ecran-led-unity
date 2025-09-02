#!/usr/bin/env python3
"""
Serveur UDP pour WSL - Reçoit les données Unity depuis Windows
Basé sur le script Windows qui fonctionne
"""

import socket
import sys
import subprocess
import re

def get_wsl_ip():
    """Récupère l'IP de WSL pour que Unity puisse s'y connecter"""
    try:
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        wsl_ip = result.stdout.strip().split()[0]
        return wsl_ip
    except:
        return "172.26.223.135"  # Fallback

def main():
    # Port par défaut ou spécifié en argument
    UDP_PORT = 8765
    if len(sys.argv) > 1:
        try:
            UDP_PORT = int(sys.argv[1])
        except ValueError:
            print("Port invalide, utilisation du port 8765")
    
    # IP d'écoute - WSL doit écouter sur toutes les interfaces
    UDP_IP = "0.0.0.0"  # Écoute sur toutes les interfaces (important pour WSL)
    
    wsl_ip = get_wsl_ip()
    
    print("=== Serveur UDP WSL pour Unity ===")
    print(f"IP WSL: {wsl_ip}")
    print(f"Écoute sur: {UDP_IP}:{UDP_PORT}")
    print(f"Unity doit envoyer vers: {wsl_ip}:{UDP_PORT}")
    print("-" * 50)
    
    # Création d'un socket serveur UDP
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))
        
        print(f"✓ Serveur UDP démarré sur {UDP_IP}:{UDP_PORT}")
        print("En attente des données Unity...")
        print("Appuyez sur Ctrl+C pour arrêter")
        print("-" * 50)
        
        packet_count = 0
        
        # Réception continue de packets UDP
        while True:
            try:
                data, addr = sock.recvfrom(64*1024)  # buffer size identique au script Windows
                packet_count += 1
                
                print(f"\n📦 Paquet #{packet_count}")
                print(f"🔗 Reçu de: {addr}")
                print(f"📏 Taille: {len(data)} bytes")
                print(f"📄 Données (50 premiers bytes): {data[:50]}")
                if len(data) > 50:
                    print(f"    ... et {len(data) - 50} bytes supplémentaires")
                
                # Ici vous pouvez ajouter le traitement des données
                # comme dans votre script Windows original:
                # entities_list = ehub.get_entities_list(data)
                # etc.
                
                print("-" * 50)
                
            except KeyboardInterrupt:
                print("\n\n🛑 Arrêt du serveur")
                break
            except Exception as e:
                print(f"❌ Erreur réception: {e}")
                continue
                
    except PermissionError:
        print(f"❌ Erreur: Permission refusée pour le port {UDP_PORT}")
        print("Essayez avec un port > 1024 ou lancez avec sudo")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Erreur: Le port {UDP_PORT} est déjà utilisé")
            print("Arrêtez l'autre processus ou utilisez un autre port")
        else:
            print(f"❌ Erreur système: {e}")
    except Exception as e:
        print(f"❌ Erreur serveur: {e}")
    finally:
        try:
            sock.close()
            print("🔒 Socket fermé")
        except:
            pass

if __name__ == "__main__":
    main()
