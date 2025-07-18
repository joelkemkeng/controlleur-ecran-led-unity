"""
tools/show_config.py - Affichage de la configuration système du routeur LED

Ce script permet d'afficher la configuration système utilisée (config.json ou générée),
pour vérifier visuellement les contrôleurs, plages d'entités, univers, IP, etc.

Portabilité :
- Fonctionne sur Linux, Mac, Windows, Raspbian
- Aucune dépendance exotique

Exemple d'utilisation :
----------------------
$ python tools/show_config.py

Sortie attendue :
----------------
Configuration système :
  Port écoute eHuB : 8765
  Univers eHuB : 0
  Max FPS : 40
  Contrôleurs :
    - controller1 : 192.168.1.45, entités 100-4858, univers 0-31
    - controller2 : 192.168.1.46, entités 5100-9858, univers 32-63
    ...

Explication pédagogique :
------------------------
- Permet de vérifier la config avant tout lancement ou déploiement
- Utile pour s'assurer qu'on utilise la bonne config, les bons ports/IP, etc.
"""

from config.manager import ConfigManager

if __name__ == "__main__":
    config_mgr = ConfigManager("config/config.json")
    config = config_mgr.config
    print("Configuration système :")
    print(f"  Port écoute eHuB : {config.listen_port}")
    print(f"  Univers eHuB : {config.ehub_universe}")
    print(f"  Max FPS : {config.max_fps}")
    print(f"  Contrôleurs :")
    for name, ctrl in config.controllers.items():
        universes = f"{ctrl.universes[0]}-{ctrl.universes[-1]}" if ctrl.universes else "-"
        print(f"    - {name} : {ctrl.ip}, entités {ctrl.start_entity}-{ctrl.end_entity}, univers {universes}") 