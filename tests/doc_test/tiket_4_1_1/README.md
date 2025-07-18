# Ticket 4.1.1 – Packet ArtNet (ArtNetSender)

## Objectif
Implémenter la génération de paquets ArtNet DMX512 valides à partir des données DMX, conformément au protocole ArtNet, pour permettre l'envoi vers les contrôleurs LED.

## Ce que fait ce ticket
- Implémente la classe `ArtNetSender` dans `artnet/sender.py`
- Méthode :
  - `create_artnet_packet(universe: int, dmx_data: Dict[int, int]) -> bytes`
- Docstring pdoc détaillée, exemples d'utilisation, portabilité
- Test unitaire dans `tests/test_artnet_sender.py`

## Pourquoi c'est important
- Permet de générer des paquets ArtNet conformes au standard, compatibles avec tous les contrôleurs DMX/ArtNet
- Base indispensable pour l'envoi réseau UDP dans le pipeline
- Garantit la robustesse et la portabilité du code

## Comment tester concrètement
1. Lancer le test unitaire :
   ```bash
   .\venv\Scripts\activate
   pytest tests/test_artnet_sender.py
   ```
   (ou sur Linux/Mac : `source venv/bin/activate` puis `pytest tests/test_artnet_sender.py`)
2. Le test vérifie :
   - La validité du header ArtNet
   - La longueur totale du paquet (header + 512 canaux)
   - La position et la valeur des canaux DMX dans le paquet
3. En cas réel, tu peux utiliser la méthode pour générer un paquet à envoyer en UDP.

## Exemples concrets
```python
from artnet.sender import ArtNetSender
sender = ArtNetSender()
dmx_data = {1: 255, 2: 128, 3: 0, 512: 42}
packet = sender.create_artnet_packet(universe=0, dmx_data=dmx_data)
print(packet)
```

### Exemple de sortie console réelle
```
b'Art-Net\x00...\xff\x80\x00...*'
```

## Portabilité
- 100% compatible Linux, Raspbian, Mac, Windows
- Aucune dépendance exotique, chemins relatifs, code Python standard

---

## Prochaine étape
Intégrer la génération et l'envoi de paquets ArtNet dans le pipeline principal (Epic 4, Story 4.2). 