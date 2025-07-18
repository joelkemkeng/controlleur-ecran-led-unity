import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ehub.parser import parse_header, decompress_payload, parse_update_message, parse_config_message
import pytest
import gzip
from core.models import EntityUpdate

# Teste le parsing d'un header eHuB valide
# On vérifie que tous les champs sont extraits correctement
def test_parse_header_valid():
    # Message eHuB : signature + type=2 + universe=0 + entity_count=1 + payload_size=6 + payload
    data = b'eHuB' + bytes([2, 0]) + b'\x01\x00' + b'\x06\x00' + b'\x11\x22\x33\x44\x55\x66'
    header = parse_header(data)
    assert header['type'] == 2
    assert header['universe'] == 0
    assert header['entity_count'] == 1
    assert header['payload_size'] == 6
    assert header['payload'] == b'\x11\x22\x33\x44\x55\x66'

# Teste la détection d'une signature invalide
def test_parse_header_invalid_signature():
    data = b'xxxx' + bytes([2, 0]) + b'\x01\x00' + b'\x06\x00' + b'\x11\x22\x33\x44\x55\x66'
    with pytest.raises(ValueError, match="Signature eHuB invalide"):
        parse_header(data)

# Teste la détection d'un message trop court
def test_parse_header_too_short():
    data = b'eHuB' + bytes([2, 0])  # Seulement 6 octets
    with pytest.raises(ValueError, match="Message trop court"):
        parse_header(data)

# Teste la décompression d'un payload GZip valide
def test_decompress_payload_valid():
    original = b'\x01\x00\xFF\x00\x00\x00'  # Entité 1, rouge
    compressed = gzip.compress(original)
    result = decompress_payload(compressed)
    assert result == original

# Teste la gestion d'une erreur sur un payload non GZip
def test_decompress_payload_invalid():
    invalid = b'notgzipdata'
    with pytest.raises(ValueError, match="Payload GZip invalide"):
        decompress_payload(invalid)

# Teste le parsing d'un message UPDATE valide avec une entité
def test_parse_update_message_single_entity():
    import struct
    payload = struct.pack('<H', 42) + bytes([255, 128, 64, 0])  # id=42, r=255, g=128, b=64, w=0
    compressed = gzip.compress(payload)
    header = b'eHuB' + bytes([2, 0]) + b'\x01\x00' + struct.pack('<H', len(compressed))
    message = header + compressed
    entities = parse_update_message(message)
    assert len(entities) == 1
    assert entities[0] == EntityUpdate(42, 255, 128, 64, 0)

# Teste le parsing d'un message UPDATE valide avec plusieurs entités
def test_parse_update_message_multiple_entities():
    import struct
    payload = (
        struct.pack('<H', 1) + bytes([10, 20, 30, 40]) +
        struct.pack('<H', 2) + bytes([50, 60, 70, 80])
    )
    compressed = gzip.compress(payload)
    header = b'eHuB' + bytes([2, 0]) + b'\x02\x00' + struct.pack('<H', len(compressed))
    message = header + compressed
    entities = parse_update_message(message)
    assert len(entities) == 2
    assert entities[0] == EntityUpdate(1, 10, 20, 30, 40)
    assert entities[1] == EntityUpdate(2, 50, 60, 70, 80)

# Teste la gestion d'un message qui n'est pas UPDATE
def test_parse_update_message_wrong_type():
    import struct
    payload = struct.pack('<H', 1) + bytes([1, 2, 3, 4])
    compressed = gzip.compress(payload)
    header = b'eHuB' + bytes([1, 0]) + b'\x01\x00' + struct.pack('<H', len(compressed))
    message = header + compressed
    with pytest.raises(ValueError, match="n'est pas de type UPDATE"):
        parse_update_message(message)

# Teste la gestion d'un payload tronqué (entité incomplète)
def test_parse_update_message_truncated_entity():
    import struct
    # 1 entité complète + 1 entité incomplète (4 octets au lieu de 6)
    payload = struct.pack('<H', 1) + bytes([1, 2, 3, 4]) + b'\x00\x01\x02\x03'  # 10 octets
    compressed = gzip.compress(payload)
    header = b'eHuB' + bytes([2, 0]) + b'\x01\x00' + struct.pack('<H', len(compressed))
    message = header + compressed
    entities = parse_update_message(message)
    # Seule la première entité complète doit être extraite
    assert len(entities) == 1
    assert entities[0].id == 1

# Teste le parsing d'un message CONFIG valide avec une plage
def test_parse_config_message_single_range():
    import struct
    payload = struct.pack('<HHHH', 0, 1, 169, 170)  # plage : positions 0-169 = entités 1-170
    compressed = gzip.compress(payload)
    header = b'eHuB' + bytes([1, 0]) + b'\x01\x00' + struct.pack('<H', len(compressed))
    message = header + compressed
    ranges = parse_config_message(message)
    assert len(ranges) == 1
    assert ranges[0].payload_start == 0
    assert ranges[0].entity_start == 1
    assert ranges[0].payload_end == 169
    assert ranges[0].entity_end == 170

# Teste le parsing d'un message CONFIG valide avec plusieurs plages
def test_parse_config_message_multiple_ranges():
    import struct
    payload = (
        struct.pack('<HHHH', 0, 1, 169, 170) +
        struct.pack('<HHHH', 170, 200, 339, 370)
    )
    compressed = gzip.compress(payload)
    header = b'eHuB' + bytes([1, 0]) + b'\x02\x00' + struct.pack('<H', len(compressed))
    message = header + compressed
    ranges = parse_config_message(message)
    assert len(ranges) == 2
    assert ranges[1].payload_start == 170
    assert ranges[1].entity_start == 200
    assert ranges[1].payload_end == 339
    assert ranges[1].entity_end == 370

# Teste la gestion d'un message qui n'est pas CONFIG
def test_parse_config_message_wrong_type():
    import struct
    payload = struct.pack('<HHHH', 0, 1, 169, 170)
    compressed = gzip.compress(payload)
    header = b'eHuB' + bytes([2, 0]) + b'\x01\x00' + struct.pack('<H', len(compressed))
    message = header + compressed
    with pytest.raises(ValueError, match="n'est pas de type CONFIG"):
        parse_config_message(message)

# Teste la gestion d'un payload tronqué (plage incomplète)
def test_parse_config_message_truncated_range():
    import struct
    # 1 plage complète + 1 plage incomplète (4 octets au lieu de 8)
    payload = struct.pack('<HHHH', 0, 1, 169, 170) + b'\x00\x01\x02\x03'  # 12 octets
    compressed = gzip.compress(payload)
    header = b'eHuB' + bytes([1, 0]) + b'\x01\x00' + struct.pack('<H', len(compressed))
    message = header + compressed
    ranges = parse_config_message(message)
    # Seule la première plage complète doit être extraite
    assert len(ranges) == 1
    assert ranges[0].entity_start == 1