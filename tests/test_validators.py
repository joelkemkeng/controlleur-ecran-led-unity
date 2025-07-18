import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.models import EntityUpdate
from core.validators import validate_entity_update, validate_ehub_signature

# Teste la validation d'une entité LED
# On vérifie qu'une entité avec des valeurs correctes est acceptée
# et qu'une entité avec une valeur hors borne (ici r=300) est rejetée
def test_entity_validation():
    valid_entity = EntityUpdate(1, 255, 128, 0, 64)  # Toutes les valeurs sont valides
    invalid_entity = EntityUpdate(1, 300, 0, 0, 0)  # r > 255, donc invalide
    assert validate_entity_update(valid_entity) == True
    assert validate_entity_update(invalid_entity) == False

# Teste la validation de la signature eHuB
# On vérifie qu'un message commençant par 'eHuB' est reconnu comme valide
# et qu'un message avec une signature incorrecte est rejeté
def test_ehub_signature():
    valid_data = b'eHuB' + b'\x02\x00\x01\x00\x06\x00' + b'\x00' * 6  # Signature correcte
    invalid_data = b'xxxx' + b'\x02\x00\x01\x00\x06\x00' + b'\x00' * 6  # Signature incorrecte
    assert validate_ehub_signature(valid_data) == True
    assert validate_ehub_signature(invalid_data) == False 