# Ticket 3.1.1 – Classes DMX (DMXChannel, DMXPacket)

## Objectif
Créer les structures de données de base pour représenter les canaux et paquets DMX, socle du mapping entités → DMX, en respectant la logique DMX512 et la structure réelle de l'écran LED.

## Ce que fait ce ticket
- Implémente les dataclasses `DMXChannel` et `DMXPacket` dans `dmx/models.py`
- Docstring pdoc détaillée, exemples d'utilisation, schéma de mapping
- Portabilité assurée (Linux, Raspbian, Mac, Windows)
- Tests unitaires et d'intégration dans `tests/test_dmx_models.py`

## Pourquoi c'est important
- Permet de manipuler proprement les données DMX dans tout le pipeline
- Base indispensable pour le mapping, le routage ArtNet, et les tests
- Facilite la compréhension et la maintenance du code

## Comment tester concrètement
1. Lancer les tests unitaires :
   ```bash
   .\venv\Scripts\activate
   pytest tests/test_dmx_models.py
   ```
   (ou sur Linux/Mac : `source venv/bin/activate` puis `pytest tests/test_dmx_models.py`)
2. Les tests vérifient :
   - La création correcte d'un canal DMX (`DMXChannel`)
   - La création et l'usage d'un paquet DMX (`DMXPacket`)
   - L'ajout dynamique de canaux dans un paquet
3. En cas réel, tu peux instancier ces classes dans n'importe quel module du projet.

## Exemples concrets
```python
from dmx.models import DMXChannel, DMXPacket
ch = DMXChannel(universe=1, channel=42, value=128)
pkt = DMXPacket(controller_ip="192.168.1.45", universe=0, channels={1: 255, 2: 128, 3: 0})
pkt.channels[10] = 200
print(pkt)
```

### Exemple de sortie console réelle
```
DMXPacket(controller_ip='192.168.1.45', universe=0, channels={1: 255, 2: 128, 3: 0, 10: 200})
```

## Portabilité
- 100% compatible Linux, Raspbian, Mac, Windows
- Aucune dépendance exotique, chemins relatifs, code Python standard

---

## Prochaine étape
Intégrer ces classes dans le mapping entités → DMX (Epic 3, Story 3.2) et le routage ArtNet. 