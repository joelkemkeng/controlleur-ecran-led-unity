import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.models import EntityUpdate, EntityRange, EHubMessage

def test_entity_update_creation():
    entity = EntityUpdate(1, 255, 0, 0, 0)
    assert entity.id == 1
    assert entity.r == 255
    assert entity.g == 0
    assert entity.b == 0
    assert entity.w == 0

def test_entity_range_creation():
    rng = EntityRange(0, 1, 169, 170)
    assert rng.payload_start == 0
    assert rng.entity_start == 1
    assert rng.payload_end == 169
    assert rng.entity_end == 170

def test_ehub_message_creation():
    msg = EHubMessage(2, 0, b'payload')
    assert msg.message_type == 2
    assert msg.universe == 0
    assert msg.payload == b'payload' 