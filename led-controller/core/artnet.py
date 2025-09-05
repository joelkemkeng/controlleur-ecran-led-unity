import socket
import time
from typing import Dict, Tuple

class ArtNetSender:
    """Classe optimisée pour l'envoi Art-Net avec socket réutilisé"""
    
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sequence = 0
        self.header_template = bytearray(b'Art-Net\x00\x00\x50\x00\x0e')  # Header + OpCode + Protocol
        
    def send_packet(self, ip: str, universe: int, dmx_data: bytes):
        """Envoie un paquet Art-Net optimisé"""
        packet = bytearray(self.header_template)
        packet.append(self.sequence)                    # Sequence
        packet.append(0x00)                            # Physical
        packet.extend((universe & 0xFF, (universe >> 8)))  # Universe LSB/MSB
        packet.extend((len(dmx_data) >> 8, len(dmx_data) & 0xFF))  # Length
        packet.extend(dmx_data)                        # Données DMX
        
        self.socket.sendto(packet, (ip, 6454))
        self.sequence = (self.sequence + 1) % 256
        
    def close(self):
        """Ferme le socket"""
        if self.socket:
            self.socket.close()
            self.socket = None

# Instance globale pour réutilisation
_artnet_sender = None

def get_artnet_sender() -> ArtNetSender:
    """Retourne l'instance globale du sender Art-Net"""
    global _artnet_sender
    if _artnet_sender is None:
        _artnet_sender = ArtNetSender()
    return _artnet_sender

def send_artnet_packet(ip: str, universe: int, dmx_data: bytes):
    """Fonction de compatibilité - utilise le sender optimisé"""
    sender = get_artnet_sender()
    sender.send_packet(ip, universe, dmx_data)

def close_artnet_sender():
    """Ferme le sender Art-Net global"""
    global _artnet_sender
    if _artnet_sender:
        _artnet_sender.close()
        _artnet_sender = None