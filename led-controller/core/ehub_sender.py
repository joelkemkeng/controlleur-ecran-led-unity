"""
Module d'envoi de paquets eHub
Complément du module ehub.py existant pour l'émission de données
"""

import socket
import struct
import gzip
from typing import List, Tuple

class EHubSender:
    """Émetteur de paquets eHub"""
    
    def __init__(self, target_ip: str = "127.0.0.1", target_port: int = 8765):
        self.target_ip = target_ip
        self.target_port = target_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def create_ehub_packet(self, entities: List[Tuple[int, int, int, int, int]], universe: int = 1) -> bytes:
        """
        Crée un paquet eHub au format attendu
        
        Args:
            entities: Liste de tuples (entity_id, r, g, b, w)
            universe: Univers eHub (défaut: 1)
            
        Returns:
            bytes: Paquet eHub compressé prêt à l'envoi
        """
        # Créer le payload des entités
        entities_payload = bytearray()
        for entity_id, r, g, b, w in entities:
            # Format: entity_id (2 bytes) + RGBW (4 bytes)
            entities_payload.extend(struct.pack('HBBBB', entity_id, r, g, b, w))
        
        # Compresser le payload
        compressed_payload = gzip.compress(entities_payload)
        
        # Créer l'en-tête
        header = bytearray()
        header.extend(b'eHub')  # Magic number (4 bytes)
        header.append(0x01)     # Message type (1 byte) - 0x01 pour update
        header.append(universe) # Universe (1 byte)
        header.extend(struct.pack('H', len(entities)))  # Entities count (2 bytes)
        header.extend(struct.pack('H', len(compressed_payload)))  # Payload size (2 bytes)
        
        # Assembler le paquet final
        packet = header + compressed_payload
        return bytes(packet)
    
    def send_entities(self, entities: List[Tuple[int, int, int, int, int]], universe: int = 1):
        """
        Envoie une liste d'entités via eHub
        
        Args:
            entities: Liste de tuples (entity_id, r, g, b, w)
            universe: Univers eHub
        """
        if not entities:
            return
            
        packet = self.create_ehub_packet(entities, universe)
        self.socket.sendto(packet, (self.target_ip, self.target_port))
    
    def send_frame(self, frame_data, pixel_mapping: dict = None):
        """
        Envoie une frame complète avec mapping des pixels
        
        Args:
            frame_data: Données de frame (numpy array ou autre)
            pixel_mapping: Dictionnaire de mapping ID -> (x, y)
        """
        entities = []
        
        if pixel_mapping:
            # Utiliser le mapping existant comme dans le logiciel actuel
            for entity_id, (x, y) in pixel_mapping.items():
                if hasattr(frame_data, 'shape') and len(frame_data.shape) == 3:
                    # Frame numpy
                    if 0 <= y < frame_data.shape[0] and 0 <= x < frame_data.shape[1]:
                        r, g, b = frame_data[y, x]
                        if r > 0 or g > 0 or b > 0:  # Ignorer les pixels noirs
                            entities.append((entity_id, int(r), int(g), int(b), 0))
        
        if entities:
            self.send_entities(entities)
    
    def close(self):
        """Ferme le socket"""
        if self.socket:
            self.socket.close()

# Instance globale pour réutilisation (comme artnet.py)
_ehub_sender = None

def get_ehub_sender(target_ip: str = "127.0.0.1", target_port: int = 8765) -> EHubSender:
    """Retourne l'instance globale du sender eHub"""
    global _ehub_sender
    if _ehub_sender is None:
        _ehub_sender = EHubSender(target_ip, target_port)
    return _ehub_sender

def send_ehub_packet(entities: List[Tuple[int, int, int, int, int]], universe: int = 1, 
                    target_ip: str = "127.0.0.1", target_port: int = 8765):
    """Fonction de compatibilité - utilise le sender optimisé"""
    sender = get_ehub_sender(target_ip, target_port)
    sender.send_entities(entities, universe)

def close_ehub_sender():
    """Ferme le sender eHub global"""
    global _ehub_sender
    if _ehub_sender:
        _ehub_sender.close()
        _ehub_sender = None