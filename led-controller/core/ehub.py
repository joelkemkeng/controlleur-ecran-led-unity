from struct import unpack
import gzip
from typing import List, Tuple
import hashlib

# Cache pour éviter la redécompression de paquets identiques
_decompression_cache = {}
_cache_max_size = 100

def get_entities_list(data: bytes) -> List[List[int]]:
    """Parse un paquet eHub et retourne la liste des entités optimisée"""
    sextet_size = 6
    
    # Vérifier le cache de décompression
    data_hash = hashlib.md5(data).digest()
    if data_hash in _decompression_cache:
        return _decompression_cache[data_hash]
    
    # Parse header
    message_head = unpack('4s', data[:4])
    message_type = data[4]
    ehub_universe = data[5]
    entities_count = unpack('H', data[6:8])
    payload_size = unpack('H', data[8:10])
    
    # Décompression
    compressed_payload = gzip.decompress(data[10:])
    
    # Parse optimisé des entités
    entities_list = []
    count = entities_count[0]
    
    # Utiliser une approche plus efficace pour le parsing
    for i in range(count):
        offset = i * sextet_size
        led = compressed_payload[offset:offset + sextet_size]
        entity_id, r, v, b, w = unpack('HBBBB', led)
        entities_list.append([entity_id, r, v, b, w])
    
    # Mettre en cache (avec limite de taille)
    if len(_decompression_cache) >= _cache_max_size:
        # Supprimer l'entrée la plus ancienne
        oldest_key = next(iter(_decompression_cache))
        del _decompression_cache[oldest_key]
    
    _decompression_cache[data_hash] = entities_list
    return entities_list

def clear_cache():
    """Vide le cache de décompression"""
    global _decompression_cache
    _decompression_cache.clear()
