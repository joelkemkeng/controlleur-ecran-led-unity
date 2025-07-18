---

## Tâche 1.3.1 – Parsing des messages UPDATE (parse_update_message)

### Objectif
Extraire, à partir d’un message binaire eHuB UPDATE, la liste complète des entités (LEDs) et leurs valeurs RGBW, en respectant le format du protocole (payload GZip, sextuors de 6 octets).

### Importance pour le projet
- Permet de décoder les instructions de l’application artistique (Unity/Tan) et de les transformer en actions sur les LEDs.
- Garantit la robustesse du parsing (gestion des erreurs, payload tronqué, etc.).
- Base indispensable pour le mapping DMX et le routage ArtNet.

### Comment tester concrètement
1. Lancer les tests unitaires :
   ```bash
   pytest tests/test_ehub_parser.py
   ```
2. Les tests vérifient :
   - Extraction correcte d’une ou plusieurs entités à partir d’un message UPDATE valide
   - Gestion d’un message de type incorrect (erreur attendue)
   - Gestion d’un payload tronqué (ignore les entités incomplètes)
3. En cas réel, on peut simuler un message eHuB UPDATE compressé GZip, et vérifier que chaque entité (ID, R, G, B, W) est bien extraite.

### Exemples concrets
```python
from ehub.parser import parse_update_message
import struct, gzip

# Exemple : 2 entités (id=1, rouge; id=2, vert)
payload = struct.pack('<H', 1) + bytes([255, 0, 0, 0])
payload += struct.pack('<H', 2) + bytes([0, 255, 0, 0])
compressed = gzip.compress(payload)
header = b'eHuB\x02\x00\x02\x00' + struct.pack('<H', len(compressed))
message = header + compressed
entities = parse_update_message(message)
assert entities[0].id == 1 and entities[0].r == 255
assert entities[1].id == 2 and entities[1].g == 255
```

## Exemples de sortie console réelle

Lors de l’utilisation de `parse_update_message` dans un pipeline réel, voici ce que l’on pourrait voir en console :

### Message UPDATE (entités)
```
Reçu 2 entités
Entité 1 : RGBW(255,0,0,0)
Entité 2 : RGBW(0,255,0,0)
```

*Exemple de callback pour affichage :*
```python
def update_cb(entities):
    print(f"Reçu {len(entities)} entités")
    for e in entities:
        print(f"Entité {e.id} : RGBW({e.r},{e.g},{e.b},{e.w})")
```

---

## Prochaine étape
Passer au parsing des messages CONFIG (Tâche 1.4.1) et à l’intégration dans le pipeline de routage.
