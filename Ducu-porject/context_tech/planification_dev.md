# Planification Projet LED - 3 Jours (21h)

## 🎯 OBJECTIF GLOBAL
Développer un module de routage LED complet (P1 + P2) en Python pour obtenir 75% de la note totale (75 points sur 100).

---

## 📅 PLANNING GÉNÉRAL

```
JOUR 1 (7h) : FONDATIONS & PARSING
├── Epic 1: eHuB Parser (4h)
└── Epic 2: Architecture Core (3h)

JOUR 2 (7h) : MAPPING & ARTNET  
├── Epic 3: Entity Mapper (3h)
├── Epic 4: ArtNet Sender (2h)
└── Epic 5: Monitoring (2h)

JOUR 3 (7h) : INTÉGRATION & DÉMO
├── Epic 6: Patch System (2h)
├── Epic 7: Configuration (2h)
├── Epic 8: Tests & Debug (2h)
└── Epic 9: Animation P2 (1h)
```

---

# 📋 JOUR 1 - FONDATIONS (7h)

## Epic 1: eHuB Parser Foundation (4h)

### Story 1.1: Structures de données (1h)
**Objectif :** Créer les classes de base pour manipuler les messages eHuB.

#### Tâche 1.1.1: Classes de base (30min)
```python
# Fichier: core/models.py
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
```

**Tests :**
```python
def test_entity_update_creation():
    entity = EntityUpdate(1, 255, 0, 0, 0)
    assert entity.id == 1
    assert entity.r == 255
```

#### Tâche 1.1.2: Validation des données (30min)
```python
# Fichier: core/validators.py
def validate_entity_update(entity: EntityUpdate) -> bool:
    return (0 <= entity.id <= 65535 and 
            all(0 <= val <= 255 for val in [entity.r, entity.g, entity.b, entity.w]))

def validate_ehub_signature(data: bytes) -> bool:
    return data[:4] == b'eHuB'
```

**Tests :**
```python
def test_entity_validation():
    valid_entity = EntityUpdate(1, 255, 128, 0, 64)
    invalid_entity = EntityUpdate(1, 300, 0, 0, 0)  # R > 255
    assert validate_entity_update(valid_entity) == True
    assert validate_entity_update(invalid_entity) == False
```

### Story 1.2: Message Parser (1.5h)

#### Tâche 1.2.1: Parsing header eHuB (45min)
```python
# Fichier: ehub/parser.py
import struct
import gzip

class EHubParser:
    def parse_header(self, data: bytes) -> dict:
        if len(data) < 10:
            raise ValueError("Message trop court")
        
        signature = data[:4]
        if signature != b'eHuB':
            raise ValueError("Signature invalide")
        
        msg_type = data[4]
        universe = data[5]
        entity_count = struct.unpack('<H', data[6:8])[0]  # little-endian
        payload_size = struct.unpack('<H', data[8:10])[0]
        
        return {
            'type': msg_type,
            'universe': universe,
            'entity_count': entity_count,
            'payload_size': payload_size,
            'payload': data[10:]
        }
```

**Tests :**
```python
def test_parse_header():
    # Message UPDATE: eHuB + type=2 + universe=0 + count=1 + size=6
    test_data = b'eHuB\x02\x00\x01\x00\x06\x00' + b'\x00' * 6
    parser = EHubParser()
    header = parser.parse_header(test_data)
    assert header['type'] == 2
    assert header['universe'] == 0
    assert header['entity_count'] == 1
```

#### Tâche 1.2.2: Décompression GZip (45min)
```python
def decompress_payload(self, compressed_data: bytes) -> bytes:
    try:
        return gzip.decompress(compressed_data)
    except gzip.BadGzipFile:
        raise ValueError("Payload GZip invalide")
```

**Tests :**
```python
def test_gzip_decompression():
    original = b'\x01\x00\xFF\x00\x00\x00'  # Entité 1, rouge
    compressed = gzip.compress(original)
    parser = EHubParser()
    decompressed = parser.decompress_payload(compressed)
    assert decompressed == original
```

### Story 1.3: UPDATE Message Parser (1h)

#### Tâche 1.3.1: Parsing sextuors (1h)
```python
def parse_update_message(self, data: bytes) -> List[EntityUpdate]:
    header = self.parse_header(data)
    if header['type'] != 2:
        raise ValueError("Message n'est pas UPDATE")
    
    decompressed = self.decompress_payload(header['payload'][:header['payload_size']])
    entities = []
    
    # Chaque entité = 6 octets (2 + 1 + 1 + 1 + 1)
    for i in range(0, len(decompressed), 6):
        if i + 6 <= len(decompressed):
            entity_id = struct.unpack('<H', decompressed[i:i+2])[0]
            r = decompressed[i+2]
            g = decompressed[i+3]
            b = decompressed[i+4]
            w = decompressed[i+5]
            entities.append(EntityUpdate(entity_id, r, g, b, w))
    
    return entities
```

**Tests :**
```python
def test_parse_update_complete():
    # Créer message UPDATE complet
    payload = struct.pack('<H', 1) + bytes([255, 0, 0, 0])  # Entité 1 rouge
    payload += struct.pack('<H', 2) + bytes([0, 255, 0, 0]) # Entité 2 verte
    compressed = gzip.compress(payload)
    
    header = b'eHuB\x02\x00\x02\x00' + struct.pack('<H', len(compressed))
    message = header + compressed
    
    parser = EHubParser()
    entities = parser.parse_update_message(message)
    
    assert len(entities) == 2
    assert entities[0].id == 1 and entities[0].r == 255
    assert entities[1].id == 2 and entities[1].g == 255
```

### Story 1.4: CONFIG Message Parser (30min)

#### Tâche 1.4.1: Parsing des plages (30min)
```python
def parse_config_message(self, data: bytes) -> List[EntityRange]:
    header = self.parse_header(data)
    if header['type'] != 1:
        raise ValueError("Message n'est pas CONFIG")
    
    decompressed = self.decompress_payload(header['payload'][:header['payload_size']])
    ranges = []
    
    # Chaque plage = 8 octets (4 × unsigned short)
    for i in range(0, len(decompressed), 8):
        if i + 8 <= len(decompressed):
            values = struct.unpack('<HHHH', decompressed[i:i+8])
            ranges.append(EntityRange(*values))
    
    return ranges
```

**Tests :**
```python
def test_parse_config():
    # Plage: payload 0-169 = entités 1-170
    payload = struct.pack('<HHHH', 0, 1, 169, 170)
    compressed = gzip.compress(payload)
    
    header = b'eHuB\x01\x00\x01\x00' + struct.pack('<H', len(compressed))
    message = header + compressed
    
    parser = EHubParser()
    ranges = parser.parse_config_message(message)
    
    assert len(ranges) == 1
    assert ranges[0].payload_start == 0
    assert ranges[0].entity_start == 1
    assert ranges[0].entity_end == 170
```

## Epic 2: Architecture Core (3h)

### Story 2.1: UDP Receiver (1h)

#### Tâche 2.1.1: Socket UDP (1h)
```python
# Fichier: network/receiver.py
import socket
import threading
from typing import Callable

class EHubReceiver:
    def __init__(self, port: int = 8765, universe: int = 0):
        self.port = port
        self.universe = universe
        self.socket = None
        self.is_listening = False
        self.parser = EHubParser()
        
    def start_listening(self, update_callback: Callable, config_callback: Callable):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', self.port))
        self.is_listening = True
        
        thread = threading.Thread(target=self._listen_loop, 
                                args=(update_callback, config_callback))
        thread.daemon = True
        thread.start()
        
    def _listen_loop(self, update_callback, config_callback):
        while self.is_listening:
            try:
                data, addr = self.socket.recvfrom(65536)
                header = self.parser.parse_header(data)
                
                if header['universe'] == self.universe:
                    if header['type'] == 2:  # UPDATE
                        entities = self.parser.parse_update_message(data)
                        update_callback(entities)
                    elif header['type'] == 1:  # CONFIG
                        ranges = self.parser.parse_config_message(data)
                        config_callback(ranges)
                        
            except Exception as e:
                print(f"Erreur réception: {e}")
```

**Tests :**
```python
def test_udp_receiver():
    received_entities = []
    
    def update_handler(entities):
        received_entities.extend(entities)
    
    def config_handler(ranges):
        pass
        
    receiver = EHubReceiver(port=8766)
    receiver.start_listening(update_handler, config_handler)
    
    # Simuler envoi
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # ... envoyer message test
    
    time.sleep(0.1)
    assert len(received_entities) > 0
```

### Story 2.2: Configuration System (1h)

#### Tâche 2.2.1: Config Manager (1h)
```python
# Fichier: config/manager.py
import json
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ControllerConfig:
    ip: str
    start_entity: int
    end_entity: int
    universes: List[int]

@dataclass
class SystemConfig:
    listen_port: int
    ehub_universe: int
    max_fps: int
    controllers: Dict[str, ControllerConfig]

class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> SystemConfig:
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                return SystemConfig(**data)
        except FileNotFoundError:
            return self.create_default_config()
    
    def create_default_config(self) -> SystemConfig:
        return SystemConfig(
            listen_port=8765,
            ehub_universe=0,
            max_fps=40,
            controllers={
                "controller1": ControllerConfig(
                    ip="192.168.1.45",
                    start_entity=100,
                    end_entity=4858,
                    universes=list(range(0, 32))
                )
            }
        )
```

**Tests :**
```python
def test_config_manager():
    config_mgr = ConfigManager("test_config.json")
    assert config_mgr.config.listen_port == 8765
    assert "controller1" in config_mgr.config.controllers
```

### Story 2.3: Main Application (1h)

#### Tâche 2.3.1: Application principale (1h)
```python
# Fichier: main.py
class LEDRoutingApp:
    def __init__(self):
        self.config_mgr = ConfigManager()
        self.receiver = EHubReceiver(
            port=self.config_mgr.config.listen_port,
            universe=self.config_mgr.config.ehub_universe
        )
        self.entity_ranges = {}  # Mapping CONFIG
        
    def start(self):
        print("Démarrage du routeur LED...")
        self.receiver.start_listening(
            self.handle_update,
            self.handle_config
        )
        
    def handle_update(self, entities: List[EntityUpdate]):
        print(f"Reçu {len(entities)} entités")
        # TODO: mapper vers DMX
        
    def handle_config(self, ranges: List[EntityRange]):
        print(f"Reçu {len(ranges)} plages de configuration")
        self.entity_ranges = {r.entity_start: r for r in ranges}

if __name__ == "__main__":
    app = LEDRoutingApp()
    app.start()
    input("Appuyez sur Entrée pour arrêter...")
```

---

# 📋 JOUR 2 - MAPPING & ARTNET (7h)

## Epic 3: Entity to DMX Mapper (3h)

### Story 3.1: DMX Data Structures (30min)

#### Tâche 3.1.1: Classes DMX (30min)
```python
# Fichier: dmx/models.py
@dataclass
class DMXChannel:
    universe: int
    channel: int  # 1-512
    value: int    # 0-255

@dataclass
class DMXPacket:
    controller_ip: str
    universe: int
    channels: Dict[int, int]  # channel -> value
```

### Story 3.2: Entity Mapping Logic (2h)

#### Tâche 3.2.1: Mapper principal (2h)
```python
# Fichier: mapping/entity_mapper.py
class EntityMapper:
    def __init__(self, config: SystemConfig):
        self.config = config
        self.entity_to_dmx = {}  # Cache mapping
        
    def build_mapping(self, entity_ranges: Dict[int, EntityRange]):
        """Construit le mapping entité -> DMX à partir de la config"""
        self.entity_to_dmx.clear()
        
        for controller_name, controller in self.config.controllers.items():
            entities_in_range = [
                entity_id for entity_id in range(controller.start_entity, controller.end_entity + 1)
            ]
            
            # Calcul des positions DMX
            for i, entity_id in enumerate(entities_in_range):
                # 3 canaux par entité RGB (R, G, B)
                start_channel = (i * 3) + 1
                universe_offset = i // 170  # 170 entités par univers
                universe = controller.universes[universe_offset]
                channel_in_universe = ((i % 170) * 3) + 1
                
                self.entity_to_dmx[entity_id] = {
                    'controller_ip': controller.ip,
                    'universe': universe,
                    'r_channel': channel_in_universe,
                    'g_channel': channel_in_universe + 1,
                    'b_channel': channel_in_universe + 2,
                }
    
    def map_entities_to_dmx(self, entities: List[EntityUpdate]) -> List[DMXPacket]:
        dmx_packets = {}  # (ip, universe) -> DMXPacket
        
        for entity in entities:
            if entity.id not in self.entity_to_dmx:
                continue
                
            mapping = self.entity_to_dmx[entity.id]
            key = (mapping['controller_ip'], mapping['universe'])
            
            if key not in dmx_packets:
                dmx_packets[key] = DMXPacket(
                    controller_ip=mapping['controller_ip'],
                    universe=mapping['universe'],
                    channels={}
                )
            
            # Mapper RGB vers canaux DMX
            packet = dmx_packets[key]
            packet.channels[mapping['r_channel']] = entity.r
            packet.channels[mapping['g_channel']] = entity.g
            packet.channels[mapping['b_channel']] = entity.b
        
        return list(dmx_packets.values())
```

**Tests :**
```python
def test_entity_mapping():
    config = SystemConfig(...)
    mapper = EntityMapper(config)
    
    # Simuler des entités
    entities = [EntityUpdate(100, 255, 0, 0, 0)]  # Entité 100 rouge
    
    dmx_packets = mapper.map_entities_to_dmx(entities)
    assert len(dmx_packets) > 0
    
    packet = dmx_packets[0]
    assert packet.controller_ip == "192.168.1.45"
    assert 1 in packet.channels  # Canal R
    assert packet.channels[1] == 255  # Rouge
```

### Story 3.3: Performance Optimization (30min)

#### Tâche 3.3.1: Cache et optimisations (30min)
```python
def optimize_mapping(self):
    """Pré-calcule les mappings pour éviter les calculs répétés"""
    # Déjà implémenté dans build_mapping avec self.entity_to_dmx
    pass

def batch_process_entities(self, entities: List[EntityUpdate], batch_size: int = 100):
    """Traite les entités par lots pour optimiser la mémoire"""
    for i in range(0, len(entities), batch_size):
        batch = entities[i:i + batch_size]
        yield self.map_entities_to_dmx(batch)
```

## Epic 4: ArtNet Sender (2h)

### Story 4.1: ArtNet Protocol (1h)

#### Tâche 4.1.1: Packet ArtNet (1h)
```python
# Fichier: artnet/sender.py
import struct
import socket
import time

class ArtNetSender:
    ARTNET_PORT = 6454
    ARTNET_HEADER = b'Art-Net\x00'
    
    def __init__(self, max_fps: int = 40):
        self.max_fps = max_fps
        self.last_send_time = 0
        self.sockets = {}  # IP -> socket
        
    def create_artnet_packet(self, universe: int, dmx_data: Dict[int, int]) -> bytes:
        # Header ArtNet
        packet = self.ARTNET_HEADER
        packet += struct.pack('<H', 0x5000)  # OpCode DMX
        packet += struct.pack('>H', 14)      # Protocol version
        packet += bytes([0, 0])              # Sequence, Physical
        packet += struct.pack('<H', universe) # Universe
        packet += struct.pack('>H', 512)     # Data length
        
        # Données DMX (512 canaux)
        dmx_channels = bytearray(512)
        for channel, value in dmx_data.items():
            if 1 <= channel <= 512:
                dmx_channels[channel - 1] = value
        
        packet += bytes(dmx_channels)
        return packet
    
    def send_dmx_packets(self, dmx_packets: List[DMXPacket]):
        # Limitation du taux de trame
        current_time = time.time()
        time_since_last = current_time - self.last_send_time
        min_interval = 1.0 / self.max_fps
        
        if time_since_last < min_interval:
            time.sleep(min_interval - time_since_last)
        
        for packet in dmx_packets:
            self._send_to_controller(packet)
        
        self.last_send_time = time.time()
    
    def _send_to_controller(self, packet: DMXPacket):
        if packet.controller_ip not in self.sockets:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sockets[packet.controller_ip] = sock
        
        sock = self.sockets[packet.controller_ip]
        artnet_data = self.create_artnet_packet(packet.universe, packet.channels)
        
        try:
            sock.sendto(artnet_data, (packet.controller_ip, self.ARTNET_PORT))
        except Exception as e:
            print(f"Erreur envoi vers {packet.controller_ip}: {e}")
```

**Tests :**
```python
def test_artnet_packet_creation():
    sender = ArtNetSender()
    dmx_data = {1: 255, 2: 128, 3: 0}  # R=255, G=128, B=0
    
    packet = sender.create_artnet_packet(0, dmx_data)
    
    # Vérifier header
    assert packet[:8] == b'Art-Net\x00'
    
    # Vérifier données DMX
    dmx_start = 18  # Après header ArtNet
    assert packet[dmx_start] == 255  # Canal 1
    assert packet[dmx_start + 1] == 128  # Canal 2
    assert packet[dmx_start + 2] == 0    # Canal 3
```

### Story 4.2: Network Management (1h)

#### Tâche 4.2.1: Gestion réseau robuste (1h)
```python
def validate_controller_connection(self, ip: str) -> bool:
    """Teste la connectivité vers un contrôleur"""
    try:
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_sock.settimeout(1.0)
        test_sock.sendto(b'test', (ip, self.ARTNET_PORT))
        test_sock.close()
        return True
    except:
        return False

def cleanup_sockets(self):
    """Nettoie les sockets ouvertes"""
    for sock in self.sockets.values():
        sock.close()
    self.sockets.clear()
```

## Epic 5: Monitoring System (2h)

### Story 5.1: Real-time Display (2h)

#### Tâche 5.1.1: Monitor Console (2h)
```python
# Fichier: monitoring/display.py
import threading
import time
from collections import deque

class MonitoringDisplay:
    def __init__(self):
        self.ehub_enabled = True
        self.dmx_enabled = True
        self.artnet_enabled = True
        
        self.ehub_stats = {'messages': 0, 'entities': 0, 'last_update': 0}
        self.dmx_stats = {'packets': 0, 'channels': 0, 'last_update': 0}
        self.artnet_stats = {'sent': 0, 'controllers': set(), 'last_send': 0}
        
        self.recent_entities = deque(maxlen=10)
        self.recent_dmx = deque(maxlen=10)
        
    def log_ehub_data(self, entities: List[EntityUpdate]):
        if not self.ehub_enabled:
            return
            
        self.ehub_stats['messages'] += 1
        self.ehub_stats['entities'] += len(entities)
        self.ehub_stats['last_update'] = time.time()
        
        # Garder les dernières entités pour affichage
        self.recent_entities.extend(entities[:5])  # 5 premières
        
        self._display_ehub_update(entities)
    
    def log_dmx_data(self, packets: List[DMXPacket]):
        if not self.dmx_enabled:
            return
            
        self.dmx_stats['packets'] += len(packets)
        self.dmx_stats['channels'] += sum(len(p.channels) for p in packets)
        self.dmx_stats['last_update'] = time.time()
        
        self.recent_dmx.extend(packets)
        self._display_dmx_update(packets)
    
    def log_artnet_send(self, packets: List[DMXPacket]):
        if not self.artnet_enabled:
            return
            
        self.artnet_stats['sent'] += len(packets)
        self.artnet_stats['controllers'].update(p.controller_ip for p in packets)
        self.artnet_stats['last_send'] = time.time()
        
        self._display_artnet_send(packets)
    
    def _display_ehub_update(self, entities: List[EntityUpdate]):
        print(f"[eHuB] {len(entities)} entités reçues")
        for entity in entities[:3]:  # Afficher 3 premières
            print(f"  Entité {entity.id}: RGB({entity.r},{entity.g},{entity.b})")
    
    def _display_dmx_update(self, packets: List[DMXPacket]):
        print(f"[DMX] {len(packets)} paquets générés")
        for packet in packets[:2]:  # Afficher 2 premiers
            channels_str = ', '.join(f"Ch{ch}={val}" for ch, val in list(packet.channels.items())[:3])
            print(f"  {packet.controller_ip} U{packet.universe}: {channels_str}")
    
    def _display_artnet_send(self, packets: List[DMXPacket]):
        print(f"[ArtNet] Envoyé vers {len(set(p.controller_ip for p in packets))} contrôleurs")
    
    def display_stats(self):
        """Affiche les statistiques globales"""
        print("\n=== STATISTIQUES ===")
        print(f"eHuB: {self.ehub_stats['messages']} msg, {self.ehub_stats['entities']} entités")
        print(f"DMX: {self.dmx_stats['packets']} paquets, {self.dmx_stats['channels']} canaux")
        print(f"ArtNet: {self.artnet_stats['sent']} envois vers {len(self.artnet_stats['controllers'])} contrôleurs")
        print("==================\n")
```

**Tests :**
```python
def test_monitoring():
    monitor = MonitoringDisplay()
    
    # Test eHuB logging
    entities = [EntityUpdate(1, 255, 0, 0, 0)]
    monitor.log_ehub_data(entities)
    
    assert monitor.ehub_stats['messages'] == 1
    assert monitor.ehub_stats['entities'] == 1
    assert len(monitor.recent_entities) == 1
```

---

# 📋 JOUR 3 - INTÉGRATION & DÉMO (7h)

## Epic 6: Patch System (2h)

### Story 6.1: Patch Handler (2h)

#### Tâche 6.1.1: Système de patches (2h)
```python
# Fichier: patching/handler.py
import csv
from typing import Dict

class PatchHandler:
    def __init__(self):
        self.patches = {}  # source_channel -> target_channel
        self.enabled = False
        
    def load_patches_from_csv(self, filepath: str):
        """Charge les patches depuis un fichier CSV"""
        self.patches.clear()
        try:
            with open(filepath, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 2:
                        source = int(row[0])
                        target = int(row[1])
                        self.patches[source] = target
        except FileNotFoundError:
            print(f"Fichier patch non trouvé: {filepath}")
    
    def apply_patches(self, dmx_packets: List[DMXPacket]) -> List[DMXPacket]:
        """Applique les patches aux paquets DMX"""
        if not self.enabled or not self.patches:
            return dmx_packets
        
        patched_packets = []
        for packet in dmx_packets:
            new_channels = dict(packet.channels)
            
            # Appliquer les patches
            for source_ch, target_ch in self.patches.items():
                if source_ch in packet.channels:
                    # Copier la valeur du canal source vers le canal cible
                    new_channels[target_ch] = packet.channels[source_ch]
                    print(f"Patch appliqué: Canal {source_ch} -> {target_ch} = {packet.channels[source_ch]}")
            
            patched_packet = DMXPacket(
                controller_ip=packet.controller_ip,
                universe=packet.universe,
                channels=new_channels
            )
            patched_packets.append(patched_packet)
        
        return patched_packets
    
    def add_patch(self, source_channel: int, target_channel: int):
        """Ajoute un patch dynamiquement"""
        self.patches[source_channel] = target_channel
        
    def save_patches_to_csv(self, filepath: str):
        """Sauvegarde les patches dans un fichier CSV"""
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Source_Channel', 'Target_Channel'])
            for source, target in self.patches.items():
                writer.writerow([source, target])
```

**Tests :**
```python
def test_patch_system():
    handler = PatchHandler()
    
    # Ajouter patches: canal 1 défaillant -> redirigé vers canal 389
    handler.add_patch(1, 389)
    handler.add_patch(2, 390)
    handler.enabled = True
    
    # Créer packet DMX avec canaux défaillants
    original_packet = DMXPacket(
        controller_ip="192.168.1.45",
        universe=0,
        channels={1: 255, 2: 128, 3: 64}
    )
    
    patched_packets = handler.apply_patches([original_packet])
    packet = patched_packets[0]
    
    # Vérifier que les patches sont appliqués
    assert packet.channels[389] == 255  # Canal 1 -> 389
    assert packet.channels[390] == 128  # Canal 2 -> 390
    assert packet.channels[3] == 64     # Canal 3 inchangé
```

## Epic 7: Configuration & Integration (2h)

### Story 7.1: Configuration Complete (1h)

#### Tâche 7.1.1: Config avancée (1h)
```python
# Fichier: config/advanced_config.py
class AdvancedConfigManager(ConfigManager):
    def __init__(self, config_file: str = "config.json"):
        super().__init__(config_file)
        self.patch_file = "patches.csv"
        
    def create_mur_led_config(self) -> SystemConfig:
        """Configuration spécifique pour le mur LED 128x128"""
        return SystemConfig(
            listen_port=8765,
            ehub_universe=0,
            max_fps=40,
            controllers={
                "controller1": ControllerConfig(
                    ip="192.168.1.45",
                    start_entity=100,
                    end_entity=4858,
                    universes=list(range(0, 32))
                ),
                "controller2": ControllerConfig(
                    ip="192.168.1.46",
                    start_entity=5100,
                    end_entity=9858,
                    universes=list(range(32, 64))
                ),
                "controller3": ControllerConfig(
                    ip="192.168.1.47",
                    start_entity=10100,
                    end_entity=14858,
                    universes=list(range(64, 96))
                ),
                "controller4": ControllerConfig(
                    ip="192.168.1.48",
                    start_entity=15100,
                    end_entity=19858,
                    universes=list(range(96, 128))
                )
            }
        )
    
    def validate_config(self) -> bool:
        """Valide la cohérence de la configuration"""
        # Vérifier que les plages d'entités ne se chevauchent pas
        entity_ranges = []
        for controller in self.config.controllers.values():
            entity_ranges.append((controller.start_entity, controller.end_entity))
        
        # Trier et vérifier les chevauchements
        entity_ranges.sort()
        for i in range(len(entity_ranges) - 1):
            if entity_ranges[i][1] >= entity_ranges[i+1][0]:
                print(f"Erreur: Chevauchement d'entités détecté")
                return False
        
        return True
    
    def export_excel_template(self, filepath: str):
        """Exporte un template Excel pour la configuration"""
        import pandas as pd
        
        # Créer DataFrame avec exemple de mapping
        data = []
        for name, controller in self.config.controllers.items():
            for entity_id in range(controller.start_entity, 
                                 min(controller.start_entity + 10, controller.end_entity + 1)):
                data.append({
                    'Entity_ID': entity_id,
                    'Controller_IP': controller.ip,
                    'Controller_Name': name,
                    'Universe': controller.universes[0],
                    'Start_Channel': ((entity_id - controller.start_entity) * 3) + 1,
                    'Channels': 'RGB'
                })
        
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False)
        print(f"Template Excel exporté: {filepath}")
```

### Story 7.2: Application Intégrée (1h)

#### Tâche 7.2.1: Application finale (1h)
```python
# Fichier: main_integrated.py
class IntegratedLEDRouter:
    def __init__(self):
        self.config_mgr = AdvancedConfigManager()
        self.receiver = None
        self.mapper = None
        self.patch_handler = PatchHandler()
        self.artnet_sender = None
        self.monitor = MonitoringDisplay()
        
        self.is_running = False
        self.stats_thread = None
        
    def initialize(self):
        """Initialise tous les composants"""
        print("🚀 Initialisation du routeur LED...")
        
        # Valider la configuration
        if not self.config_mgr.validate_config():
            print("❌ Configuration invalide!")
            return False
        
        # Initialiser les composants
        self.receiver = EHubReceiver(
            port=self.config_mgr.config.listen_port,
            universe=self.config_mgr.config.ehub_universe
        )
        
        self.mapper = EntityMapper(self.config_mgr.config)
        
        self.artnet_sender = ArtNetSender(
            max_fps=self.config_mgr.config.max_fps
        )
        
        # Charger les patches si disponibles
        try:
            self.patch_handler.load_patches_from_csv("patches.csv")
            self.patch_handler.enabled = True
            print(f"✅ {len(self.patch_handler.patches)} patches chargés")
        except:
            print("⚠️  Aucun fichier de patches trouvé")
        
        print("✅ Initialisation terminée")
        return True
    
    def start(self):
        """Démarre le routeur"""
        if not self.initialize():
            return
        
        self.is_running = True
        
        # Démarrer l'écoute eHuB
        self.receiver.start_listening(
            self.handle_update,
            self.handle_config
        )
        
        # Démarrer le thread de statistiques
        self.stats_thread = threading.Thread(target=self._stats_loop)
        self.stats_thread.daemon = True
        self.stats_thread.start()
        
        print("🎯 Routeur démarré - En attente de messages eHuB...")
        print("📊 Affichage des stats toutes les 10 secondes")
        print("🔧 Fichiers: config.json, patches.csv")
        
    def handle_update(self, entities: List[EntityUpdate]):
        """Traite un message UPDATE eHuB"""
        try:
            # 1. Logger la réception
            self.monitor.log_ehub_data(entities)
            
            # 2. Mapper entités -> DMX
            dmx_packets = self.mapper.map_entities_to_dmx(entities)
            self.monitor.log_dmx_data(dmx_packets)
            
            # 3. Appliquer les patches
            patched_packets = self.patch_handler.apply_patches(dmx_packets)
            
            # 4. Envoyer via ArtNet
            self.artnet_sender.send_dmx_packets(patched_packets)
            self.monitor.log_artnet_send(patched_packets)
            
        except Exception as e:
            print(f"❌ Erreur traitement UPDATE: {e}")
    
    def handle_config(self, ranges: List[EntityRange]):
        """Traite un message CONFIG eHuB"""
        try:
            self.monitor.log_ehub_data([])  # Pas d'entités dans CONFIG
            
            # Reconstruire le mapping avec les nouvelles plages
            entity_ranges_dict = {r.entity_start: r for r in ranges}
            self.mapper.build_mapping(entity_ranges_dict)
            
            print(f"🔄 Configuration mise à jour: {len(ranges)} plages")
            
        except Exception as e:
            print(f"❌ Erreur traitement CONFIG: {e}")
    
    def _stats_loop(self):
        """Affiche les statistiques périodiquement"""
        while self.is_running:
            time.sleep(10)  # Toutes les 10 secondes
            self.monitor.display_stats()
    
    def stop(self):
        """Arrête le routeur proprement"""
        self.is_running = False
        if self.artnet_sender:
            self.artnet_sender.cleanup_sockets()
        print("🛑 Routeur arrêté")

# Point d'entrée principal
if __name__ == "__main__":
    try:
        router = IntegratedLEDRouter()
        router.start()
        
        print("\n" + "="*50)
        print("COMMANDES DISPONIBLES:")
        print("  's' + Enter : Afficher les statistiques")
        print("  'p' + Enter : Afficher les patches actifs")
        print("  'q' + Enter : Quitter")
        print("="*50)
        
        while True:
            cmd = input().strip().lower()
            if cmd == 'q':
                break
            elif cmd == 's':
                router.monitor.display_stats()
            elif cmd == 'p':
                print(f"Patches actifs: {router.patch_handler.patches}")
                print(f"Patches activés: {router.patch_handler.enabled}")
        
        router.stop()
        
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
```

## Epic 8: Tests & Debug (2h)

### Story 8.1: Tests d'intégration (1h)

#### Tâche 8.1.1: Test complet du pipeline (1h)
```python
# Fichier: tests/integration_test.py
import unittest
import threading
import time
import gzip
import struct

class IntegrationTest(unittest.TestCase):
    def setUp(self):
        self.router = IntegratedLEDRouter()
        self.router.initialize()
        
    def test_complete_pipeline(self):
        """Test du pipeline complet eHuB -> DMX -> ArtNet"""
        
        # 1. Créer un message UPDATE eHuB
        entities_data = []
        entities_data.append(struct.pack('<H', 100) + bytes([255, 0, 0, 0]))  # Entité 100 rouge
        entities_data.append(struct.pack('<H', 101) + bytes([0, 255, 0, 0]))  # Entité 101 verte
        
        payload = b''.join(entities_data)
        compressed = gzip.compress(payload)
        
        header = b'eHuB\x02\x00\x02\x00' + struct.pack('<H', len(compressed))
        message = header + compressed
        
        # 2. Simuler la réception
        received_dmx = []
        original_send = self.router.artnet_sender.send_dmx_packets
        
        def capture_dmx(packets):
            received_dmx.extend(packets)
            return original_send(packets)
        
        self.router.artnet_sender.send_dmx_packets = capture_dmx
        
        # 3. Parser et traiter le message
        entities = self.router.receiver.parser.parse_update_message(message)
        self.router.handle_update(entities)
        
        # 4. Vérifier les résultats
        self.assertEqual(len(entities), 2)
        self.assertEqual(entities[0].id, 100)
        self.assertEqual(entities[0].r, 255)
        
        # Vérifier que du DMX a été généré
        self.assertGreater(len(received_dmx), 0)
        
        # Vérifier le mapping
        packet = received_dmx[0]
        self.assertEqual(packet.controller_ip, "192.168.1.45")
        self.assertIn(1, packet.channels)  # Canal R de la première entité
    
    def test_patch_application(self):
        """Test de l'application des patches"""
        
        # Ajouter un patch
        self.router.patch_handler.add_patch(1, 389)
        self.router.patch_handler.enabled = True
        
        # Créer une entité qui utilise le canal 1
        entities = [EntityUpdate(100, 255, 0, 0, 0)]
        
        # Traiter
        dmx_packets = self.router.mapper.map_entities_to_dmx(entities)
        patched_packets = self.router.patch_handler.apply_patches(dmx_packets)
        
        # Vérifier que le patch est appliqué
        packet = patched_packets[0]
        self.assertIn(389, packet.channels)  # Canal patché
        self.assertEqual(packet.channels[389], 255)
    
    def test_performance(self):
        """Test de performance avec beaucoup d'entités"""
        
        # Créer 1000 entités
        entities = [
            EntityUpdate(i, i % 256, (i * 2) % 256, (i * 3) % 256, 0)
            for i in range(100, 1100)
        ]
        
        start_time = time.time()
        dmx_packets = self.router.mapper.map_entities_to_dmx(entities)
        end_time = time.time()
        
        # Vérifier la performance (< 10ms pour 1000 entités)
        processing_time = end_time - start_time
        self.assertLess(processing_time, 0.01)
        
        # Vérifier que toutes les entités sont traitées
        total_channels = sum(len(p.channels) for p in dmx_packets)
        self.assertGreater(total_channels, 0)

if __name__ == '__main__':
    unittest.main()
```

### Story 8.2: Debug Tools (1h)

#### Tâche 8.2.1: Outils de débogage (1h)
```python
# Fichier: tools/debug_tools.py
class DebugTools:
    @staticmethod
    def create_test_ehub_message(entity_id: int, r: int, g: int, b: int) -> bytes:
        """Crée un message eHuB UPDATE pour test"""
        payload = struct.pack('<H', entity_id) + bytes([r, g, b, 0])
        compressed = gzip.compress(payload)
        
        header = b'eHuB\x02\x00\x01\x00' + struct.pack('<H', len(compressed))
        return header + compressed
    
    @staticmethod
    def send_test_message(message: bytes, port: int = 8765):
        """Envoie un message de test via UDP"""
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message, ('127.0.0.1', port))
        sock.close()
    
    @staticmethod
    def create_sequential_test():
        """Crée un test qui allume les LEDs en séquence"""
        for entity_id in range(100, 110):
            message = DebugTools.create_test_ehub_message(entity_id, 255, 0, 0)
            DebugTools.send_test_message(message)
            time.sleep(0.1)
            print(f"Envoyé: Entité {entity_id} rouge")
    
    @staticmethod
    def create_color_sweep_test():
        """Test de balayage de couleurs"""
        colors = [
            (255, 0, 0),    # Rouge
            (0, 255, 0),    # Vert
            (0, 0, 255),    # Bleu
            (255, 255, 0),  # Jaune
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
            (255, 255, 255) # Blanc
        ]
        
        for i, (r, g, b) in enumerate(colors):
            entity_id = 100 + i
            message = DebugTools.create_test_ehub_message(entity_id, r, g, b)
            DebugTools.send_test_message(message)
            print(f"Envoyé: Entité {entity_id} RGB({r},{g},{b})")
            time.sleep(0.5)

# Script de test interactif
if __name__ == "__main__":
    print("🧪 Outils de test eHuB")
    print("1. Test séquentiel")
    print("2. Test balayage couleurs")
    print("3. Test entité unique")
    
    choice = input("Choix (1-3): ").strip()
    
    if choice == "1":
        DebugTools.create_sequential_test()
    elif choice == "2":
        DebugTools.create_color_sweep_test()
    elif choice == "3":
        entity_id = int(input("ID entité: "))
        r = int(input("Rouge (0-255): "))
        g = int(input("Vert (0-255): "))
        b = int(input("Bleu (0-255): "))
        
        message = DebugTools.create_test_ehub_message(entity_id, r, g, b)
        DebugTools.send_test_message(message)
        print(f"✅ Message envoyé: Entité {entity_id} RGB({r},{g},{b})")
```

## Epic 9: Animation Demo P2 (1h)

### Story 9.1: Démonstration artistique (1h)

#### Tâche 9.1.1: Animation simple pour démo (1h)
```python
# Fichier: demo/animation_demo.py
import math
import time
import threading

class AnimationDemo:
    def __init__(self, router):
        self.router = router
        self.running = False
        
    def start_demo(self):
        """Lance la démonstration"""
        self.running = True
        
        print("🎨 Démonstration artistique démarrée")
        print("Animations disponibles:")
        print("1. Vague de couleur")
        print("2. Effet arc-en-ciel")
        print("3. Pulsation")
        print("4. Effet matrice")
        
        animations = [
            self.color_wave_animation,
            self.rainbow_animation,
            self.pulse_animation,
            self.matrix_animation
        ]
        
        try:
            for i, animation in enumerate(animations):
                if not self.running:
                    break
                    
                print(f"\n🎭 Animation {i+1}: {animation.__name__}")
                animation()
                time.sleep(2)  # Pause entre animations
                
        except KeyboardInterrupt:
            print("\n🛑 Démonstration interrompue")
        finally:
            self.running = False
    
    def color_wave_animation(self, duration: float = 10.0):
        """Animation de vague de couleur traversant l'écran"""
        start_time = time.time()
        
        while time.time() - start_time < duration and self.running:
            current_time = time.time() - start_time
            
            entities = []
            
            # Créer une vague qui traverse l'écran (entités 100-300)
            for entity_id in range(100, 301):
                # Position relative de l'entité (0.0 à 1.0)
                pos = (entity_id - 100) / 200.0
                
                # Vague sinusoïdale avec décalage temporel
                wave = math.sin(pos * 2 * math.pi + current_time * 3)
                intensity = int((wave + 1) * 127.5)  # 0-255
                
                # Couleur qui change selon la position
                r = intensity if pos < 0.33 else 0
                g = intensity if 0.33 <= pos < 0.66 else 0
                b = intensity if pos >= 0.66 else 0
                
                entities.append(EntityUpdate(entity_id, r, g, b, 0))
            
            # Envoyer au routeur
            self.router.handle_update(entities)
            time.sleep(1/30)  # 30 FPS
    
    def rainbow_animation(self, duration: float = 8.0):
        """Effet arc-en-ciel rotatif"""
        start_time = time.time()
        
        while time.time() - start_time < duration and self.running:
            current_time = time.time() - start_time
            
            entities = []
            
            for entity_id in range(100, 201):
                # Position relative
                pos = (entity_id - 100) / 100.0
                
                # Rotation de l'arc-en-ciel
                hue = (pos + current_time * 0.5) % 1.0
                
                # Conversion HSV vers RGB simplifiée
                r, g, b = self.hsv_to_rgb(hue, 1.0, 1.0)
                
                entities.append(EntityUpdate(entity_id, r, g, b, 0))
            
            self.router.handle_update(entities)
            time.sleep(1/25)  # 25 FPS
    
    def pulse_animation(self, duration: float = 6.0):
        """Pulsation douce de toutes les LEDs"""
        start_time = time.time()
        
        while time.time() - start_time < duration and self.running:
            current_time = time.time() - start_time
            
            # Pulsation sinusoïdale
            pulse = math.sin(current_time * 2 * math.pi / 2)  # Période de 2 secondes
            intensity = int((pulse + 1) * 127.5)
            
            entities = []
            for entity_id in range(100, 151):
                # Couleur qui change graduellement
                r = intensity
                g = int(intensity * 0.7)
                b = int(intensity * 0.3)
                
                entities.append(EntityUpdate(entity_id, r, g, b, 0))
            
            self.router.handle_update(entities)
            time.sleep(1/20)  # 20 FPS
    
    def matrix_animation(self, duration: float = 12.0):
        """Effet Matrix avec pixels qui tombent"""
        start_time = time.time()
        matrix_drops = []  # Liste des "gouttes" qui tombent
        
        while time.time() - start_time < duration and self.running:
            current_time = time.time() - start_time
            
            # Ajouter de nouvelles gouttes aléatoirement
            if len(matrix_drops) < 10 and time.time() % 0.5 < 0.1:
                import random
                column = random.randint(0, 19)  # 20 colonnes
                matrix_drops.append({
                    'column': column,
                    'position': 0,
                    'speed': random.uniform(0.5, 2.0)
                })
            
            entities = []
            
            # Mettre à jour et dessiner les gouttes
            for drop in matrix_drops[:]:
                drop['position'] += drop['speed'] * 0.1
                
                # Dessiner la traînée de la goutte
                for i in range(10):  # Traînée de 10 pixels
                    row = int(drop['position'] - i)
                    if 0 <= row < 20:  # 20 lignes
                        entity_id = 100 + row * 20 + drop['column']
                        
                        # Intensité décroissante pour la traînée
                        intensity = max(0, 255 - i * 25)
                        
                        entities.append(EntityUpdate(entity_id, 0, intensity, 0, 0))
                
                # Supprimer les gouttes qui sont sorties de l'écran
                if drop['position'] > 30:
                    matrix_drops.remove(drop)
            
            self.router.handle_update(entities)
            time.sleep(1/15)  # 15 FPS
    
    def hsv_to_rgb(self, h: float, s: float, v: float) -> tuple:
        """Conversion HSV vers RGB"""
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return int(r * 255), int(g * 255), int(b * 255)
    
    def stop(self):
        """Arrête la démonstration"""
        self.running = False

# Script de démonstration
if __name__ == "__main__":
    # Lancer le routeur en arrière-plan
    router = IntegratedLEDRouter()
    router_thread = threading.Thread(target=router.start)
    router_thread.daemon = True
    router_thread.start()
    
    time.sleep(2)  # Laisser le routeur s'initialiser
    
    # Lancer la démonstration
    demo = AnimationDemo(router)
    demo.start_demo()
    
    # Nettoyer
    router.stop()
```

---

# 📊 VALIDATION & CRITÈRES DE RÉUSSITE

## Tests obligatoires par Epic

### Epic 1-2: Foundation (Tests unitaires)
- ✅ Parsing messages eHuB UPDATE/CONFIG
- ✅ Décompression GZip
- ✅ Validation des données
- ✅ Réception UDP

### Epic 3-4: Mapping & ArtNet (Tests d'intégration)
- ✅ Mapping entités → DMX correct
- ✅ Formation paquets ArtNet valides
- ✅ Limitation taux de trame (40 FPS)
- ✅ Envoi vers contrôleurs multiples

### Epic 5-6: Monitoring & Patches (Tests fonctionnels)
- ✅ Affichage temps réel des données
- ✅ Application des patches
- ✅ Sauvegarde/chargement configuration

### Epic 7-9: Intégration finale (Tests système)
- ✅ Pipeline complet eHuB → ArtNet
- ✅ Performance avec 1000+ entités
- ✅ Animation fluide sur mur LED
- ✅ Gestion des erreurs robuste

## Points obtenus (objectif 75/100)

```
P1 - Module de routage: 60 points
├── E1 (Parser eHuB): 4 pts ✅
├── E2 (Config port): 3 pts ✅
├── E3 (Monitoring): 18 pts ✅
├── E4 (Mapping): 18 pts ✅
├── E5 (Performance): 3 pts ✅
├── E6 (Config files): 5 pts ✅
├── E7 (Rate limit): 2 pts ✅
└── E8 (Patch map): 7 pts ✅

P2 - Animation: 15 points ✅
└── Démo artistique fluide

TOTAL VISÉ: 75 points = 75%
```

---

# 🚀 COMMANDES DE LANCEMENT

## Structure des fichiers
```
led_router/
├── main.py                 # Application principale
├── config.json            # Configuration système
├── patches.csv            # Fichier des patches
├── core/
│   ├── models.py          # Structures de données
│   └── validators.py      # Validation
├── ehub/
│   └── parser.py          # Parser eHuB
├── network/
│   └── receiver.py        # Récepteur UDP
├── mapping/
│   └── entity_mapper.py   # Mapper entités→DMX
├── artnet/
│   └── sender.py          # Envoi ArtNet
├── patching/
│   └── handler.py         # Gestion patches
├── monitoring/
│   └── display.py         # Monitoring temps réel
├── config/
│   ├── manager.py         # Gestionnaire config
│   └── advanced_config.py # Config avancée
├── tools/
│   └── debug_tools.py     # Outils de test
├── demo/
│   └── animation_demo.py  # Démonstration P2
└── tests/
    └── integration_test.py # Tests complets
```

## Commandes essentielles
```bash
# Lancer le routeur principal
python main.py

# Lancer les tests
python -m pytest tests/

# Générer des messages de test
python tools/debug_tools.py

# Démonstration artistique
python demo/animation_demo.py

# Tests d'intégration
python tests/integration_test.py
```

---

# 🎯 CHECKLIST FINALE

## Jour 1 ✅
- [ ] Structures de données (EntityUpdate, DMXPacket, etc.)
- [ ] Parser eHuB (UPDATE + CONFIG)
- [ ] Récepteur UDP fonctionnel
- [ ] Configuration système de base
- [ ] Tests unitaires du parsing

## Jour 2 ✅
- [ ] Mapper entités → DMX complet
- [ ] Sender ArtNet fonctionnel
- [ ] Monitoring temps réel
- [ ] Tests d'intégration mapping
- [ ] Limitation taux de trame

## Jour 3 ✅
- [ ] Système de patches opérationnel
- [ ] Configuration avancée (mur LED)
- [ ] Application intégrée finale
- [ ] Tests système complets
- [ ] Animation de démonstration P2

## Validation finale ✅
- [ ] Test sur vrai mur LED (192.168.1.45-48)
- [ ] Performance 40 FPS avec 16k entités
- [ ] Gestion erreurs robuste
- [ ] Documentation code complète
- [ ] Démonstration artistique fluide

**🏆 OBJECTIF: 75 points en 3 jours = RÉUSSITE GARANTIE!**