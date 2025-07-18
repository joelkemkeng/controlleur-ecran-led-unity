# Contexte Complet - Projet Contrôleur LED LAPS

## 🎯 MISSION PRINCIPALE

Développer un **module de routage LED V2** pour les installations artistiques du Groupe LAPS, remplaçant l'Emitter Hub actuel qui ne peut plus gérer les grandes installations.

---

## 📋 SPÉCIFICATIONS TECHNIQUES COMPLÈTES

### Architecture Système (3 couches)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    COUCHE ARTISTIQUE                                │
│  Unity 2022.3.21 + Extension Tan → Protocole eHuB (UDP/GZip)      │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   COUCHE ROUTAGE (VOTRE MISSION)                   │
│   eHuB Receiver → Entity Mapper → Patch Handler → ArtNet Sender    │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   COUCHE MATÉRIELLE                                 │
│    Contrôleurs BC216 (DMX512) → Bandes LED RGB programmables      │
└─────────────────────────────────────────────────────────────────────┘
```

### Matériel Cible : Contrôleurs BC216

**Caractéristiques :**
- 16 sorties physiques par contrôleur
- 1024 canaux par sortie (2 univers DMX512)
- Protocole d'entrée : ArtNet (UDP)
- Protocole de sortie : SPI vers LED pixels

**Calculs importants :**
- 1 univers DMX512 = 512 canaux
- 1 LED RGB = 3 canaux (R,G,B)
- 1 LED RGBW = 4 canaux (R,G,B,W)
- 1 sortie BC216 = 2 univers = 170 LEDs RGB max (170 × 3 = 510 canaux)

### Installation Test : Mur LED 128×128

**Configuration physique :**
- Dimensions : 2m × 2m
- LEDs visibles : 128 × 128 = 16,384 LEDs
- Structure : 64 bandes de 259 LEDs chacune
- Contrôleurs : 4 BC216 (192.168.1.45 à 192.168.1.48)

**Mapping logique :**
```
Contrôleur 1 (192.168.1.45) : Entités 100-4858   → Univers 0-31
Contrôleur 2 (192.168.1.46) : Entités 5100-9858  → Univers 32-63
Contrôleur 3 (192.168.1.47) : Entités 10100-14858 → Univers 64-95
Contrôleur 4 (192.168.1.48) : Entités 15100-19858 → Univers 96-127
```

**Réseau de test :**
- SSID : GLASS_RESEAUX
- Mot de passe : networks
- Projecteur test : 192.168.1.45, univers 200, canaux 1-3

---

## 🔧 PROTOCOLE eHuB - SPÉCIFICATIONS BINAIRES

### Message UPDATE (40 Hz)

**Structure binaire :**
```
Offset | Taille | Description
-------|--------|--------------------------------------------------
0      | 4      | Signature 'eHuB' (0x65487542)
4      | 1      | Type message (2 = UPDATE)
5      | 1      | Numéro univers eHuB cible
6      | 2      | Nombre d'entités (unsigned short, little-endian)
8      | 2      | Taille payload compressé (unsigned short)
10     | X      | Payload compressé (GZip)
```

**Payload décompressé (sextuors de 6 octets) :**
```
Entité N:
- 2 octets : ID entité (unsigned short)
- 1 octet  : Canal Rouge (0-255)
- 1 octet  : Canal Vert (0-255)
- 1 octet  : Canal Bleu (0-255)
- 1 octet  : Canal Blanc (0-255)
```

### Message CONFIG (1 Hz)

**Structure binaire :**
```
Offset | Taille | Description
-------|--------|--------------------------------------------------
0      | 4      | Signature 'eHuB' (0x65487542)
4      | 1      | Type message (1 = CONFIG)
5      | 1      | Numéro univers eHuB cible
6      | 2      | Nombre de plages (unsigned short)
8      | 2      | Taille payload compressé (unsigned short)
10     | X      | Payload compressé (GZip)
```

**Payload décompressé (plages de 8 octets) :**
```
Plage N:
- 2 octets : Position début dans payload UPDATE (unsigned short)
- 2 octets : ID entité début (unsigned short)
- 2 octets : Position fin dans payload UPDATE (unsigned short)
- 2 octets : ID entité fin (unsigned short)
```

### Exemple concret

**Configuration araignée 8 pattes :**
```
Patte 1: Entités 1-170   → Payload positions 0-169
Patte 2: Entités 200-370 → Payload positions 170-339
Patte 3: Entités 400-570 → Payload positions 340-509
...
```

**Message CONFIG correspondant :**
```
Plage 1: [0, 1, 169, 170]     // Positions 0-169 = entités 1-170
Plage 2: [170, 200, 339, 370] // Positions 170-339 = entités 200-370
...
```

---

## 📋 CAHIER DES CHARGES DÉTAILLÉ

### E1 - Réception eHuB (4 points)
**Fonctionnalités obligatoires :**
- Parser les messages UPDATE et CONFIG
- Décompression GZip des payloads
- Validation des formats binaires
- Gestion des erreurs réseau

**Code example attendu :**
```python
class EHubReceiver:
    def parse_update_message(self, data: bytes) -> List[EntityUpdate]:
        # Vérifier signature 'eHuB'
        # Extraire header (10 octets)
        # Décompresser payload GZip
        # Parser les sextuors (6 octets/entité)
        pass
```

### E2 - Configuration port/univers (3 points)
- Port UDP configurable (défaut : 8765)
- Univers eHuB cible configurable
- Interface de configuration utilisateur

### E3 - Monitoring temps réel (18 points)
**Affichages requis :**
- Flux eHuB entrant (entités + couleurs)
- Flux DMX généré (univers + canaux)
- Flux ArtNet sortant (IP + univers)
- Possibilité d'activer/désactiver chaque moniteur

### E4 - Mapping entités → DMX (18 points)
**Fonctionnalités critiques :**
- Mapping configurable : EntityID → (IP, Univers, Canal)
- Sélection canaux : RGB, RGBW, R seul, etc.
- Offset dans les canaux DMX
- Validation des mappings
- Sauvegarde/chargement configuration

**Exemple mapping :**
```json
{
  "entity_1": {
    "controller_ip": "192.168.1.45",
    "universe": 0,
    "start_channel": 1,
    "channels": ["R", "G", "B"]
  },
  "entity_2": {
    "controller_ip": "192.168.1.45",
    "universe": 0,
    "start_channel": 4,
    "channels": ["R", "G", "B"]
  }
}
```

### E5 - Routage performant (3 points)
- Thread séparé pour le routage
- Algorithme optimal (structures de données efficaces)
- Minimum de paquets ArtNet envoyés
- Gestion mémoire optimisée

### E6 - Sauvegarde/chargement config (5 points)
- Format JSON ou Excel
- Validation des configurations
- Gestion des erreurs de fichier

### E7 - Limitation taux de trame (2 points)
- Fréquence max configurable (défaut : 40 Hz)
- Éviter la saturation réseau

### E8 - Patch Map (7 points)
**Fonctionnalité critique :**
- Redirection canaux défaillants
- Format : Canal source → Canal destination
- Sauvegarde CSV/Excel
- Application dynamique (activable/désactivable)

**Exemple patch :**
```
# Canaux 1-2 défaillants → redirection vers 389-390
1 → 389
2 → 390
```

### E9 - Monitoring ArtNet (Bonus - 3 points)
- Écoute des paquets ArtNet entrants
- Débogage installations
- Vérification autres instances

### E10 - Générateur de test (Bonus - 3 points)
- Simulation messages eHuB
- Patterns de test (séquentiel, couleur unie, aléatoire)
- Test sans Unity

---

## 🏗️ ARCHITECTURE TECHNIQUE RECOMMANDÉE

### Structure de classes principales

```python
# Couche réseau
class EHubReceiver:
    def __init__(self, port: int, universe: int)
    def start_listening(self)
    def parse_message(self, data: bytes) -> Union[UpdateMessage, ConfigMessage]
    def decompress_payload(self, data: bytes) -> bytes

# Couche mapping
class EntityMapper:
    def __init__(self, config: MappingConfig)
    def map_entities_to_dmx(self, entities: List[EntityUpdate]) -> List[DMXData]
    def load_mapping_from_file(self, filepath: str)
    def validate_mapping(self) -> bool

# Couche patches
class PatchHandler:
    def __init__(self, patch_file: str = None)
    def apply_patches(self, dmx_data: List[DMXData]) -> List[DMXData]
    def load_patches_from_csv(self, filepath: str)
    def enable_patching(self, enabled: bool)

# Couche ArtNet
class ArtNetSender:
    def __init__(self, max_fps: int = 40)
    def send_dmx_data(self, dmx_data: List[DMXData])
    def limit_frame_rate(self)
    def group_by_controller(self, dmx_data: List[DMXData]) -> Dict[str, List[DMXData]]
```

### Structures de données

```python
@dataclass
class EntityUpdate:
    id: int
    r: int  # 0-255
    g: int  # 0-255
    b: int  # 0-255
    w: int  # 0-255

@dataclass
class DMXData:
    controller_ip: str
    universe: int
    channel: int
    value: int  # 0-255

@dataclass
class ControllerConfig:
    ip: str
    universes: List[int]
    start_entity: int
    end_entity: int
```

---

## 🧪 TESTS ET VALIDATION

### Tests unitaires obligatoires

1. **Test parsing eHuB :**
   - Messages UPDATE valides/invalides
   - Décompression GZip
   - Gestion des erreurs

2. **Test mapping :**
   - Entités → DMX correct
   - Gestion des channels RGBW
   - Validation des adresses

3. **Test patches :**
   - Redirection canaux
   - Activation/désactivation
   - Chargement CSV

4. **Test ArtNet :**
   - Formation paquets corrects
   - Limitation taux de trame
   - Groupement par contrôleur

### Données de test

```python
# Message UPDATE exemple (après décompression)
test_update = [
    EntityUpdate(id=1, r=255, g=0, b=0, w=0),    # Rouge
    EntityUpdate(id=2, r=0, g=255, b=0, w=0),    # Vert
    EntityUpdate(id=3, r=0, g=0, b=255, w=0),    # Bleu
]

# Configuration mapping exemple
test_mapping = {
    1: {"ip": "192.168.1.45", "universe": 0, "channel": 1},
    2: {"ip": "192.168.1.45", "universe": 0, "channel": 4},
    3: {"ip": "192.168.1.45", "universe": 0, "channel": 7},
}
```

---

## 🚀 LIVRABLES ATTENDUS

### P1 - Module de routage (Obligatoire - 60 points)
- Code source complet et documenté
- Tests unitaires passants
- Configuration fonctionnelle sur le mur LED test
- Respect des exigences E1-E8

### P2 - Animations créatives (Obligatoire - 15 points)
- Démonstration artistique sur le mur LED
- Fluidité et créativité
- Utilisation optimale du routeur développé

### P3 - Outil alternatif (Bonus - 25 points)
- Alternative à Unity/Tan
- Interface utilisateur ergonomique
- Visualisation 3D recommandée

### P4 - Optimisation protocole (Bonus - 25 points)
- Analyse des performances eHuB
- Nouveau protocole optimisé
- Comparaison benchmarks

### P5 - Expérience interactive (Bonus - 25 points)
- Interaction utilisateur temps réel
- Capteurs, caméra, ou interface web
- Démo artistique ou ludique

---

## 🛠️ ENVIRONNEMENT DE DÉVELOPPEMENT

### Outils recommandés
- **Python 3.8+** (performance réseau)
- **C#/.NET** (intégration Unity)
- **Node.js** (interface web)
- **Qt/Tkinter** (interface desktop)

### Bibliothèques utiles
```python
# Réseau
import socket
import struct
import gzip

# Interface
import tkinter as tk
from PyQt5 import QtWidgets

# Données
import json
import pandas as pd
import numpy as np

# Tests
import unittest
import pytest
```

### Configuration réseau
```bash
# Test réseau local
ping 192.168.1.45  # Contrôleur 1
ping 192.168.1.46  # Contrôleur 2

# Wireshark pour déboguer ArtNet
wireshark -i eth0 -f "udp port 6454"
```

---

## 📊 CRITÈRES D'ÉVALUATION

### Performance (20%)
- Latence < 25ms (40 FPS)
- Gestion de 16k+ entités
- Utilisation CPU < 50%
- Utilisation mémoire optimisée

### Fonctionnalité (40%)
- Toutes les exigences E1-E8 implémentées
- Tests unitaires passants
- Configuration robuste
- Gestion d'erreurs complète

### Qualité code (20%)
- Architecture claire et modulaire
- Documentation complète
- Code maintenable
- Respect des conventions

### Innovation (20%)
- Solutions créatives aux problèmes
- Optimisations techniques
- Interface utilisateur intuitive
- Fonctionnalités bonus

---

## 🎯 CONSEILS STRATÉGIQUES

### Phase 1 (Jours 1-3) : Fondations
1. Implémenter EHubReceiver (parsing basique)
2. Créer structures de données
3. Tests unitaires de base
4. Premier mapping simple

### Phase 2 (Jours 4-6) : Fonctionnalités core
1. Mapping complet avec sauvegarde
2. ArtNet sender fonctionnel
3. Monitoring basique
4. Tests sur mur LED

### Phase 3 (Jours 7-9) : Optimisations
1. Patch map système
2. Monitoring avancé
3. Limitation taux de trame
4. Interface utilisateur

### Phase 4 (Jours 10-12) : Finitions
1. Générateur de test
2. Optimisations performance
3. Documentation
4. Préparation démo

### Priorités absolues
1. **E4 (18 pts)** : Mapping entités → DMX
2. **E3 (18 pts)** : Monitoring temps réel
3. **E8 (7 pts)** : Patch map (critique en production)
4. **E1 (4 pts)** : Parsing eHuB correct

---

## 💡 PIÈGES À ÉVITER

### Technique
- **Endianness** : Messages eHuB en little-endian
- **Décompression** : Payload GZip obligatoire
- **Saturation réseau** : Respecter 40 FPS max
- **Validation** : Vérifier tous les formats binaires

### Architecture
- **Thread séparé** : Routage doit être indépendant de l'UI
- **Structures efficaces** : Dict/HashMap pour les mappings
- **Gestion mémoire** : Éviter les fuites sur les messages fréquents
- **Modularité** : Composants indépendants et testables

### Production
- **Robustesse** : Gestion des pannes réseau
- **Configuration** : Validation des fichiers utilisateur
- **Monitoring** : Logs détaillés pour débogage
- **Performance** : Profiling sur grandes installations

---

## 🏆 RÉUSSITE GARANTIE

Avec ce contexte complet, vous avez toutes les informations techniques, architecturales et stratégiques pour développer un module de routage LED de qualité professionnelle. L'objectif est de créer un outil robuste, performant et utilisable en production par le Groupe LAPS.

**Bonne chance ! 🚀**

---

## 🗂️ Répartition des entités, univers et contrôleurs (synthèse asset)

- L'installation LED est découpée en 4 quarts, chacun géré par un contrôleur BC216 distinct.
- Chaque contrôleur gère une plage d'entités (LEDs), d'univers DMX et possède une IP dédiée.

| Contrôleur IP      | Entités (IDs)         | Univers DMX      |
|--------------------|-----------------------|------------------|
| 192.168.1.45       | 100 – 4858            | 0 – 31           |
| 192.168.1.46       | 5100 – 9858           | 32 – 63          |
| 192.168.1.47       | 10100 – 14858         | 64 – 95          |
| 192.168.1.48       | 15100 – 19858         | 96 – 127         |

- Chaque univers DMX gère ≈ 170 LEDs RGB.
- Chaque port du contrôleur gère 2 univers, soit ≈ 341 LEDs RGB.
- Les entités sont organisées par colonnes verticales, avec des offsets d'ID pour chaque quart.
- Un projecteur de test est disponible sur 192.168.1.45, univers 200, canaux 1-3.
- Le mapping complet est dans le fichier Excel `Ecran.xlsx`.

---