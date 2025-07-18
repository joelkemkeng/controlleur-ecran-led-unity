import socket
import threading
import time
import struct
import gzip
import pytest
from network.receiver import EHubReceiver
from core.models import EntityUpdate, EntityRange

def send_udp_message(message: bytes, port: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message, ('127.0.0.1', port))
    sock.close()

def test_ehub_receiver_update_and_config():
    port = 9876
    universe = 3
    received_entities = []
    received_ranges = []

    def update_cb(entities):
        received_entities.extend(entities)
    def config_cb(ranges):
        received_ranges.extend(ranges)

    receiver = EHubReceiver(port=port, universe=universe)
    receiver.start_listening(update_cb, config_cb)
    time.sleep(0.1)  # Laisser le thread démarrer

    # Message UPDATE pour univers cible
    payload = struct.pack('<H', 42) + bytes([1, 2, 3, 4])
    compressed = gzip.compress(payload)
    header = b'eHuB' + bytes([2, universe]) + b'\x01\x00' + struct.pack('<H', len(compressed))
    message = header + compressed
    send_udp_message(message, port)

    # Message CONFIG pour univers cible
    payload_cfg = struct.pack('<HHHH', 0, 1, 169, 170)
    compressed_cfg = gzip.compress(payload_cfg)
    header_cfg = b'eHuB' + bytes([1, universe]) + b'\x01\x00' + struct.pack('<H', len(compressed_cfg))
    message_cfg = header_cfg + compressed_cfg
    send_udp_message(message_cfg, port)

    time.sleep(0.2)  # Laisser le receiver traiter
    receiver.stop_listening()

    assert any(isinstance(e, EntityUpdate) for e in received_entities)
    assert any(isinstance(r, EntityRange) for r in received_ranges)

# Teste que les messages d'un autre univers ne sont pas dispatchés
def test_ehub_receiver_wrong_universe():
    port = 9877
    universe = 5
    received = []
    receiver = EHubReceiver(port=port, universe=universe)
    receiver.start_listening(lambda e: received.append('update'), lambda r: received.append('config'))
    time.sleep(0.1)
    # Message pour univers différent
    payload = struct.pack('<H', 1) + bytes([1, 2, 3, 4])
    compressed = gzip.compress(payload)
    header = b'eHuB' + bytes([2, 99]) + b'\x01\x00' + struct.pack('<H', len(compressed))
    message = header + compressed
    send_udp_message(message, port)
    time.sleep(0.2)
    receiver.stop_listening()
    assert not received 