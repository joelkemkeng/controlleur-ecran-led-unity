# Ticket 4 – Décompression du payload GZip (eHuB)

## Objectif
Mettre en place une fonction robuste pour décompresser le payload GZip extrait des messages eHuB, conformément au protocole et aux exigences du projet.

## Ce que fait ce ticket
- Implémente la fonction `decompress_payload(compressed_data: bytes) -> bytes` dans `ehub/parser.py`.
- Cette fonction :
  - Décompresse le payload GZip extrait du header eHuB
  - Lève une exception explicite si le payload n'est pas un GZip valide ou est corrompu
  - Est documentée avec une docstring compatible pdoc (pour la génération de documentation web)

## Pourquoi c'est important
- Permet d'extraire les données utiles (entités, plages) des messages eHuB
- Garantit la robustesse du parsing et la conformité au protocole
- Facilite le débogage et la maintenance du code
- Sert de base à tout le pipeline de traitement (mapping, routage...)

## Comment tester
1. Les tests unitaires sont dans `tests/test_ehub_parser.py`.
2. Pour lancer les tests :
   ```bash
   pytest tests/test_ehub_parser.py
   ```
3. Les tests vérifient :
   - La décompression correcte d'un payload GZip valide
   - La gestion d'une erreur sur un payload non GZip
4. Si tous les tests passent, la décompression du payload est opérationnelle et robuste.

## Exemple de code
```python
from ehub.parser import decompress_payload
import gzip

original = b'\x01\x00\xFF\x00\x00\x00'  # Entité 1, rouge
compressed = gzip.compress(original)
result = decompress_payload(compressed)
print(result == original)  # True
```

## Prochaine étape
Passer au parsing des sextuors (Epic 1, Story 1.3, Tâche 1.3.1). 