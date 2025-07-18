import struct
import gzip
from core.models import EntityUpdate, EntityRange


def parse_header(data: bytes) -> dict:
    """
    Parse l'en-tête d'un message eHuB selon le protocole spécifié.

    Args:
        data (bytes): Le message binaire à parser (doit contenir au moins 10 octets).

    Returns:
        dict: Un dictionnaire avec les champs extraits :
            - 'type' (int) : Type de message (1=CONFIG, 2=UPDATE)
            - 'universe' (int) : Univers cible
            - 'entity_count' (int) : Nombre d'entités (UPDATE) ou de plages (CONFIG)
            - 'payload_size' (int) : Taille du payload compressé
            - 'payload' (bytes) : Payload compressé (GZip)

    Raises:
        ValueError: Si la signature est invalide ou si le message est trop court.

    Exemple d'utilisation :
        >>> header = parse_header(b'eHuB\x02\x00\x01\x00\x06\x00' + b'\x00'*6)
        >>> header['type']
        2
    """
    if len(data) < 10:
        raise ValueError("Message trop court : moins de 10 octets")
    if data[:4] != b'eHuB':
        raise ValueError("Signature eHuB invalide")
    msg_type = data[4]
    universe = data[5]
    entity_count = struct.unpack('<H', data[6:8])[0]
    payload_size = struct.unpack('<H', data[8:10])[0]
    payload = data[10:]
    return {
        'type': msg_type,
        'universe': universe,
        'entity_count': entity_count,
        'payload_size': payload_size,
        'payload': payload
    }


def decompress_payload(compressed_data: bytes) -> bytes:
    """
    Décompresse un payload GZip extrait d'un message eHuB.

    Args:
        compressed_data (bytes): Le payload compressé (GZip) à décompresser.

    Returns:
        bytes: Le contenu décompressé (payload binaire exploitable).

    Raises:
        ValueError: Si le payload n'est pas un GZip valide ou est corrompu.

    Exemple d'utilisation :
        >>> import gzip
        >>> original = b'\x01\x00\xFF\x00\x00\x00'  # Entité 1, rouge
        >>> compressed = gzip.compress(original)
        >>> decompress_payload(compressed) == original
        True
    """
    try:
        return gzip.decompress(compressed_data)
    except gzip.BadGzipFile:
        raise ValueError("Payload GZip invalide ou corrompu")


def parse_update_message(data: bytes) -> list:
    """
    Parse un message eHuB de type UPDATE et extrait la liste des entités (EntityUpdate).

    Args:
        data (bytes): Message binaire eHuB (UPDATE) à parser.

    Returns:
        list[EntityUpdate]: Liste des entités extraites du payload.

    Raises:
        ValueError: Si le message n'est pas UPDATE, ou si le payload est mal formé.

    Exemple d'utilisation :
        >>> # Message UPDATE: eHuB + type=2 + universe=0 + count=1 + size=6
        >>> import gzip, struct
        >>> payload = struct.pack('<H', 1) + bytes([255, 0, 0, 0])
        >>> compressed = gzip.compress(payload)
        >>> header = b'eHuB\x02\x00\x01\x00\x06\x00'
        >>> message = header + compressed
        >>> entities = parse_update_message(message)
        >>> entities[0].id, entities[0].r
        (1, 255)
    """
    header = parse_header(data)
    if header['type'] != 2:
        raise ValueError("Le message n'est pas de type UPDATE (type=2)")
    decompressed = decompress_payload(header['payload'][:header['payload_size']])
    entities = []
    for i in range(0, len(decompressed), 6):
        if i + 6 <= len(decompressed):
            entity_id = struct.unpack('<H', decompressed[i:i+2])[0]
            r = decompressed[i+2]
            g = decompressed[i+3]
            b = decompressed[i+4]
            w = decompressed[i+5]
            entities.append(EntityUpdate(entity_id, r, g, b, w))
        else:
            # Payload tronqué, on ignore la fin incomplète
            break
    return entities


def parse_config_message(data: bytes) -> list:
    """
    Parse un message eHuB de type CONFIG et extrait la liste des plages (EntityRange).

    Args:
        data (bytes): Message binaire eHuB (CONFIG) à parser.

    Returns:
        list[EntityRange]: Liste des plages extraites du payload.

    Raises:
        ValueError: Si le message n'est pas CONFIG, ou si le payload est mal formé.

    Exemple d'utilisation :
        >>> import gzip, struct
        >>> payload = struct.pack('<HHHH', 0, 1, 169, 170)
        >>> compressed = gzip.compress(payload)
        >>> header = b'eHuB\x01\x00\x01\x00' + struct.pack('<H', len(compressed))
        >>> message = header + compressed
        >>> ranges = parse_config_message(message)
        >>> ranges[0].entity_start, ranges[0].entity_end
        (1, 170)
    """
    header = parse_header(data)
    if header['type'] != 1:
        raise ValueError("Le message n'est pas de type CONFIG (type=1)")
    decompressed = decompress_payload(header['payload'][:header['payload_size']])
    ranges = []
    for i in range(0, len(decompressed), 8):
        if i + 8 <= len(decompressed):
            values = struct.unpack('<HHHH', decompressed[i:i+8])
            ranges.append(EntityRange(*values))
        else:
            # Payload tronqué, on ignore la fin incomplète
            break
    return ranges 