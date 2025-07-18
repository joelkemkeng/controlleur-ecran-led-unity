"""
tools/check_network.py - Test de connectivité réseau vers les contrôleurs ArtNet

Ce script permet de vérifier que tous les contrôleurs définis dans la configuration (config.json)
sont bien joignables sur le réseau (UDP, port 6454). Il utilise la méthode validate_controller_connection
de ArtNetSender et affiche un rapport clair pour chaque IP.

Portabilité :
- Fonctionne sur Linux, Mac, Windows, Raspbian
- Aucune dépendance exotique

Exemple d'utilisation :
----------------------
$ python tools/check_network.py

Sortie attendue :
----------------
[OK] 192.168.1.45 (ArtNet UDP 6454)
[OK] 192.168.1.46 (ArtNet UDP 6454)
[FAIL] 192.168.1.99 (ArtNet UDP 6454)

Explication pédagogique :
------------------------
- Permet de diagnostiquer rapidement les problèmes de câblage, d'IP, de firewall
- À utiliser avant tout test ou déploiement réel
"""

from config.manager import ConfigManager
from artnet.sender import ArtNetSender

if __name__ == "__main__":
    config_mgr = ConfigManager("config/config.json")
    sender = ArtNetSender()
    ips = set(ctrl.ip for ctrl in config_mgr.config.controllers.values())
    print("Test de connectivité ArtNet (UDP 6454) :")
    for ip in sorted(ips):
        ok = sender.validate_controller_connection(ip)
        if ok:
            print(f"[OK]   {ip} (ArtNet UDP 6454)")
        else:
            print(f"[FAIL] {ip} (ArtNet UDP 6454)") 