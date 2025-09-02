# 🎭 Étape 4: Pipeline complet avec envoi ArtNet vers BC216

## 📋 Vue d'ensemble

L'**Étape 4** représente l'achèvement du pipeline complet de contrôle LED. Elle hérite des étapes précédentes et ajoute la fonctionnalité d'envoi ArtNet vers les contrôleurs BC216 réels.

### 🔗 Architecture complète

```
Unity (Windows) 
    ↓ UDP:8765
WSL Ubuntu - Étape 2: Décodage eHuB
    ↓ Entités décodées  
Étape 3: Mapping DMX
    ↓ Univers DMX
Étape 4: Envoi ArtNet → BC216
    ↓ ArtNet UDP:6454
Écran LED 128×128 (Affichage)
```

## 🎯 Fonctionnalités

### ✅ Héritages des étapes précédentes
- **Étape 2** : Décodage eHuB complet et validé
- **Étape 3** : Mapping DMX avec 129 univers et optimisations

### 🆕 Nouvelles fonctionnalités Étape 4
- **Envoi ArtNet** vers 4 contrôleurs BC216
- **Support modes** : Production (BC216 réels) et Simulateur
- **Gestion erreurs** robuste avec statistiques
- **Pipeline temps réel** avec monitoring des performances

## 🏗️ Structure des fichiers

```
etape-04-send-artnet/
├── ehub_complete_pipeline_send_artnet.py  # 🎭 Pipeline complet
├── test_etape_4.py                        # 🧪 Tests de validation
└── README.md                              # 📖 Documentation
```

## 🔧 Configuration

### Contrôleurs BC216 (Mode Production)
```python
BC216-1: 192.168.1.45:6454 (univers 0-31)
BC216-2: 192.168.1.46:6454 (univers 32-63)  
BC216-3: 192.168.1.47:6454 (univers 64-95)
BC216-4: 192.168.1.48:6454 (univers 96-127)
```

### Protocole ArtNet
- **Format** : Standard ArtNet v14
- **Univers** : 128 total (32 par contrôleur)
- **Données** : 512 canaux DMX par univers
- **Transport** : UDP vers port 6454

## 🚀 Utilisation

### Lancement du pipeline complet

```bash
cd /home/joel/projet_ecran/controlleur-ecran-led-unity/FINAL-DEV/etape-04-send-artnet
python3 ehub_complete_pipeline_send_artnet.py
```

### Tests de validation

```bash
# Test complet de l'Étape 4
python3 test_etape_4.py
```

## 📊 Classes principales

### `EHubArtNetPipeline`
Pipeline principal qui orchestre toutes les étapes :
- Hérite de `EHubCompleteDecoder` (Étape 2)
- Utilise `EHubDMXPipeline` (Étape 3)  
- Ajoute `ArtNetSender` (Étape 4)

### `ArtNetSender`
Gestionnaire d'envoi ArtNet :
- Conversion DMX → ArtNet
- Envoi vers 4 contrôleurs BC216
- Statistiques et monitoring

### `BC216Controller`
Configuration des contrôleurs :
- Adresse IP et port
- Plage d'univers gérés
- ID de contrôleur

## 🔍 Flux de données

### 1. Réception UDP (Port 8765)
```python
data, addr = udp_socket.recvfrom(65536)  # Depuis Unity
```

### 2. Décodage eHuB (Étape 2)
```python
decoded_entities = self.ehub_decoder.decode_packet(packet_data)
```

### 3. Mapping DMX (Étape 3)  
```python
universes = self.dmx_pipeline.process_entities(decoded_entities)
```

### 4. Envoi ArtNet (Étape 4)
```python
success = self.artnet_sender.send_dmx_universes(universes)
```

## 📈 Monitoring et performances

### Statistiques temps réel
- Paquets eHuB reçus
- Entités décodées et mappées
- Frames envoyées vers BC216
- Taux d'erreurs ArtNet
- FPS moyen

### Affichage périodique
```
📊 [Pipeline] Stats après 45.2s:
   📦 Paquets reçus: 1247
   🎨 Entités traitées: 156,025
   📺 Frames envoyées LED: 1247
   📤 Paquets ArtNet: 159,616
   ❌ Erreurs envoi: 0
   🎯 FPS moyen: 27.6
```

## 🛠️ Dépendances

### Modules Python
- `socket` : Communication UDP
- `struct` : Manipulation données binaires
- `threading` : Gestion concurrentielle
- `pathlib` : Gestion chemins fichiers

### Étapes précédentes
- `etape-02-decodage-ehub/ehub_complete_pipeline_decoder.py`
- `etape-03-mapping-dmx/ehub_complete_pipeline_mapping_dmx.py`

## 🧪 Tests disponibles

### `test_etape_4.py`
1. **Test pipeline complet** avec données eHuB simulées
2. **Test envoi ArtNet direct** vers BC216 (validation)

### Validation manuelle
Les scripts `test_artnet_direct.py` et `test_simple_artnet.py` peuvent être utilisés pour valider la communication avec l'écran LED réel.

## ⚠️ Notes importantes

### Réseau
- S'assurer que WSL peut atteindre 192.168.1.45-48
- Port 6454 ouvert sur les contrôleurs BC216
- Pas de conflit avec d'autres logiciels ArtNet

### Performance  
- Pipeline optimisé pour ~30 FPS
- Gestion automatique des erreurs réseau
- Monitoring mémoire et CPU

### Mode Simulateur
Pour les tests sans hardware :
```python
pipeline = EHubArtNetPipeline(LedMode.SIMULATOR)
```

## 🎯 Validation

L'Étape 4 est considérée comme **validée** si :
- ✅ Pipeline s'initialise sans erreur
- ✅ Réception UDP depuis Unity fonctionnelle  
- ✅ Décodage eHuB (Étape 2) opérationnel
- ✅ Mapping DMX (Étape 3) opérationnel
- ✅ Envoi ArtNet vers BC216 réussi
- ✅ Affichage visible sur écran LED réel
- ✅ Statistiques cohérentes et stables

## 🚀 Prochaines étapes

L'Étape 4 complète le pipeline principal. Les améliorations futures peuvent inclure :
- Optimisations performances
- Interface de monitoring web
- Support protocoles additionnels
- Gestion multiple écrans
