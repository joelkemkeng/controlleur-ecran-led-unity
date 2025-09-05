#!/usr/bin/env python3
"""
🎭 ÉTAPE 3 - Pipeline eHub → Mapping DMX
Concentré uniquement sur le mapping des entités eHuB vers structure DMX
Base sur l'étape 2 validée + logique des tests fonctionnels
"""

import sys
import time
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import os
from pathlib import Path

# Import du pipeline étape 2 validé (Windows compatible)
current_dir = Path(__file__).parent
etape2_path = current_dir.parent / "etape-02-decodage-ehub"
sys.path.insert(0, str(etape2_path))
from ehub_complete_pipeline_decoder import EHubDecoder, EHubEntity, EHubPacket

@dataclass
class DMXUniverse:
    """
    Représente un univers DMX de 512 canaux
    """
    universe_id: int
    controller_ip: str
    dmx_data: bytearray  # 512 bytes
    
    def __post_init__(self):
        if not self.dmx_data:
            self.dmx_data = bytearray(512)  # Initialiser à zéro
    
    def set_rgb(self, channel_start: int, r: int, g: int, b: int):
        """Définit les valeurs RGB à partir du canal spécifié"""
        if channel_start + 2 < 512:
            self.dmx_data[channel_start] = r
            self.dmx_data[channel_start + 1] = g
            self.dmx_data[channel_start + 2] = b
    
    def clear(self):
        """Remet tous les canaux à zéro"""
        self.dmx_data = bytearray(512)

@dataclass 
class LEDMapping:
    """
    Mapping d'une entité eHuB vers position DMX
    """
    entity_id: int
    controller_ip: str
    universe: int
    channel_start: int  # Canal de début (0-511)
    
    def __str__(self):
        return f"Entity {self.entity_id} → {self.controller_ip}:u{self.universe}:ch{self.channel_start}"

class DMXMapper:
    """
    Mapper qui convertit les entités eHuB en structure DMX
    Base sur la configuration Excel et la logique des tests fonctionnels
    """
    
    def __init__(self):
        print("🎭 [DMXMapper] Initialisation du mapper DMX")
        self.mappings: Dict[int, LEDMapping] = {}  # entity_id → LEDMapping
        self.universes: Dict[Tuple[str, int], DMXUniverse] = {}  # (ip, universe) → DMXUniverse
        self.controller_stats: Dict[str, int] = {}  # Statistiques par contrôleur
    
    def load_mappings_from_config(self, screen_config) -> bool:
        """
        Charge les mappings depuis la configuration écran (étape 2)
        """
        if not screen_config or not screen_config.mappings:
            print("❌ [DMXMapper] Pas de configuration écran disponible")
            return False
        
        print(f"🔄 [DMXMapper] Chargement {len(screen_config.mappings)} mappings...")
        
        # Convertir les mappings de l'étape 2 en mappings DMX
        for mapping in screen_config.mappings:
            led_mapping = LEDMapping(
                entity_id=mapping.entity_id,
                controller_ip=mapping.controller_ip,
                universe=mapping.universe,
                channel_start=(mapping.channel - 1) * 3  # Canal DMX commence à 0, multiplié par 3 pour RGB
            )
            
            self.mappings[mapping.entity_id] = led_mapping
            
            # Initialiser l'univers s'il n'existe pas
            universe_key = (mapping.controller_ip, mapping.universe)
            if universe_key not in self.universes:
                self.universes[universe_key] = DMXUniverse(
                    universe_id=mapping.universe,
                    controller_ip=mapping.controller_ip,
                    dmx_data=bytearray(512)
                )
            
            # Statistiques
            if mapping.controller_ip not in self.controller_stats:
                self.controller_stats[mapping.controller_ip] = 0
            self.controller_stats[mapping.controller_ip] += 1
        
        print(f"✅ [DMXMapper] {len(self.mappings)} mappings chargés")
        print(f"🌍 [DMXMapper] {len(self.universes)} univers DMX créés")
        print(f"🎮 [DMXMapper] Contrôleurs:")
        for ip, count in self.controller_stats.items():
            print(f"   • {ip}: {count} entités")
        
        return True
    
    def map_entities_to_dmx(self, entities: List[EHubEntity]) -> Dict[Tuple[str, int], DMXUniverse]:
        """
        Mappe une liste d'entités eHuB vers les univers DMX
        Retourne les univers modifiés
        """
        if not entities:
            return {}
        
        modified_universes = {}
        mapped_count = 0
        unmapped_count = 0
        
        print(f"🔄 [DMXMapper] Mapping {len(entities)} entités vers DMX...")
        
        for entity in entities:
            if entity.entity_id in self.mappings:
                mapping = self.mappings[entity.entity_id]
                universe_key = (mapping.controller_ip, mapping.universe)
                
                # Récupérer ou créer l'univers
                if universe_key in self.universes:
                    universe = self.universes[universe_key]
                    
                    # Appliquer les valeurs RGB
                    universe.set_rgb(
                        mapping.channel_start,
                        entity.red, entity.green, entity.blue
                    )
                    
                    # Marquer comme modifié
                    modified_universes[universe_key] = universe
                    mapped_count += 1
                    
                    # Debug pour les premières entités
                    if mapped_count <= 3:
                        print(f"   🎨 {mapping} → RGB({entity.red},{entity.green},{entity.blue})")
                else:
                    print(f"⚠️ [DMXMapper] Univers introuvable: {universe_key}")
                    unmapped_count += 1
            else:
                unmapped_count += 1
        
        print(f"✅ [DMXMapper] Mapping terminé: {mapped_count} mappées, {unmapped_count} ignorées")
        return modified_universes
    
    def get_universe_summary(self) -> Dict[str, List[int]]:
        """
        Retourne un résumé des univers par contrôleur
        """
        summary = {}
        for (ip, universe_id), universe in self.universes.items():
            if ip not in summary:
                summary[ip] = []
            summary[ip].append(universe_id)
        
        # Trier les univers
        for ip in summary:
            summary[ip].sort()
        
        return summary
    
    def clear_all_universes(self):
        """
        Remet tous les univers à zéro (éteint tout)
        """
        print("🔌 [DMXMapper] Remise à zéro de tous les univers")
        for universe in self.universes.values():
            universe.clear()

class EHubDMXPipeline(EHubDecoder):
    """
    Pipeline étape 3: eHub → Mapping DMX
    Hérite de l'étape 2 et ajoute le mapping DMX
    """
    
    def __init__(self, port: int = 8765):  # Port Unity standard
        print("🎭 [EHubDMXPipeline] Initialisation pipeline eHub→DMX")
        print(f"📡 [EHubDMXPipeline] Port Unity: {port}")
        super().__init__(port)
        self.dmx_mapper: Optional[DMXMapper] = None
        self.total_mapped_packets = 0
        self.total_mapped_entities = 0
    
    def initialize(self) -> bool:
        """
        Initialise le pipeline complet
        """
        print("🚀 [EHubDMXPipeline] Initialisation pipeline DMX...")
        
        # Initialiser l'étape 2 (réception + décodage)
        if not super().initialize():
            print("❌ [EHubDMXPipeline] Échec initialisation étape 2")
            return False
        
        # Initialiser le mapper DMX
        print("🎭 [EHubDMXPipeline] Initialisation mapper DMX...")
        self.dmx_mapper = DMXMapper()
        
        if not self.dmx_mapper.load_mappings_from_config(self.screen_config):
            print("❌ [EHubDMXPipeline] Échec chargement mappings DMX")
            return False
        
        print("🎉 [EHubDMXPipeline] Pipeline DMX initialisé!")
        return True
    
    def process_ehub_packet(self, packet: EHubPacket) -> Optional[Dict[Tuple[str, int], DMXUniverse]]:
        """
        Traite un paquet eHuB et retourne les univers DMX modifiés
        """
        if not self.dmx_mapper:
            print("⚠️ [EHubDMXPipeline] Mapper DMX non initialisé")
            return None
        
        # Mapper vers DMX
        modified_universes = self.dmx_mapper.map_entities_to_dmx(packet.entities)
        
        if modified_universes:
            self.total_mapped_packets += 1
            self.total_mapped_entities += len([e for e in packet.entities if e.entity_id in self.dmx_mapper.mappings])
            
            print(f"🎭 [EHubDMXPipeline] Paquet traité: {len(modified_universes)} univers modifiés")
        
        return modified_universes
    
    def process_packet(self, packet: EHubPacket):
        """
        Override de l'étape 2 : traite le paquet et effectue le mapping DMX
        """
        # Traitement de base de l'étape 2
        super().process_packet(packet)
        
        # Ajout du mapping DMX
        modified_universes = self.process_ehub_packet(packet)
        if modified_universes:
            print(f"📊 [EHubDMXPipeline] {len(modified_universes)} univers mis à jour:")
            for (ip, universe_id), universe in modified_universes.items():
                # Calculer activité dans l'univers
                active_channels = sum(1 for b in universe.dmx_data if b > 0)
                print(f"   🌍 {ip}:u{universe_id} → {active_channels}/512 canaux actifs")
    
    def run_test_mapping(self, test_duration: float = 10.0):
        """
        Lance un test du mapping pendant une durée donnée
        """
        print(f"🧪 [EHubDMXPipeline] Test mapping pendant {test_duration}s...")
        print("💡 [EHubDMXPipeline] Envoyez des données eHuB pour voir le mapping")
        print("📡 [EHubDMXPipeline] En écoute sur 172.26.223.135:8765 (port Unity)")
        print("🎮 [EHubDMXPipeline] Unity doit envoyer vers ce port pour eHuB")
        
        # Utiliser la méthode de l'étape 2 avec un timeout
        import signal
        import sys
        
        def timeout_handler(signum, frame):
            print(f"\n⏰ [EHubDMXPipeline] Timeout de {test_duration}s atteint")
            raise KeyboardInterrupt()
        
        # Configurer l'alarme
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(test_duration))
        
        try:
            # Utiliser la méthode éprouvée de l'étape 2
            self.listen_and_decode()
        except KeyboardInterrupt:
            print("\n🛑 [EHubDMXPipeline] Test interrompu")
        finally:
            signal.alarm(0)  # Annuler l'alarme
        
        self.print_mapping_stats()
    
    def print_mapping_stats(self):
        """
        Affiche les statistiques de mapping
        """
        print("\n📊 [EHubDMXPipeline] === STATISTIQUES MAPPING ===")
        print(f"📦 Paquets mappés: {self.total_mapped_packets}")
        print(f"🎨 Entités mappées: {self.total_mapped_entities}")
        
        if self.dmx_mapper:
            universe_summary = self.dmx_mapper.get_universe_summary()
            print(f"🌍 Univers par contrôleur:")
            for ip, universes in universe_summary.items():
                print(f"   • {ip}: {len(universes)} univers ({min(universes)}-{max(universes)})")
        
        print("================================================")

def main():
    """
    Programme principal pour tester l'étape 3
    """
    print("🎭 === ÉTAPE 3 : PIPELINE eHub → MAPPING DMX ===")
    print("🎯 Focus: Conversion entités eHuB vers structure DMX")
    print()
    
    # Créer pipeline étape 3
    pipeline = EHubDMXPipeline(port=8765)  # Port Unity standard
    
    try:
        # Initialiser
        if not pipeline.initialize():
            print("❌ Échec initialisation")
            return False
        
        print("✅ Pipeline DMX prêt!")
        print()
        
        # Lancer test
        pipeline.run_test_mapping(30.0)
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    finally:
        pipeline.stop()
        print("🔌 Pipeline arrêté")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
