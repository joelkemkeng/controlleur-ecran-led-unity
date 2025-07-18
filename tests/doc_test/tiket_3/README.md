# Ticket 3 – Parsing du header eHuB

## Objectif
Mettre en place une fonction robuste pour parser l'en-tête des messages eHuB, conformément au protocole décrit dans la documentation technique. Cette étape est essentielle pour garantir la bonne interprétation des messages reçus sur le réseau.

## Ce que fait ce ticket
- Implémente la fonction `parse_header(data: bytes) -> dict` dans `ehub/parser.py`.
- Cette fonction :
  - Vérifie la signature eHuB (b'eHuB')
  - Extrait le type de message, l'univers cible, le nombre d'entités/plages, la taille du payload, et le payload compressé
  - Lève des exceptions explicites en cas d'erreur (signature invalide, message trop court)
- Documente la fonction avec une docstring compatible pdoc (pour la génération de documentation web)

## Pourquoi c'est important
- Permet de valider et d'extraire les informations critiques de chaque message eHuB
- Garantit la robustesse du parsing et la conformité au protocole
- Facilite le débogage et la maintenance du code
- Sert de base à tout le pipeline de traitement (décompression, mapping, routage...)

## Comment tester
1. Les tests unitaires sont dans `tests/test_ehub_parser.py`.
2. Pour lancer les tests :
   ```bash
   pytest tests/test_ehub_parser.py
   ```
3. Les tests vérifient :
   - Le parsing correct d'un header valide
   - La détection d'une signature invalide
   - La détection d'un message trop court
4. Si tous les tests passent, le parsing du header est opérationnel et robuste.

## Exemple de code
```python
from ehub.parser import parse_header

data = b'eHuB' + bytes([2, 0]) + b'\x01\x00' + b'\x06\x00' + b'\x11\x22\x33\x44\x55\x66'
header = parse_header(data)
print(header['type'])  # 2
print(header['payload'])  # b'\x11\x22\x33\x44\x55\x66'
```

## Prochaine étape
Passer à la décompression du payload GZip (Epic 1, Story 1.2, Tâche 1.2.2). 