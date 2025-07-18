"""
dmx/models.py - Structures de données DMX pour le mapping entités → DMX

Ce module définit les classes de base pour représenter les canaux et paquets DMX,
conformes au protocole DMX512 et à la structure réelle de l'écran LED.

Exemple d'utilisation :
    >>> from dmx.models import DMXChannel, DMXPacket
    >>> ch = DMXChannel(universe=0, channel=1, value=255)
    >>> pkt = DMXPacket(controller_ip="192.168.1.45", universe=0, channels={1: 255, 2: 128, 3: 0})
    >>> print(pkt)

Portabilité :
- 100% compatible Linux, Raspbian, Mac, Windows
- Aucune dépendance exotique
"""

from dataclasses import dataclass, field
from typing import Dict

@dataclass
class DMXChannel:
    """
    Représente un canal DMX (univers, numéro de canal, valeur).
    Args:
        universe (int): Numéro d'univers DMX (0-127)
        channel (int): Numéro de canal (1-512)
        value (int): Valeur du canal (0-255)
    """
    universe: int
    channel: int  # 1-512
    value: int    # 0-255

@dataclass
class DMXPacket:
    """
    Représente un paquet DMX à envoyer à un contrôleur ArtNet.
    Args:
        controller_ip (str): Adresse IP du contrôleur cible
        universe (int): Univers DMX concerné
        channels (Dict[int, int]): Dictionnaire {canal: valeur}
    Exemple d'utilisation :
        >>> pkt = DMXPacket(controller_ip="192.168.1.45", universe=0, channels={1: 255, 2: 128, 3: 0})
    """
    controller_ip: str
    universe: int
    channels: Dict[int, int] = field(default_factory=dict) 