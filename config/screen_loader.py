"""
Module de chargement de configuration écran depuis Ecran.xlsx
Simple, bien commenté, avec debug prints
"""

import pandas as pd
from dataclasses import dataclass
from typing import List, Dict
import os

@dataclass
class LEDMapping:
    """
    Représente un mapping LED simple
    """
    entity_id: int          # ID entité (ex: 100)
    controller_ip: str      # IP contrôleur (ex: 192.168.1.45)
    universe: int          # Univers DMX (ex: 0) 
    channel: int           # Canal DMX (ex: 1)

class ScreenConfigLoader:
    """
    Chargeur de configuration écran depuis Ecran.xlsx
    Garde les choses simples et testables
    """
    
    def __init__(self, excel_file: str = "Ducu-porject/asset-execices/Ecran.xlsx"):
        self.excel_file = excel_file
        self.mappings: List[LEDMapping] = []
        self.controllers: Dict[str, int] = {}  # IP -> nombre d'entités
        
        print(f"🔧 [ScreenConfig] Initialisation du chargeur config écran")
        print(f"📁 [ScreenConfig] Fichier Excel: {excel_file}")
        
    def load_config(self) -> bool:
        """
        Charge la configuration depuis Excel
        Retourne True si succès, False sinon
        """
        try:
            print(f"📖 [ScreenConfig] Lecture du fichier Excel...")
            
            # Vérifier que le fichier existe
            if not os.path.exists(self.excel_file):
                print(f"❌ [ScreenConfig] ERREUR: Fichier non trouvé: {self.excel_file}")
                return False
            
            # Lire le fichier Excel
            df = pd.read_excel(self.excel_file)
            print(f"✅ [ScreenConfig] Fichier lu: {len(df)} lignes trouvées")
            
            # Afficher les colonnes pour debug
            print(f"🔍 [ScreenConfig] Colonnes: {list(df.columns)}")
            print(f"🔍 [ScreenConfig] Aperçu des données:")
            print(df.head(3))
            
            # Parser les données
            self._parse_mappings(df)
            self._analyze_controllers()
            
            print(f"✅ [ScreenConfig] Configuration chargée avec succès!")
            return True
            
        except Exception as e:
            print(f"❌ [ScreenConfig] ERREUR lors du chargement: {e}")
            return False
    
    def _parse_mappings(self, df: pd.DataFrame):
        """
        Parse les mappings depuis le DataFrame
        Colonnes: Name, Entity Start, Entity End, ArtNet IP, ArtNet Universe
        ATTENTION: Les écarts entre univers ne sont pas fixes !
        """
        print(f"🔄 [ScreenConfig] Parsing des mappings...")
        
        self.mappings = []
        
        for index, row in df.iterrows():
            try:
                # Utiliser les vraies colonnes du fichier Excel
                entity_start = int(row['Entity Start'])
                entity_end = int(row['Entity End'])
                controller_ip = str(row['ArtNet IP'])
                universe = int(row['ArtNet Universe'])
                
                # Calculer le nombre d'entités dans cette plage
                entity_count = entity_end - entity_start + 1
                
                # Créer un mapping pour chaque entité dans la plage
                for i, entity_id in enumerate(range(entity_start, entity_end + 1)):
                    # Canal DMX relatif dans l'univers (commence à 1)
                    channel = i + 1
                    
                    mapping = LEDMapping(
                        entity_id=entity_id,
                        controller_ip=controller_ip,
                        universe=universe,
                        channel=channel
                    )
                    self.mappings.append(mapping)
                
                # Debug pour les premières lignes avec info détaillée
                if index < 5:
                    print(f"🗺️  [ScreenConfig] Ligne {index}: {entity_start}-{entity_end} ({entity_count} entités) → {controller_ip}:u{universe}")
                    if index == 0:
                        print(f"   📍 Premier mapping: Entité {entity_start} → canal 1")
                        print(f"   📍 Dernier mapping: Entité {entity_end} → canal {entity_count}")
                    
            except Exception as e:
                print(f"⚠️  [ScreenConfig] Erreur ligne {index}: {e}")
        
        print(f"✅ [ScreenConfig] {len(self.mappings)} mappings créés")
    
    def _analyze_controllers(self):
        """
        Analyse les contrôleurs détectés
        """
        print(f"🔍 [ScreenConfig] Analyse des contrôleurs...")
        
        self.controllers = {}
        
        for mapping in self.mappings:
            ip = mapping.controller_ip
            if ip not in self.controllers:
                self.controllers[ip] = 0
            self.controllers[ip] += 1
        
        print(f"🎮 [ScreenConfig] Contrôleurs détectés:")
        for ip, count in self.controllers.items():
            print(f"   • {ip}: {count} entités")
        
        print(f"✅ [ScreenConfig] {len(self.controllers)} contrôleurs trouvés")
    
    def get_mapping_for_entity(self, entity_id: int) -> LEDMapping:
        """
        Retourne le mapping pour une entité donnée
        """
        for mapping in self.mappings:
            if mapping.entity_id == entity_id:
                return mapping
        return None
    
    def print_summary(self):
        """
        Affiche un résumé de la configuration
        """
        print(f"\n📊 [ScreenConfig] === RÉSUMÉ CONFIGURATION ===")
        print(f"📁 Fichier: {self.excel_file}")
        print(f"🗺️  Mappings totaux: {len(self.mappings)}")
        print(f"🎮 Contrôleurs: {len(self.controllers)}")
        
        if self.mappings:
            first = self.mappings[0]
            last = self.mappings[-1]
            print(f"🔢 Plage entités: {first.entity_id} → {last.entity_id}")
        
        print(f"=============================================\n")

# Test simple si exécuté directement
if __name__ == "__main__":
    print("🧪 [TEST] Test du chargeur de configuration")
    
    loader = ScreenConfigLoader()
    success = loader.load_config()
    
    if success:
        loader.print_summary()
        
        # Test mapping entité 100
        mapping = loader.get_mapping_for_entity(100)
        if mapping:
            print(f"🧪 [TEST] Entité 100 → {mapping.controller_ip}:{mapping.universe}:{mapping.channel}")
        else:
            print(f"🧪 [TEST] Entité 100 non trouvée")
    else:
        print("❌ [TEST] Échec du chargement")
