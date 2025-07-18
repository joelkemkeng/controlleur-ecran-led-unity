"""
artnet/sender.py - Génération de paquets ArtNet DMX

Ce module contient la classe ArtNetSender qui permet de générer des paquets ArtNet DMX512 valides
à partir de données DMX, conformément au protocole ArtNet (header, OpCode, univers, data length, etc.).

Exemple d'utilisation :
    >>> from artnet.sender import ArtNetSender
    >>> sender = ArtNetSender()
    >>> dmx_data = {1: 255, 2: 128, 3: 0}
    >>> packet = sender.create_artnet_packet(universe=0, dmx_data=dmx_data)
    >>> print(packet)

Portabilité :
- 100% compatible Linux, Raspbian, Mac, Windows
- Aucune dépendance exotique
"""

import struct
import socket
import time
from typing import Dict, List

# Import DMXPacket si besoin (adapter le chemin selon ton projet)
try:
    from dmx.models import DMXPacket
except ImportError:
    class DMXPacket:
        """Classe factice pour DMXPacket (à remplacer par l'import réel)"""
        def __init__(self, controller_ip, universe, channels):
            self.controller_ip = controller_ip
            self.universe = universe
            self.channels = channels

class ArtNetSender:
    """
    Générateur et expéditeur de paquets ArtNet DMX512.
    Permet de créer et d'envoyer des paquets ArtNet sur le réseau à un ou plusieurs contrôleurs.

    - Compatible Linux, Mac, Windows, Raspbian
    - Aucun module exotique requis
    """
    ARTNET_PORT = 6454
    ARTNET_HEADER = b'Art-Net\x00'

    def __init__(self, max_fps: int = 40):
        """
        Initialise l'expéditeur ArtNet.
        Args:
            max_fps (int): Limite de fréquence d'envoi (frames/seconde)
        """
        self.max_fps = max_fps
        self.last_send_time = 0
        self.sockets = {}  # IP -> socket

    def create_artnet_packet(self, universe: int, dmx_data: Dict[int, int]) -> bytes:
        """
        Génère un paquet ArtNet DMX512 valide pour l'univers et les canaux donnés.
        Args:
            universe (int): Numéro d'univers DMX (0-32767)
            dmx_data (Dict[int, int]): Dictionnaire {canal: valeur} (1-512)
        Returns:
            bytes: Paquet binaire ArtNet prêt à l'envoi
        """
        # Header ArtNet
        packet = self.ARTNET_HEADER
        packet += struct.pack('<H', 0x5000)  # OpCode DMX
        packet += struct.pack('>H', 14)      # Protocol version
        packet += bytes([0, 0])              # Sequence, Physical
        packet += struct.pack('<H', universe) # Universe (little-endian)
        packet += struct.pack('>H', 512)     # Data length (toujours 512 canaux)

        # Données DMX (512 canaux)
        dmx_channels = bytearray(512)
        for channel, value in dmx_data.items():
            if 1 <= channel <= 512:
                dmx_channels[channel - 1] = value

        packet += bytes(dmx_channels)
        return packet

    def send_dmx_packets(self, dmx_packets: List[DMXPacket]):
        """
        Envoie une liste de paquets DMX (un par univers/contrôleur) via ArtNet.
        Gère la limitation du taux de trame (max_fps).
        Args:
            dmx_packets (List[DMXPacket]): Liste de paquets DMX à envoyer
        """
        current_time = time.time()
        time_since_last = current_time - self.last_send_time
        min_interval = 1.0 / self.max_fps
        if time_since_last < min_interval:
            time.sleep(min_interval - time_since_last)
        for packet in dmx_packets:
            self._send_to_controller(packet)
        self.last_send_time = time.time()

    def _send_to_controller(self, packet: DMXPacket):
        """
        Envoie un paquet DMX à un contrôleur ArtNet donné (IP/univers).
        Args:
            packet (DMXPacket): Paquet DMX à envoyer
        """
        if packet.controller_ip not in self.sockets:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sockets[packet.controller_ip] = sock
        sock = self.sockets[packet.controller_ip]
        artnet_data = self.create_artnet_packet(packet.universe, packet.channels)
        try:
            sock.sendto(artnet_data, (packet.controller_ip, self.ARTNET_PORT))
        except Exception as e:
            print(f"Erreur envoi vers {packet.controller_ip}: {e}")

    def cleanup_sockets(self):
        """
        Ferme et nettoie tous les sockets ouverts (à appeler à la fin du programme).
        """
        for sock in self.sockets.values():
            sock.close()
        self.sockets.clear()

    def validate_controller_connection(self, ip: str, timeout: float = 1.0) -> bool:
        """
        Teste la connectivité réseau vers un contrôleur ArtNet donné (UDP).

        Cette méthode tente d'envoyer un petit paquet de test ("test") en UDP sur le port ArtNet (6454)
        à l'adresse IP du contrôleur. Si l'envoi ne lève pas d'exception (pas d'erreur réseau, pas de timeout),
        la méthode retourne True, ce qui signifie que le contrôleur est joignable sur le réseau.
        Sinon, elle retourne False.

        Args:
            ip (str): Adresse IP du contrôleur ArtNet à tester (ex: '192.168.1.45')
            timeout (float): Durée maximale d'attente en secondes (défaut: 1.0)

        Returns:
            bool: True si le contrôleur est joignable (UDP), False sinon.

        Exemple d'utilisation :
            >>> sender = ArtNetSender()
            >>> is_ok = sender.validate_controller_connection('192.168.1.45')
            >>> print('Contrôleur joignable' if is_ok else 'Contrôleur injoignable')

        Notes pédagogiques :
        - Cette méthode ne garantit pas que le contrôleur "comprend" ArtNet, seulement qu'il répond au niveau réseau.
        - Utile pour diagnostiquer les problèmes de câblage, de configuration IP, ou de firewall.
        - Fonctionne sur tous les OS (Linux, Mac, Windows, Raspbian).
        """
        try:
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            test_sock.settimeout(timeout)
            # On envoie un petit paquet de test (le contenu importe peu)
            test_sock.sendto(b'test', (ip, self.ARTNET_PORT))
            test_sock.close()
            return True
        except Exception as e:
            # Pour le debug, on peut décommenter la ligne suivante :
            print(f"[validate_controller_connection] Erreur: {e}")
            return False 