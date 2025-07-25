"""
config/advanced_config.py - Gestionnaire de configuration avancée pour le routeur LED

Ce module fournit la classe AdvancedConfigManager, qui permet de gérer des configurations complexes
(multi-contrôleurs, plages d'entités, univers, validation, export Excel) pour des installations LED professionnelles.

Portabilité :
- Fonctionne sur Linux, Mac, Windows, Raspbian
- Nécessite pandas pour l'export Excel (pip install pandas openpyxl)

Exemple d'utilisation :
----------------------
from config.advanced_config import AdvancedConfigManager
mgr = AdvancedConfigManager()
config = mgr.create_mur_led_config()
assert mgr.validate_config(config)
mgr.export_excel_template('template_mapping.xlsx', config)

Explication pédagogique :
------------------------
- Permet de décrire toute l'installation (plusieurs contrôleurs, plages d'entités, univers)
- Vérifie la cohérence (pas de chevauchement d'entités)
- Génère un fichier Excel pour documenter ou préparer le mapping
"""

import pandas as pd
from config.manager import ConfigManager, ControllerConfig, SystemConfig

class AdvancedConfigManager(ConfigManager):
    """
    Gestionnaire de configuration avancée pour le routeur LED.
    Permet de créer, valider et exporter des configurations complexes (multi-contrôleurs).
    """
    def create_mur_led_config(self) -> SystemConfig:
        """
        Génère une configuration complète pour un mur LED 128x128 (4 contrôleurs, plages d'entités, univers).
        Retourne un objet SystemConfig prêt à être utilisé.
        """
        return SystemConfig(
            listen_port=8765,
            ehub_universe=1,
            max_fps=40,
            controllers={
                "controller1": ControllerConfig(
                    ip="192.168.1.45",
                    start_entity=100,
                    end_entity=4858,
                    universes=list(range(0, 32))
                ),
                "controller2": ControllerConfig(
                    ip="192.168.1.46",
                    start_entity=5100,
                    end_entity=9858,
                    universes=list(range(32, 64))
                ),
                "controller3": ControllerConfig(
                    ip="192.168.1.47",
                    start_entity=10100,
                    end_entity=14858,
                    universes=list(range(64, 96))
                ),
                "controller4": ControllerConfig(
                    ip="192.168.1.48",
                    start_entity=15100,
                    end_entity=19858,
                    universes=list(range(96, 128))
                )
            }
        )

    def validate_config(self, config: SystemConfig = None) -> bool:
        """
        Valide la cohérence de la configuration (pas de chevauchement d'entités entre contrôleurs).
        Retourne True si la config est cohérente, False sinon.
        """
        if config is None:
            config = self.config
        entity_ranges = []
        for ctrl in config.controllers.values():
            entity_ranges.append((ctrl.start_entity, ctrl.end_entity))
        entity_ranges.sort()
        for i in range(len(entity_ranges) - 1):
            if entity_ranges[i][1] >= entity_ranges[i+1][0]:
                print(f"Erreur: Chevauchement d'entités entre {entity_ranges[i]} et {entity_ranges[i+1]}")
                return False
        return True

    def export_excel_template(self, filepath: str, config: SystemConfig = None):
        """
        Exporte un template Excel du mapping entités → contrôleurs/univers/canaux.
        Args:
            filepath (str): Chemin du fichier Excel à générer
            config (SystemConfig, optionnel): Config à exporter (défaut : self.config)
        """
        if config is None:
            config = self.config
        data = []
        for name, ctrl in config.controllers.items():
            for entity_id in range(ctrl.start_entity, min(ctrl.start_entity + 10, ctrl.end_entity + 1)):
                data.append({
                    'Entity_ID': entity_id,
                    'Controller_IP': ctrl.ip,
                    'Controller_Name': name,
                    'Universe': ctrl.universes[0],
                    'Start_Channel': ((entity_id - ctrl.start_entity) * 3) + 1,
                    'Channels': 'RGB'
                })
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False)
        print(f"Template Excel exporté : {filepath}") 