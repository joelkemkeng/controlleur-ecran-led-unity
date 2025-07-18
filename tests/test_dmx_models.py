r"""
tests/test_dmx_models.py - Tests unitaires et d'intégration pour les classes DMX (dmx/models.py)

Ce module vérifie la création, l'accès aux attributs, et l'usage des classes DMXChannel et DMXPacket.
Il garantit que la base du mapping DMX est correcte, portable, et conforme à la logique du projet.

Exécution :
    $ .\venv\Scripts\activate
    $ pytest tests/test_dmx_models.py

Portabilité :
- Pour Linux/Mac/Raspbian, active le venv avec :
    $ source venv/bin/activate
- Aucun code spécifique Windows, 100% portable.
"""

import pytest
from dmx.models import DMXChannel, DMXPacket

def test_dmxchannel_creation():
    """
    Vérifie la création d'un canal DMX et l'accès à ses attributs.
    """
    ch = DMXChannel(universe=1, channel=42, value=128)
    assert ch.universe == 1
    assert ch.channel == 42
    assert ch.value == 128


def test_dmxpacket_creation_and_usage():
    """
    Vérifie la création d'un paquet DMX, l'accès aux attributs, et l'usage du dictionnaire channels.
    """
    pkt = DMXPacket(controller_ip="192.168.1.45", universe=0, channels={1: 255, 2: 128, 3: 0})
    assert pkt.controller_ip == "192.168.1.45"
    assert pkt.universe == 0
    assert isinstance(pkt.channels, dict)
    assert pkt.channels[1] == 255
    assert pkt.channels[2] == 128
    assert pkt.channels[3] == 0


def test_dmxpacket_add_channel():
    """
    Vérifie qu'on peut ajouter dynamiquement un canal à un DMXPacket.
    """
    pkt = DMXPacket(controller_ip="192.168.1.45", universe=1, channels={})
    pkt.channels[10] = 200
    assert pkt.channels[10] == 200 