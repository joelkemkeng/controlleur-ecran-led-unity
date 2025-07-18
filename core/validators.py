from core.models import EntityUpdate

# Vérifie que les valeurs d'une entité LED sont valides
# - id doit être compris entre 0 et 65535 (format unsigned short)
# - r, g, b, w doivent être compris entre 0 et 255 (valeurs DMX standard)
def validate_entity_update(entity: EntityUpdate) -> bool:
    """
    Vérifie que les valeurs d'une entité LED sont valides.

    Args:
        entity (EntityUpdate): L'entité à valider (doit avoir id, r, g, b, w).

    Returns:
        bool: True si l'entité est valide (toutes les valeurs dans les bornes), False sinon.
    """
    return (0 <= entity.id <= 65535 and 
            all(0 <= val <= 255 for val in [entity.r, entity.g, entity.b, entity.w]))

# Vérifie que le message binaire commence bien par la signature 'eHuB'
# Cela permet de s'assurer que le message reçu est bien du bon protocole
def validate_ehub_signature(data: bytes) -> bool:
    """
    Vérifie que le message binaire commence bien par la signature 'eHuB'.

    Args:
        data (bytes): Le message binaire à vérifier.

    Returns:
        bool: True si la signature est correcte, False sinon.
    """
    return data[:4] == b'eHuB' 