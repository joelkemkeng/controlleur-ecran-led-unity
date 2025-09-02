#!/usr/bin/env python3
"""
Utilitaire pour vérifier les ports UDP utilisés
"""

import subprocess
import socket

def check_port_usage():
    """Vérifie quels processus utilisent le port 8765"""
    print("=== Vérification des ports UDP ===")
    
    try:
        # Vérification avec netstat
        result = subprocess.run(['netstat', '-ulnp'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        print("Ports UDP en écoute :")
        for line in lines:
            if ':8765' in line or 'Proto' in line:
                print(line)
        
        print("\nTous les ports UDP :")
        for line in lines:
            if 'udp' in line.lower():
                print(line)
                
    except Exception as e:
        print(f"Erreur netstat: {e}")
    
    # Test direct du port
    print(f"\n=== Test direct du port 8765 ===")
    try:
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_sock.bind(('0.0.0.0', 8765))
        print("✓ Port 8765 disponible")
        test_sock.close()
    except OSError as e:
        print(f"✗ Port 8765 occupé: {e}")

def get_network_info():
    """Affiche les informations réseau WSL"""
    print("\n=== Informations réseau WSL ===")
    
    try:
        # IP WSL
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        wsl_ip = result.stdout.strip()
        print(f"IP WSL: {wsl_ip}")
        
        # Interfaces réseau
        result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
        print("\nInterfaces réseau :")
        for line in result.stdout.split('\n'):
            if 'inet ' in line and 'scope global' in line:
                print(f"  {line.strip()}")
                
    except Exception as e:
        print(f"Erreur réseau: {e}")

if __name__ == "__main__":
    check_port_usage()
    get_network_info()
    
    print(f"\n=== Instructions ===")
    print("1. Lancez le serveur WSL: python3 udp_server_wsl.py")
    print("2. Dans Unity, configurez l'IP de destination vers votre IP WSL")
    print("3. Unity doit envoyer vers WSL, pas l'inverse")
