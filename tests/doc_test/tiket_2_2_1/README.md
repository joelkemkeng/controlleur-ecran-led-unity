# Ticket 2.2.1 – Config Manager

## Objectif
Mettre en place un gestionnaire de configuration centralisé pour le routeur LED, capable de charger la configuration réelle de l'écran (issue de l'Excel), de créer une config par défaut, et de garantir la portabilité et la maintenabilité du projet.

## Ce que fait ce ticket
- Implémente la classe `ConfigManager` dans `config/manager.py`.
- Structures de données : `ControllerConfig`, `SystemConfig` (dataclasses)
- Chargement automatique d'un fichier `config/config.json` (structure fidèle à l'écran réel)
- Création d'une config par défaut si le fichier n'existe pas
- Docstring pdoc claire et exemples d'utilisation
- Portabilité assurée (aucune dépendance exotique)

## Pourquoi c'est important
- Permet de gérer facilement la configuration de plusieurs contrôleurs et univers ArtNet
- Facilite la maintenance, l'évolution et la portabilité du projet (Linux, Raspbian, Mac...)
- Permet de tester le projet sur la vraie structure de l'écran (mapping réel)

## Comment tester concrètement
1. Lancer les tests unitaires :
   ```bash
   .\venv\Scripts\activate
   pytest tests/test_config_manager.py
   ```
2. Les tests vérifient :
   - Le chargement correct de la config réelle (4 contrôleurs, plages, univers)
   - La création d'une config par défaut si le fichier n'existe pas
   - La cohérence des plages, IP, univers, etc.
3. En cas réel, tu peux modifier `config/config.json` pour adapter la config à ton installation, puis relancer le routeur.

## Exemples concrets
```python
from config.manager import ConfigManager
mgr = ConfigManager("config/config.json")
print(mgr.config.listen_port)  # 8765
for name, ctrl in mgr.config.controllers.items():
    print(f"{name}: {ctrl.ip} ({ctrl.start_entity}-{ctrl.end_entity}) universes={ctrl.universes}")
```

### Exemple de sortie console réelle
```
8765
controller1: 192.168.1.45 (100-4858) universes=[0, 1, ..., 31]
controller2: 192.168.1.46 (5100-9858) universes=[32, ..., 63]
controller3: 192.168.1.47 (10100-14858) universes=[64, ..., 95]
controller4: 192.168.1.48 (15100-19858) universes=[96, ..., 127]
```

## Lien avec la config réelle
- La structure du fichier `config/config.json` est directement issue du fichier Excel `/asset-execices/Ecran.xlsx`.
- Chaque contrôleur, plage d'entités et univers ArtNet correspond à la réalité de l'écran utilisé pour l'exercice et les tests.

---

## Prochaine étape
Intégrer le ConfigManager dans le pipeline principal (main.py) et l'utiliser pour initialiser le routeur, le mapping, etc. 