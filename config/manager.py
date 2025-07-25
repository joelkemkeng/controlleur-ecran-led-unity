import json
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class ControllerConfig:
    """
    Représente la configuration d'un contrôleur LED (ex : BC216).
    Args:
        ip (str): Adresse IP du contrôleur
        start_entity (int): ID de la première entité gérée
        end_entity (int): ID de la dernière entité gérée
        universes (List[int]): Liste des univers ArtNet gérés
    """
    ip: str
    start_entity: int
    end_entity: int
    universes: List[int]

@dataclass
class SystemConfig:
    """
    Représente la configuration système globale du routeur LED.
    Args:
        listen_port (int): Port UDP d'écoute
        ehub_universe (int): Univers eHuB cible
        max_fps (int): Limite de fréquence d'envoi
        controllers (Dict[str, ControllerConfig]): Dictionnaire des contrôleurs
    """
    listen_port: int
    ehub_universe: int
    max_fps: int
    controllers: Dict[str, ControllerConfig] = field(default_factory=dict)

class ConfigManager:
    """
    Gestionnaire de configuration pour le routeur LED.
    Permet de charger, sauvegarder et générer une configuration système complète.

    Exemple d'utilisation :
        config_mgr = ConfigManager("config.json")
        print(config_mgr.config.listen_port)
        for name, ctrl in config_mgr.config.controllers.items():
            print(f"{name}: {ctrl.ip} ({ctrl.start_entity}-{ctrl.end_entity})")
    """
    def __init__(self, config_file: str = "config/config.json"):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self) -> SystemConfig:
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                #verifier si les donnee sont bien presente dans data
                if not all(key in data for key in ['listen_port', 'ehub_universe', 'max_fps', 'controllers']):
                    print(f"\n\n\n\n\n\n DEBUG [data_config_reseau_ehub_primaire_file_config] : Fichier de configuration invalide ou manquant : {self.config_file}")
                    raise ValueError("Données de configuration manquantes")
                
                print(f"\n\n\n\n\n\n DEBUG [data_config_reseau_ehub_primaire_file_config] : Données configuration recuperer dans le fichier de configuration :: \n - data_port: {data['listen_port']} \n - data_universe: {data['ehub_universe']}, \n - data: {data}")
                controllers = {
                    name: ControllerConfig(**ctrl)
                    for name, ctrl in data['controllers'].items()
                }
                
                
                return SystemConfig(
                    listen_port=data['listen_port'],
                    ehub_universe=data['ehub_universe'],
                    max_fps=data['max_fps'],
                    controllers=controllers
                )
        except FileNotFoundError:
            return self.create_default_config()

    def create_default_config(self) -> SystemConfig:
        # Exemple de config par défaut pour un contrôleur
        controllers = {
            "controller1": ControllerConfig(
                ip="192.168.1.45",
                start_entity=100,
                end_entity=4858,
                universes=list(range(0, 32))
            )
        }
        return SystemConfig(
            listen_port=8765,
            ehub_universe=0,
            max_fps=40,
            controllers=controllers
        ) 