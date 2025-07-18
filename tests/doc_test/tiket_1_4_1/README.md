# Ticket 1.4.1 – Parsing des messages CONFIG (parse_config_message)

## Objectif
Implémenter une fonction qui extrait, à partir d'un message binaire eHuB CONFIG, la liste complète des plages (EntityRange) définissant la correspondance entre positions dans le payload UPDATE et IDs d'entités.

## Ce que fait ce ticket
- Implémente la fonction `parse_config_message(data: bytes) -> list[EntityRange]` dans `ehub/parser.py`.
- Cette fonction :
  - Vérifie le type du message (CONFIG = 1)
  - Décompresse le payload GZip
  - Extrait chaque plage (8 octets : 4 entiers non signés little-endian)
  - Ignore les plages incomplètes
  - Retourne une liste d'objets `EntityRange`
- Docstring compatible pdoc pour la génération de documentation web.

## Pourquoi c'est important
- Permet de configurer dynamiquement le mapping entre les entités logiques et les positions dans le payload UPDATE.
- Indispensable pour gérer des installations LED complexes et évolutives.
- Garantit la robustesse du parsing et la conformité au protocole eHuB.

## Comment tester concrètement
1. Lancer les tests unitaires :
   ```bash
   pytest tests/test_ehub_parser.py
   ```
2. Les tests vérifient :
   - Extraction correcte d'une ou plusieurs plages à partir d'un message CONFIG valide
   - Gestion d'un message de type incorrect (erreur attendue)
   - Gestion d'un payload tronqué (ignore les plages incomplètes)
3. En cas réel, on peut simuler un message eHuB CONFIG compressé GZip, et vérifier que chaque plage (payload_start, entity_start, payload_end, entity_end) est bien extraite.

## Exemples concrets
```python
from ehub.parser import parse_config_message
import struct, gzip

# Exemple : 2 plages
payload = struct.pack('<HHHH', 0, 1, 169, 170)
payload += struct.pack('<HHHH', 170, 200, 339, 370)
compressed = gzip.compress(payload)
header = b'eHuB\x01\x00\x02\x00' + struct.pack('<H', len(compressed))
message = header + compressed
ranges = parse_config_message(message)
assert ranges[0].entity_start == 1 and ranges[0].entity_end == 170
assert ranges[1].entity_start == 200 and ranges[1].entity_end == 370
```

## Prochaine étape
Intégrer le parsing CONFIG dans le pipeline de routage et passer à l'Epic 2 (récepteur UDP, configuration système, etc.). 