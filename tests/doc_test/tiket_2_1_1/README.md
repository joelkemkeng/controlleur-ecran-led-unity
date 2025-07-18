# Ticket 2.1.1 – Récepteur UDP eHuB (EHubReceiver)

## Objectif
Mettre en place un récepteur UDP robuste capable d'écouter les messages eHuB (UPDATE et CONFIG), de les parser et de dispatcher les données extraites via des callbacks.

## Ce que fait ce ticket
- Implémente la classe `EHubReceiver` dans `network/receiver.py`.
- Cette classe :
  - Écoute sur un port UDP configurable (par défaut 8765)
  - Filtre les messages selon l'univers cible
  - Parse les messages reçus (UPDATE ou CONFIG) grâce aux fonctions du parser
  - Utilise des callbacks pour transmettre les entités ou plages extraites
  - Fonctionne en thread séparé pour ne pas bloquer l'application principale
  - Gère proprement l'arrêt de l'écoute et les erreurs réseau
- Docstring compatible pdoc pour la génération de documentation web.

## Pourquoi c'est important
- Permet de recevoir en temps réel les instructions de l'application artistique (Unity/Tan) sur le réseau.
- Base de tout le pipeline de routage LED (mapping, patch, ArtNet…)
- Compatible Linux, Raspbian, Mac, Windows (aucune dépendance exotique)

## Comment tester concrètement
1. Lancer les tests fonctionnels :
   ```bash
   pytest tests/test_receiver.py
   ```
2. Les tests vérifient :
   - La réception et le parsing correct d'un message UPDATE (callback appelé avec la bonne entité)
   - La réception et le parsing correct d'un message CONFIG (callback appelé avec la bonne plage)
   - Le filtrage par univers (un message d'un autre univers n'est pas dispatché)
3. En cas réel, on peut envoyer un message eHuB via UDP (ex: avec netcat ou un script Python) et vérifier la réception côté application.

## Exemples concrets
```python
from network.receiver import EHubReceiver
import struct, gzip

def update_cb(entities):
    print(f"Reçu {len(entities)} entités")
def config_cb(ranges):
    print(f"Reçu {len(ranges)} plages")
receiver = EHubReceiver(port=8765, universe=0)
receiver.start_listening(update_cb, config_cb)
# Envoyer un message eHuB sur 127.0.0.1:8765 pour tester
```

## Exemples de sortie console réelle

Lors de la réception de messages eHuB, voici ce que vous pourriez voir en console :

### Message UPDATE (entités)
```
Reçu 1 entités
Entité 42 : RGBW(1,2,3,4)
```

### Message CONFIG (plages)
```
Reçu 1 plages
Plage : payload 0-169 = entités 1-170
```

*Ces sorties dépendent du contenu des callbacks `update_cb` et `config_cb` :*

```python
def update_cb(entities):
    print(f"Reçu {len(entities)} entités")
    for e in entities:
        print(f"Entité {e.id} : RGBW({e.r},{e.g},{e.b},{e.w})")

def config_cb(ranges):
    print(f"Reçu {len(ranges)} plages")
    for r in ranges:
        print(f"Plage : payload {r.payload_start}-{r.payload_end} = entités {r.entity_start}-{r.entity_end}")
```

## Prochaine étape
Intégrer le mapping entités → DMX (Epic 3) et le routage ArtNet. 