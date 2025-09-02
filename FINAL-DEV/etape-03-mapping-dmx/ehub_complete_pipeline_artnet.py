#!/usr/bin/env python3
"""
🎭 ÉTAPE 3 : Pipeline Complet eHub → ArtNet/DMX
Extension du décodeur eHub avec envoi ArtNet vers contrôleurs BC216

Architecture:
Unity → eHub → Décodage → Mapping → ArtNet → Contrôleurs BC216

Ce module étend ehub_complete_pipeline_decoder.py en ajoutant:
- Génération de paquets ArtNet
- Envoi vers contrôleurs BC216 (192.168.1.45-48)
- Gestion des univers DMX512
- Optimisations de performance temps réel
"""

import sys
import time
import threading
import socket
import struct
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

# Import du pipeline étape 2
sys.path.append('/home/joel/projet_ecran/controlleur-ecran-led-unity/FINAL-DEV/etape-02-decodage-ehub')
from ehub_complete_pipeline_decoder import (
    EHubDecoder, EHubEntity, EHubPacket
)

@dataclass
class LEDMapping:
    """
    Mapping LED vers DMX Channel
    """
    led_x: int
    led_y: int
    controller_ip: str
    universe: int
    channel_r: int
    channel_g: int
    channel_b: int

@dataclass
class ArtNetPacket:
    """
    Paquet ArtNet DMX512 pour BC216
    """
    universe: int
    data: bytes  # 512 bytes de données DMX
    
@dataclass
class DMXChannel:
    """
    Canal DMX avec valeurs RGB
    """
    channel: int
    red: int
    green: int 
    blue: int

@dataclass
class ControllerState:
    """
    État d'un contrôleur BC216
    """
    ip: str
    universes: Dict[int, bytes]  # universe_id -> dmx_data[512]
    last_update: float
    packet_count: int

class ArtNetSender:
    """
    Générateur et envoyeur de paquets ArtNet
    """
    
    def __init__(self):
        self.socket = None
        self.sent_packets = 0
        self.sent_bytes = 0
        
    def initialize(self) -> bool:
        """
        Initialise le socket ArtNet
        """
        try:
            print("🎭 [ArtNetSender] Initialisation sender ArtNet...")
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            print("✅ [ArtNetSender] Socket ArtNet créé")
            return True
            
        except Exception as e:
            print(f"❌ [ArtNetSender] Erreur initialisation: {e}")
            return False
    
    def create_artnet_packet(self, universe: int, dmx_data: bytes) -> bytes:
        """
        Crée un paquet ArtNet DMX512
        Format ArtNet: Header(18) + DMX_Data(512) = 530 bytes
        """
        # Header ArtNet selon spécification
        header = bytearray(18)
        
        # Signature "Art-Net\0"
        header[0:8] = b"Art-Net\0"
        
        # OpCode DMX (0x5000 en little-endian)
        header[8:10] = struct.pack('<H', 0x5000)
        
        # Protocol version (14)
        header[10:12] = struct.pack('>H', 14)
        
        # Sequence (0)
        header[12] = 0
        
        # Physical port (0)
        header[13] = 0
        
        # Universe (2 bytes little-endian)
        header[14:16] = struct.pack('<H', universe)
        
        # Data length (512 en big-endian)
        header[16:18] = struct.pack('>H', 512)
        
        # Compléter DMX data à 512 bytes si nécessaire
        dmx_512 = dmx_data[:512].ljust(512, b'\x00')
        
        return bytes(header) + dmx_512
    
    def send_to_controller(self, controller_ip: str, universe: int, dmx_data: bytes) -> bool:
        """
        Envoie un paquet ArtNet à un contrôleur BC216
        """
        try:
            if not self.socket:
                return False
            
            # Créer paquet ArtNet
            artnet_packet = self.create_artnet_packet(universe, dmx_data)
            
            # Envoyer vers contrôleur (port ArtNet standard 6454)
            self.socket.sendto(artnet_packet, (controller_ip, 6454))
            
            # Stats
            self.sent_packets += 1
            self.sent_bytes += len(artnet_packet)
            
            return True
            
        except Exception as e:
            print(f"❌ [ArtNetSender] Erreur envoi {controller_ip}:u{universe}: {e}")
            return False
    
    def close(self):
        """
        Ferme le socket ArtNet
        """
        if self.socket:
            self.socket.close()
            self.socket = None
            print("🔌 [ArtNetSender] Socket fermé")

class EHubArtNetPipeline(EHubDecoder):
    """
    Pipeline complet eHub → ArtNet
    Étend EHubDecoder avec capacités ArtNet
    """
    
    def __init__(self, port: int = 8765):
        super().__init__(port)
        
        # Composants ArtNet
        self.artnet_sender = ArtNetSender()
        
        # État des contrôleurs
        self.controllers: Dict[str, ControllerState] = {}
        
        # Buffers DMX par contrôleur/univers
        self.dmx_buffers: Dict[Tuple[str, int], bytearray] = {}
        
        # Stats
        self.processed_entities = 0
        self.sent_universes = 0
        self.artnet_errors = 0
        
        print("🎭 [EHubArtNetPipeline] Initialisation pipeline eHub→ArtNet")
    
    def initialize(self) -> bool:
        """
        Initialise le pipeline complet
        """
        print("🚀 [EHubArtNetPipeline] Initialisation pipeline complet...")
        
        # 1. Initialiser le décodeur eHub (étape 2)
        if not super().initialize():
            print("❌ [EHubArtNetPipeline] Échec initialisation décodeur eHub")
            return False
        
        # 2. Initialiser ArtNet sender
        if not self.artnet_sender.initialize():
            print("❌ [EHubArtNetPipeline] Échec initialisation ArtNet")
            return False
        
        # 3. Initialiser les contrôleurs
        self._initialize_controllers()
        
        print("🎉 [EHubArtNetPipeline] Pipeline complet initialisé!")
        return True
    
    def _initialize_controllers(self):
        """
        Initialise l'état des contrôleurs BC216
        """
        print("🎮 [EHubArtNetPipeline] Initialisation contrôleurs BC216...")
        
        if not self.screen_config:
            print("⚠️ [EHubArtNetPipeline] Pas de config écran")
            return
        
        # Découvrir les contrôleurs depuis la config
        for mapping in self.screen_config.mappings:
            controller_ip = mapping.controller_ip
            
            if controller_ip not in self.controllers:
                self.controllers[controller_ip] = ControllerState(
                    ip=controller_ip,
                    universes={},
                    last_update=0,
                    packet_count=0
                )
                
                # Initialiser les buffers DMX pour chaque univers
                for universe in range(128):  # BC216 supporte jusqu'à 128 univers
                    buffer_key = (controller_ip, universe)
                    self.dmx_buffers[buffer_key] = bytearray(512)  # Buffer DMX512
        
        print(f"🎮 [EHubArtNetPipeline] {len(self.controllers)} contrôleurs initialisés:")
        for ip in self.controllers:
            print(f"   • {ip}")
    
    def process_packet(self, packet: EHubPacket):
        """
        Traite un paquet eHub décodé et génère ArtNet
        """
        print(f"🔄 [EHubArtNetPipeline] Traitement paquet: {len(packet.entities)} entités")
        
        # Grouper les entités par contrôleur/univers
        updates_by_controller = defaultdict(lambda: defaultdict(list))
        
        for entity in packet.entities:
            # Obtenir le mapping LED
            mapping = self.get_led_mapping(entity.entity_id)
            if not mapping:
                continue  # Entité non mappée
            
            # Grouper par contrôleur et univers
            controller_ip = mapping.controller_ip
            universe = mapping.universe
            
            updates_by_controller[controller_ip][universe].append((entity, mapping))
            self.processed_entities += 1
        
        # Générer et envoyer ArtNet pour chaque contrôleur/univers
        for controller_ip, universes in updates_by_controller.items():
            for universe, entity_mappings in universes.items():
                self._update_dmx_universe(controller_ip, universe, entity_mappings)
                self._send_artnet_universe(controller_ip, universe)
    
    def _update_dmx_universe(self, controller_ip: str, universe: int, entity_mappings: List[Tuple[EHubEntity, LEDMapping]]):
        """
        Met à jour un univers DMX avec les nouvelles valeurs
        """
        buffer_key = (controller_ip, universe)
        dmx_buffer = self.dmx_buffers.get(buffer_key)
        
        if dmx_buffer is None:
            print(f"⚠️ [EHubArtNetPipeline] Buffer DMX non trouvé: {controller_ip}:u{universe}")
            return
        
        # Mettre à jour les canaux DMX
        for entity, mapping in entity_mappings:
            channel_start = mapping.channel
            
            # Vérifier limites DMX512 (canaux 1-512)
            if channel_start < 1 or channel_start + 2 > 512:
                continue
            
            # Écrire RGB dans le buffer DMX (canaux consécutifs)
            dmx_buffer[channel_start - 1] = entity.red    # Canal R
            dmx_buffer[channel_start] = entity.green      # Canal G  
            dmx_buffer[channel_start + 1] = entity.blue   # Canal B
            # Note: W (white) ignoré pour l'instant, pourrait être canal+3
    
    def _send_artnet_universe(self, controller_ip: str, universe: int):
        """
        Envoie un univers DMX via ArtNet
        """
        buffer_key = (controller_ip, universe)
        dmx_buffer = self.dmx_buffers.get(buffer_key)
        
        if dmx_buffer is None:
            return
        
        # Envoyer vers contrôleur
        success = self.artnet_sender.send_to_controller(
            controller_ip, 
            universe, 
            bytes(dmx_buffer)
        )
        
        if success:
            self.sent_universes += 1
            
            # Mettre à jour stats contrôleur
            if controller_ip in self.controllers:
                controller = self.controllers[controller_ip]
                controller.last_update = time.time()
                controller.packet_count += 1
        else:
            self.artnet_errors += 1
    
    def run_continuous(self):
        """
        Mode continu: Réception → Décodage → ArtNet
        """
        print("🚀 [EHubArtNetPipeline] Démarrage mode continu eHub→ArtNet")
        print("📡 En attente des données Unity...")
        print("🎭 Les paquets ArtNet seront envoyés vers les contrôleurs BC216")
        print("💡 Appuyez Ctrl+C pour arrêter")
        print("-" * 60)
        
        packet_count = 0
        stats_interval = 100  # Afficher stats tous les 100 paquets
        
        try:
            while True:
                # Recevoir message UDP
                message = self.receiver.receive_message(timeout=1.0)
                
                if message:
                    # Décoder paquet eHub
                    packet = self.decode_ehub_packet(message)
                    
                    if packet:
                        # Traiter et envoyer ArtNet
                        self.process_packet(packet)
                        
                        packet_count += 1
                        
                        # Afficher stats périodiquement
                        if packet_count % stats_interval == 0:
                            self._print_stats()
                
        except KeyboardInterrupt:
            print(f"\n🛑 [EHubArtNetPipeline] Arrêt demandé par utilisateur")
        
        self._print_final_stats()
    
    def _print_stats(self):
        """
        Affiche les statistiques courantes
        """
        print(f"📊 [Stats] Paquets: {self.total_packets} | "
              f"Entités: {self.processed_entities} | "
              f"Univers envoyés: {self.sent_universes} | "
              f"Erreurs ArtNet: {self.artnet_errors}")
    
    def _print_final_stats(self):
        """
        Affiche les statistiques finales
        """
        print("\n" + "=" * 60)
        print("📊 STATISTIQUES FINALES PIPELINE eHub→ArtNet")
        print("=" * 60)
        
        # Stats réception/décodage
        print(f"📡 Réception UDP:")
        if self.receiver:
            print(f"   • Messages reçus: {getattr(self.receiver, 'message_count', 0)}")
            print(f"   • Bytes totaux: {getattr(self.receiver, 'total_bytes', 0)}")
        
        print(f"🔬 Décodage eHub:")
        print(f"   • Paquets décodés: {self.total_packets}")
        print(f"   • Entités totales: {self.total_entities}")
        print(f"   • Erreurs décodage: {self.decode_errors}")
        
        # Stats ArtNet
        print(f"🎭 Envoi ArtNet:")
        print(f"   • Entités traitées: {self.processed_entities}")
        print(f"   • Univers envoyés: {self.sent_universes}")
        print(f"   • Paquets ArtNet: {self.artnet_sender.sent_packets}")
        print(f"   • Bytes ArtNet: {self.artnet_sender.sent_bytes}")
        print(f"   • Erreurs envoi: {self.artnet_errors}")
        
        # Stats contrôleurs
        print(f"🎮 Contrôleurs BC216:")
        for ip, controller in self.controllers.items():
            print(f"   • {ip}: {controller.packet_count} paquets")
        
        print("=" * 60)
    
    def stop(self):
        """
        Arrête le pipeline complet
        """
        print("🔌 [EHubArtNetPipeline] Arrêt du pipeline...")
        
        # Arrêter ArtNet
        self.artnet_sender.close()
        
        # Arrêter décodeur eHub (étape 2)
        super().stop()
        
        print("✅ [EHubArtNetPipeline] Pipeline arrêté")

def main():
    """
    Point d'entrée principal - Mode démo
    """
    print("🎭 === PIPELINE COMPLET eHub → ArtNet ===")
    print("🎯 Réception Unity → Décodage eHub → Envoi BC216")
    print()
    
    # Initialiser pipeline
    pipeline = EHubArtNetPipeline(port=8765)
    
    if not pipeline.initialize():
        print("❌ Échec initialisation pipeline")
        return
    
    # Mode continu
    try:
        pipeline.run_continuous()
    finally:
        pipeline.stop()

if __name__ == "__main__":
    main()
