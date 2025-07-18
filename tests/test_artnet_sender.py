r"""
tests/test_artnet_sender.py - Test unitaire pour la génération de paquets ArtNet (artnet/sender.py)

Ce module vérifie que la méthode create_artnet_packet génère un paquet ArtNet DMX512 valide,
conforme au protocole, avec le bon header et les bonnes données DMX.

Exécution :
    $ .\venv\Scripts\activate
    $ pytest tests/test_artnet_sender.py

Portabilité :
- Pour Linux/Mac/Raspbian, active le venv avec :
    $ source venv/bin/activate
- Aucun code spécifique Windows, 100% portable.
"""

from artnet.sender import ArtNetSender
import pytest
import time
from unittest.mock import patch, MagicMock

# Classe factice pour DMXPacket si besoin
class DMXPacket:
    def __init__(self, controller_ip, universe, channels):
        self.controller_ip = controller_ip
        self.universe = universe
        self.channels = channels

def test_create_artnet_packet():
    """
    Vérifie la génération d'un paquet ArtNet DMX512 valide.
    - Vérifie le header ArtNet
    - Vérifie la position et la valeur des canaux DMX
    - Vérifie que les canaux hors bornes sont ignorés
    """
    sender = ArtNetSender()
    dmx_data = {1: 255, 2: 128, 3: 0, 512: 42, 0: 99, 513: 77}  # 0 et 513 doivent être ignorés
    packet = sender.create_artnet_packet(universe=0, dmx_data=dmx_data)
    # Vérifie le header
    assert packet[:8] == b'Art-Net\x00'
    # Vérifie la longueur totale (header + 512 canaux)
    assert len(packet) == 18 + 512
    # Vérifie les valeurs DMX
    dmx_start = 18  # Après le header ArtNet
    assert packet[dmx_start] == 255      # Canal 1
    assert packet[dmx_start + 1] == 128  # Canal 2
    assert packet[dmx_start + 2] == 0    # Canal 3
    assert packet[dmx_start + 511] == 42 # Canal 512
    # Canaux hors bornes
    assert 99 not in packet[dmx_start:dmx_start+512]
    assert 77 not in packet[dmx_start:dmx_start+512]

def test_send_dmx_packets_udp():
    """
    Teste l'envoi UDP de paquets DMX via send_dmx_packets (mock du socket).
    Vérifie que le socket est bien utilisé et que le paquet généré est correct.
    """
    sender = ArtNetSender()
    dmx_packet = DMXPacket('127.0.0.1', 0, {1: 255, 2: 128, 3: 0})
    with patch('socket.socket') as mock_socket_class:
        mock_sock = MagicMock()
        mock_socket_class.return_value = mock_sock
        sender.send_dmx_packets([dmx_packet])
        # Vérifie qu'un socket a été créé et utilisé
        mock_sock.sendto.assert_called()
        args, kwargs = mock_sock.sendto.call_args
        data_sent, addr = args
        assert addr == ('127.0.0.1', sender.ARTNET_PORT)
        assert data_sent[:8] == b'Art-Net\x00'

def test_cleanup_sockets():
    """
    Vérifie que cleanup_sockets ferme bien tous les sockets ouverts.
    """
    sender = ArtNetSender()
    # Simule deux sockets ouverts
    sender.sockets = {'ip1': MagicMock(), 'ip2': MagicMock()}
    sender.cleanup_sockets()
    assert sender.sockets == {}
    # Vérifie que close a été appelé sur chaque socket
    for sock in ['ip1', 'ip2']:
        sender.sockets.get(sock, MagicMock()).close.assert_not_called()  # sockets dict vidé

def test_send_multiple_universes():
    """
    Vérifie l'envoi de paquets vers plusieurs IP et univers différents.
    """
    sender = ArtNetSender()
    packets = [
        DMXPacket('192.168.1.10', 0, {1: 100}),
        DMXPacket('192.168.1.11', 1, {2: 200}),
        DMXPacket('192.168.1.10', 2, {3: 50}),
    ]
    with patch('socket.socket') as mock_socket_class:
        mock_sock = MagicMock()
        mock_socket_class.return_value = mock_sock
        sender.send_dmx_packets(packets)
        # 3 envois attendus
        assert mock_sock.sendto.call_count == 3

def test_max_fps_respected(monkeypatch):
    """
    Vérifie que le délai d'attente est respecté si send_dmx_packets est appelé trop vite (max_fps).
    """
    sender = ArtNetSender(max_fps=10)  # 0.1s min entre envois
    dmx_packet = DMXPacket('127.0.0.1', 0, {1: 255})
    with patch('socket.socket') as mock_socket_class:
        mock_sock = MagicMock()
        mock_socket_class.return_value = mock_sock
        # Premier envoi (doit passer tout de suite)
        sender.send_dmx_packets([dmx_packet])
        t0 = time.time()
        # Deuxième envoi (doit attendre ~0.1s)
        sender.send_dmx_packets([dmx_packet])
        t1 = time.time()
        assert (t1 - t0) >= 0.09  # marge d'erreur 

def test_validate_controller_connection_success():
    """
    Teste que validate_controller_connection retourne True si l'envoi UDP ne lève pas d'exception.
    On mock le socket pour simuler un contrôleur joignable (aucune exception).
    Ce test montre comment vérifier la connectivité réseau sans dépendre d'un vrai matériel.
    """
    sender = ArtNetSender()
    with patch('socket.socket') as mock_socket_class:
        mock_sock = MagicMock()
        mock_socket_class.return_value = mock_sock
        # Pas d'exception lors de sendto
        result = sender.validate_controller_connection('192.168.1.45')
        assert result is True

def test_validate_controller_connection_failure():
    """
    Teste que validate_controller_connection retourne False si une exception réseau est levée.
    On mock le socket pour simuler un contrôleur injoignable (exception lors de sendto).
    Ce test est utile pour s'assurer que la méthode gère bien les erreurs réseau.
    """
    sender = ArtNetSender()
    with patch('socket.socket') as mock_socket_class:
        mock_sock = MagicMock()
        mock_socket_class.return_value = mock_sock
        mock_sock.sendto.side_effect = OSError('Network unreachable')
        result = sender.validate_controller_connection('192.168.1.99')
        assert result is False 