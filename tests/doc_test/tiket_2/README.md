# Ticket 2 – Validation des données eHuB

## Objectif
Mettre en place des fonctions de validation pour garantir l'intégrité des données manipulées par le module de routage LED. Cela permet d'éviter les erreurs de parsing, de mapping ou de routage en amont.

## Ce que fait ce ticket
- Définit deux fonctions principales dans `core/validators.py` :
  - `validate_entity_update(entity: EntityUpdate) -> bool` : vérifie que l'ID et les valeurs RGBW d'une entité sont dans les bornes autorisées.
  - `validate_ehub_signature(data: bytes) -> bool` : vérifie que le message binaire commence bien par la signature eHuB.
- Permet de sécuriser le traitement des messages reçus et d'éviter les corruptions de données.

## Pourquoi c'est important
- Garantit la robustesse du parsing et du routage.
- Permet de détecter rapidement les messages invalides ou corrompus.
- Facilite le débogage et la maintenance du code.

## Comment tester
1. Les tests unitaires sont dans `tests/test_validators.py`.
2. Pour lancer les tests :
   ```bash
   pytest tests/test_validators.py
   ```
3. Les tests vérifient :
   - La validation correcte d'une entité valide et invalide.
   - La détection correcte d'une signature eHuB valide ou non.
4. Si tous les tests passent, la validation des données est opérationnelle.

## Exemple de code
```python
from core.models import EntityUpdate
from core.validators import validate_entity_update, validate_ehub_signature

entity = EntityUpdate(1, 255, 128, 0, 64)
print(validate_entity_update(entity))  # True

invalid_entity = EntityUpdate(1, 300, 0, 0, 0)
print(validate_entity_update(invalid_entity))  # False

msg = b'eHuB' + b'\x02\x00\x01\x00\x06\x00' + b'\x00' * 6
print(validate_ehub_signature(msg))  # True
```

## Prochaine étape
Passer au parsing des headers eHuB (Epic 1, Story 1.2, Tâche 1.2.1). 