from dataclasses import dataclass
from typing import List

@dataclass
class EntityUpdate:
    id: int
    r: int  # 0-255
    g: int  # 0-255
    b: int  # 0-255
    w: int  # 0-255

@dataclass
class EntityRange:
    payload_start: int
    entity_start: int
    payload_end: int
    entity_end: int

@dataclass
class EHubMessage:
    message_type: int  # 1=CONFIG, 2=UPDATE
    universe: int
    payload: bytes 



#msg = EHubMessage(2, 0, b'payload')
# Ici, b'payload' simule un bloc binaire reçu sur le réseau.
# En vrai, ce serait quelque chose comme : b'\\x1f\\x8b\\x08...' (données GZip)
