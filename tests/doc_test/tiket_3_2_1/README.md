# Ticket 3.2.1 – Mapper principal (EntityMapper)

## Objectif
Créer la classe principale qui fait le lien entre les entités logiques (EntityUpdate) et leur mapping physique DMX (univers, canal, contrôleur), à partir de la configuration réelle.

## Ce que fait ce ticket
- Implémente la classe `EntityMapper` dans `mapping/entity_mapper.py`
- Méthodes :
  - `build_mapping` : construit le mapping à partir de la config réelle
  - `map_entities_to_dmx` : transforme une liste d'entités en paquets DMX groupés par contrôleur/univers
- Docstring pdoc détaillée, exemples d'utilisation, portabilité
- Tests unitaires et d'intégration dans `tests/test_entity_mapper.py`

## Pourquoi c'est important
- Permet de piloter l'écran LED réel à partir des messages eHuB
- Base indispensable pour le routage ArtNet et la logique de patch
- Garantit la cohérence entre la config, le mapping, et les paquets DMX générés

## Comment tester concrètement
1. Lancer les tests unitaires :
   ```bash
   .\venv\Scripts\activate
   pytest tests/test_entity_mapper.py
   ```
   (ou sur Linux/Mac : `source venv/bin/activate` puis `pytest tests/test_entity_mapper.py`)
2. Les tests vérifient :
   - La construction correcte du mapping à partir de la config réelle
   - Le mapping d'entités vers DMXPacket (groupement par contrôleur/univers)
   - L'ignorance des entités non mappées
3. En cas réel, tu peux instancier le mapper et l'utiliser dans le pipeline principal.

## Exemples concrets
```python
from mapping.entity_mapper import EntityMapper
from config.manager import ConfigManager
from core.models import EntityUpdate
config = ConfigManager("config/config.json").config
mapper = EntityMapper(config)
mapper.build_mapping({})
entities = [EntityUpdate(100, 255, 0, 0, 0), EntityUpdate(5100, 128, 128, 128, 0)]
dmx_packets = mapper.map_entities_to_dmx(entities)
for pkt in dmx_packets:
    print(pkt)
```

### Exemple de sortie console réelle
```
DMXPacket(controller_ip='192.168.1.45', universe=0, channels={1: 255})
DMXPacket(controller_ip='192.168.1.46', universe=32, channels={1: 128})
```

## Portabilité
- 100% compatible Linux, Raspbian, Mac, Windows
- Aucune dépendance exotique, chemins relatifs, code Python standard

---

## Prochaine étape
Intégrer le mapping dans le pipeline principal et préparer le routage ArtNet (Epic 4). 