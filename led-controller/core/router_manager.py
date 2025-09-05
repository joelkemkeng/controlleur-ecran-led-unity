import json
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class RouterConfig:
    """Configuration d'un routeur LED"""
    name: str
    ip: str
    enabled: bool
    port: int = 6454
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "ip": self.ip,
            "enabled": self.enabled,
            "port": self.port
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RouterConfig':
        return cls(
            name=data.get("name", "Routeur"),
            ip=data.get("ip", "192.168.1.1"),
            enabled=data.get("enabled", False),
            port=data.get("port", 6454)
        )

class RouterManager:
    """Gestionnaire de configuration des routeurs LED"""
    
    def __init__(self, config_file: str = "router_config.json"):
        self.config_file = config_file
        self.routers: List[RouterConfig] = []
        self.load_config()
    
    def load_config(self) -> bool:
        """Charge la configuration depuis le fichier JSON"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.routers = [RouterConfig.from_dict(router) for router in data.get("routers", [])]
            else:
                # Configuration par défaut
                self.routers = [
                    RouterConfig("Routeur 1", "192.168.1.45", True),
                    RouterConfig("Routeur 2", "192.168.1.46", True),
                    RouterConfig("Routeur 3", "192.168.1.47", True),
                    RouterConfig("Routeur 4", "192.168.1.48", True)
                ]
                self.save_config()
            return True
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration: {e}")
            # Configuration de secours
            self.routers = [
                RouterConfig("Routeur 1", "192.168.1.45", True),
                RouterConfig("Routeur 2", "192.168.1.46", True),
                RouterConfig("Routeur 3", "192.168.1.47", True),
                RouterConfig("Routeur 4", "192.168.1.48", True)
            ]
            return False
    
    def reset_to_default(self) -> bool:
        """Réinitialise la configuration aux valeurs par défaut"""
        self.routers = [
            RouterConfig("Routeur 1", "192.168.1.45", True),
            RouterConfig("Routeur 2", "192.168.1.46", True),
            RouterConfig("Routeur 3", "192.168.1.47", True),
            RouterConfig("Routeur 4", "192.168.1.48", True)
        ]
        return self.save_config()
    
    def save_config(self) -> bool:
        """Sauvegarde la configuration dans le fichier JSON"""
        try:
            data = {
                "routers": [router.to_dict() for router in self.routers]
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la configuration: {e}")
            return False
    
    def get_enabled_routers(self) -> List[Tuple[str, int]]:
        """Retourne la liste des routeurs activés avec leurs IPs et ports"""
        return [(router.ip, router.port) for router in self.routers if router.enabled]
    
    def update_router(self, index: int, name: str, ip: str, enabled: bool, port: int = 6454) -> bool:
        """Met à jour la configuration d'un routeur"""
        if 0 <= index < len(self.routers):
            self.routers[index] = RouterConfig(name, ip, enabled, port)
            return self.save_config()
        return False
    
    def add_router(self, name: str = None, ip: str = "192.168.1.1", enabled: bool = True, port: int = 6454) -> bool:
        """Ajoute un nouveau routeur"""
        if name is None:
            name = f"Routeur {len(self.routers) + 1}"
        
        # Générer une IP unique si nécessaire
        if ip == "192.168.1.1":
            used_ips = {router.ip for router in self.routers}
            base_ip = "192.168.1."
            for i in range(1, 255):
                candidate_ip = f"{base_ip}{i}"
                if candidate_ip not in used_ips:
                    ip = candidate_ip
                    break
        
        new_router = RouterConfig(name, ip, enabled, port)
        self.routers.append(new_router)
        return self.save_config()
    
    def remove_router(self, index: int) -> bool:
        """Supprime un routeur"""
        if 0 <= index < len(self.routers):
            del self.routers[index]
            return self.save_config()
        return False
    
    def move_router(self, from_index: int, to_index: int) -> bool:
        """Déplace un routeur d'une position à une autre"""
        if 0 <= from_index < len(self.routers) and 0 <= to_index < len(self.routers):
            router = self.routers.pop(from_index)
            self.routers.insert(to_index, router)
            return self.save_config()
        return False
    
    def get_router_count(self) -> int:
        """Retourne le nombre total de routeurs"""
        return len(self.routers)
    
    def get_enabled_count(self) -> int:
        """Retourne le nombre de routeurs activés"""
        return sum(1 for router in self.routers if router.enabled)
    
    def validate_ip(self, ip: str) -> bool:
        """Valide une adresse IP"""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                if not 0 <= int(part) <= 255:
                    return False
            return True
        except:
            return False
    
    def get_mapping_info(self) -> Dict:
        """Retourne les informations de mapping pour l'affichage"""
        enabled_routers = self.get_enabled_routers()
        total_bands = len(enabled_routers) * 16  # 16 bandes par routeur
        
        return {
            "enabled_routers": enabled_routers,
            "total_bands": total_bands,
            "bands_per_router": 16,
            "router_count": len(enabled_routers)
        } 