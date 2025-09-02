#!/usr/bin/env python3
"""
Script de diagnostic réseau WSL <-> Windows pour Unity UDP
"""

import socket
import subprocess
import re
import sys

def get_network_info():
    """Récupère les informations réseau WSL"""
    print("=== Informations réseau WSL ===")
    
    # IP de WSL
    try:
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        wsl_ip = result.stdout.strip().split()[0]
        print(f"IP WSL: {wsl_ip}")
    except:
        print("Impossible de récupérer l'IP WSL")
    
    # Gateway (IP Windows)
    try:
        result = subprocess.run(['ip', 'route', 'show', 'default'], 
                              capture_output=True, text=True)
        match = re.search(r'via\s+(\d+\.\d+\.\d+\.\d+)', result.stdout)
        if match:
            windows_ip = match.group(1)
            print(f"IP Windows (gateway): {windows_ip}")
        else:
            print("Impossible de trouver l'IP Windows via route")
    except:
        print("Erreur lors de la récupération de la route")
    
    # DNS (méthode alternative pour l'IP Windows)
    try:
        with open('/etc/resolv.conf', 'r') as f:
            content = f.read()
            match = re.search(r'nameserver\s+(\d+\.\d+\.\d+\.\d+)', content)
            if match:
                dns_ip = match.group(1)
                print(f"IP Windows (DNS): {dns_ip}")
    except:
        print("Impossible de lire /etc/resolv.conf")

def test_connectivity(target_ip, port=8765):
    """Test la connectivité vers l'IP cible"""
    print(f"\n=== Test connectivité vers {target_ip}:{port} ===")
    
    # Test ping
    print(f"Test ping vers {target_ip}...")
    ping_result = subprocess.run(['ping', '-c', '3', '-W', '2', target_ip], 
                               capture_output=True, text=True)
    if ping_result.returncode == 0:
        print("✓ Ping réussi")
    else:
        print("✗ Ping échoué")
        print("Sortie ping:", ping_result.stdout[:200])
    
    # Test UDP
    print(f"Test UDP sur port {port}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.0)
        
        # Envoi d'un paquet test
        sock.sendto(b"TEST_WSL", (target_ip, port))
        print("✓ Paquet UDP envoyé")
        
        # Tentative de réception (peut échouer si Unity n'envoie pas de réponse)
        try:
            data, addr = sock.recvfrom(1024)
            print(f"✓ Réponse reçue: {data[:50]}")
        except socket.timeout:
            print("⚠ Pas de réponse (normal si Unity ne répond pas aux paquets test)")
        
        sock.close()
        
    except Exception as e:
        print(f"✗ Erreur UDP: {e}")

def check_firewall():
    """Vérifications pour le pare-feu"""
    print("\n=== Conseils pare-feu Windows ===")
    print("Si la connectivité échoue, vérifiez :")
    print("1. Pare-feu Windows : autorisez Unity et le port 8765")
    print("2. Antivirus : peut bloquer les connexions réseau")
    print("3. Dans Unity : vérifiez que le serveur UDP écoute sur '0.0.0.0' et non '127.0.0.1'")

def main():
    print("=== Diagnostic réseau WSL -> Windows/Unity ===")
    
    # Récupère les infos réseau
    get_network_info()
    
    # IP cible (Windows)
    target_ip = None
    port = 8765
    
    if len(sys.argv) > 1:
        target_ip = sys.argv[1]
    else:
        # Auto-détection
        try:
            result = subprocess.run(['ip', 'route', 'show', 'default'], 
                                  capture_output=True, text=True)
            match = re.search(r'via\s+(\d+\.\d+\.\d+\.\d+)', result.stdout)
            if match:
                target_ip = match.group(1)
        except:
            target_ip = "172.17.0.1"  # Fallback
    
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except:
            pass
    
    # Test de connectivité
    if target_ip:
        test_connectivity(target_ip, port)
    
    # Conseils pare-feu
    check_firewall()
    
    print(f"\n=== Commandes de test ===")
    print(f"Pour tester avec l'IP détectée: python3 test_client_udp_wsl.py {port} {target_ip}")
    print(f"Pour diagnostiquer à nouveau: python3 {sys.argv[0]} [IP] [PORT]")

if __name__ == "__main__":
    main()
