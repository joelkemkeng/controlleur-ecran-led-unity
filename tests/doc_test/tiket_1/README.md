# Ticket 1 – Création des classes de base pour le routage LED

## Objectif
Mettre en place les structures de données fondamentales pour manipuler les messages eHuB dans le module de routage LED. Ces classes servent de socle à toute la logique de parsing, mapping et routage des données LED.

## Ce que fait ce ticket
- Définit trois classes principales dans `core/models.py` :
  - `EntityUpdate` : représente l'état d'une LED (ID, valeurs RGBW)
  - `EntityRange` : décrit une plage de correspondance entre positions dans le payload binaire et IDs d'entités
  - `EHubMessage` : structure un message eHuB reçu (type, univers, payload binaire)
- Permet de manipuler proprement les données reçues sur le réseau, de les parser et de les mapper.

## Pourquoi c'est important
- Ces classes sont la base de toute la chaîne de traitement : parsing, mapping, routage, tests.
- Elles garantissent la portabilité (compatibles Raspberry Pi) et la maintenabilité du code.
- Elles facilitent l'écriture de tests unitaires et l'évolution du projet.

## Comment tester
1. Les tests unitaires sont dans `tests/test_models.py`.
2. Pour lancer les tests :
   ```bash
   pytest tests/test_models.py
   ```
3. Les tests vérifient :
   - La création correcte d'une entité LED (`EntityUpdate`)
   - La création correcte d'une plage (`EntityRange`)
   - La création correcte d'un message eHuB (`EHubMessage`)
4. Si tous les tests passent, la structure de base est valide et portable.

## Exemple de code
```python
from core.models import EntityUpdate, EntityRange, EHubMessage

entity = EntityUpdate(1, 255, 0, 0, 0)
range_ = EntityRange(0, 1, 169, 170)
msg = EHubMessage(2, 0, b'payload')
```
