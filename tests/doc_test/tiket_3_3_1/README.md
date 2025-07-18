# Ticket 3.3.1 – Cache et optimisations (EntityMapper)

## Objectif
Optimiser le mapping entités → DMX pour garantir des performances élevées, même avec des milliers d'entités, grâce à un système de cache et au traitement par lots.

## Ce que fait ce ticket
- Ajoute la méthode `optimize_mapping` (cache) à `EntityMapper` (mapping/entity_mapper.py)
- Ajoute la méthode `batch_process_entities` (traitement par lots)
- Docstring pdoc détaillée, exemples d'utilisation, portabilité
- Tests unitaires et d'intégration dans `tests/test_entity_mapper.py`

## Pourquoi c'est important
- Garantit la performance et la scalabilité du pipeline, même pour de très grandes installations
- Permet de traiter les entités par lots pour optimiser la mémoire et le débit
- Assure que le mapping est toujours à jour et cohérent (idempotence du cache)

## Comment tester concrètement
1. Lancer les tests unitaires :
   ```bash
   .\venv\Scripts\activate
   pytest tests/test_entity_mapper.py
   ```
   (ou sur Linux/Mac : `source venv/bin/activate` puis `pytest tests/test_entity_mapper.py`)
2. Les tests vérifient :
   - Le traitement correct des entités par lots (`batch_process_entities`)
   - L'idempotence du cache (`optimize_mapping`)
   - La robustesse du mapping même avec des plages irrégulières
3. En cas réel, tu peux utiliser ces méthodes pour traiter des milliers d'entités sans perte de performance.

## Exemples concrets
```python
from mapping.entity_mapper import EntityMapper
from config.manager import ConfigManager
from core.models import EntityUpdate, EntityRange
config = ConfigManager("config/config.json").config
mapper = EntityMapper(config)
entity_ranges = {100: EntityRange(0, 100, 169, 269)}
mapper.build_mapping(entity_ranges)
entities = [EntityUpdate(100 + i, i, i, i, 0) for i in range(10)]
for dmx_packets in mapper.batch_process_entities(entities, batch_size=4):
    print(dmx_packets)
```

### Exemple de sortie console réelle
```
[DMXPacket(controller_ip='192.168.1.45', universe=0, channels={1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 2, 8: 2, 9: 2, 10: 3, 11: 3, 12: 3})]
...
```

## Portabilité
- 100% compatible Linux, Raspbian, Mac, Windows
- Aucune dépendance exotique, chemins relatifs, code Python standard

---

## Prochaine étape
Intégrer ces optimisations dans le pipeline principal et préparer le routage ArtNet (Epic 4). 