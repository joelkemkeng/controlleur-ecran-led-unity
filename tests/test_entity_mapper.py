r"""
tests/test_entity_mapper.py - Tests unitaires et d'intégration pour EntityMapper (mapping/entity_mapper.py)

Ce module vérifie la construction du mapping entités → DMX et la transformation d'entités en paquets DMX.
Il garantit la cohérence du mapping avec la config réelle et la portabilité du code.

Exécution :
    $ .\venv\Scripts\activate
    $ pytest tests/test_entity_mapper.py

Portabilité :
- Pour Linux/Mac/Raspbian, active le venv avec :
    $ source venv/bin/activate
- Aucun code spécifique Windows, 100% portable.
"""

from mapping.entity_mapper import EntityMapper
from config.manager import ConfigManager
from core.models import EntityUpdate, EntityRange
from dmx.models import DMXPacket


def test_build_mapping_and_map_entities():
    """
    Vérifie la construction du mapping et le mapping d'entités vers DMXPacket.
    - Utilise la config réelle (config/config.json)
    - Simule des plages réelles pour chaque contrôleur
    - Vérifie que les paquets DMX sont corrects
    """
    config = ConfigManager("config/config.json").config
    mapper = EntityMapper(config)
    # Simule des plages réelles (extraites de l'Excel)
    entity_ranges = {
        100: EntityRange(0, 100, 169, 269),      # Plage pour le contrôleur 1, univers 0
        5100: EntityRange(0, 5100, 169, 5269),  # Plage pour le contrôleur 2, univers 32
    }
    mapper.build_mapping(entity_ranges)
    entities = [
        EntityUpdate(100, 255, 0, 0, 0),  # LED 1 du contrôleur 1
        EntityUpdate(101, 0, 255, 0, 0),  # LED 2 du contrôleur 1
        EntityUpdate(5100, 128, 128, 128, 0)  # LED 1 du contrôleur 2
    ]
    dmx_packets = mapper.map_entities_to_dmx(entities)
    # On doit avoir au moins 2 paquets (2 contrôleurs différents)
    assert any(pkt.controller_ip == "192.168.1.45" for pkt in dmx_packets)
    assert any(pkt.controller_ip == "192.168.1.46" for pkt in dmx_packets)
    # Vérifie les canaux du premier paquet
    pkt1 = next(pkt for pkt in dmx_packets if pkt.controller_ip == "192.168.1.45")
    assert pkt1.channels[1] == 255  # R de LED 100
    assert pkt1.channels[2] == 0    # G de LED 100
    assert pkt1.channels[3] == 0    # B de LED 100
    assert pkt1.channels[4] == 0    # R de LED 101
    assert pkt1.channels[5] == 255  # G de LED 101
    assert pkt1.channels[6] == 0    # B de LED 101


def test_map_entities_ignore_unmapped():
    """
    Vérifie que les entités non mappées sont ignorées sans erreur.
    """
    config = ConfigManager("config/config.json").config
    mapper = EntityMapper(config)
    # Simule une plage réelle pour le contrôleur 1
    entity_ranges = {
        100: EntityRange(0, 100, 169, 269),
    }
    mapper.build_mapping(entity_ranges)
    entities = [EntityUpdate(999999, 1, 2, 3, 0)]  # ID hors plage
    dmx_packets = mapper.map_entities_to_dmx(entities)
    assert dmx_packets == []


def test_batch_process_entities():
    """
    Vérifie que batch_process_entities traite bien les entités par lots et retourne les bons paquets DMX.
    """
    config = ConfigManager("config/config.json").config
    mapper = EntityMapper(config)
    entity_ranges = {
        100: EntityRange(0, 100, 169, 269),
    }
    mapper.build_mapping(entity_ranges)
    # Crée 10 entités mappées
    entities = [EntityUpdate(100 + i, i, i, i, 0) for i in range(10)]
    batches = list(mapper.batch_process_entities(entities, batch_size=4))
    assert len(batches) == 3  # 10 entités, batch de 4 => 3 lots
    assert all(isinstance(batch, list) for batch in batches)
    assert sum(len(batch) for batch in batches) > 0


def test_optimize_mapping_is_idempotent():
    """
    Vérifie que optimize_mapping ne modifie pas le mapping existant (idempotence).
    """
    config = ConfigManager("config/config.json").config
    mapper = EntityMapper(config)
    entity_ranges = {
        100: EntityRange(0, 100, 169, 269),
    }
    mapper.build_mapping(entity_ranges)
    before = dict(mapper.entity_to_dmx)
    mapper.optimize_mapping()
    after = dict(mapper.entity_to_dmx)
    assert before == after 