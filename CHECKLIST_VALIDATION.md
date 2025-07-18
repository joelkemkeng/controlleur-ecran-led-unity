# ✅ Checklist de Validation Complète du Workflow LED

## 🔍 Vérification du Workflow Complet

### Étape 1 : Réception eHuB (UDP)
- [ ] Port UDP 8765 ouvert et en écoute
- [ ] Filtrage correct par univers eHuB
- [ ] Reception messages UPDATE (type=2) et CONFIG (type=1)
- [ ] Parsing header eHuB (signature, type, taille)
- [ ] Décompression GZip des payloads

### Étape 2 : Parsing des Messages
- [ ] Messages UPDATE → List[EntityUpdate]
- [ ] Messages CONFIG → List[EntityRange]
- [ ] Validation des structures binaires
- [ ] Gestion des erreurs de parsing

### Étape 3 : Mapping Entités → DMX (🚨 PROBLÈME CRITIQUE)
- [ ] **build_mapping()** construit le mapping correctement
- [ ] **Calcul correct des univers DMX** (170 LEDs par univers)
- [ ] **Calcul correct des canaux DMX** (1-512, 3 canaux RGB)
- [ ] **Validation des limites DMX** (pas de dépassement)
- [ ] **Matching correct entités → contrôleurs**

### Étape 4 : Application des Patches DMX
- [ ] Patches chargés depuis patches.csv
- [ ] Redirection des canaux défaillants
- [ ] Activation/désactivation des patches

### Étape 5 : Envoi ArtNet
- [ ] Création paquets ArtNet valides
- [ ] Envoi vers IPs contrôleurs corrects
- [ ] Limitation taux de trame (40 FPS)
- [ ] Gestion des sockets UDP

### Étape 6 : Monitoring
- [ ] Logs eHuB (entités reçues)
- [ ] Logs DMX (paquets générés)
- [ ] Logs ArtNet (envois contrôleurs)
- [ ] Statistiques temps réel

## 🚨 Problèmes Identifiés

### CRITIQUE - Mapping EntityMapper
**Fichier**: `mapping/entity_mapper.py`

**Problème 1** : Logique d'univers incorrecte (lignes 59-72)
```python
# INCORRECT (ligne 62)
plage_index = ctrl.universes.index(plage.payload_start)
```

**Problème 2** : Calcul canaux DMX incorrect (ligne 72)
```python
# INCORRECT - i est la position dans la plage, pas dans l'univers
channel = (i * 3) + 1
```

**Problème 3** : Pas de validation des limites DMX
- Aucune vérification que les canaux ≤ 512
- Aucune validation des valeurs RGB (0-255)

## 🔧 Corrections Nécessaires

### 1. Corriger build_mapping()
```python
def build_mapping(self, entity_ranges: Dict[int, EntityRange]):
    self.entity_to_dmx.clear()
    
    for plage in entity_ranges.values():
        for ctrl_name, ctrl in self.config.controllers.items():
            if ctrl.start_entity <= plage.entity_start and plage.entity_end <= ctrl.end_entity:
                nb_leds = plage.entity_end - plage.entity_start + 1
                
                # Calcul correct de l'offset dans le contrôleur
                entity_offset = plage.entity_start - ctrl.start_entity
                
                for i in range(nb_leds):
                    entity_id = plage.entity_start + i
                    current_offset = entity_offset + i
                    
                    # Calcul correct de l'univers (170 LEDs par univers)
                    universe_index = current_offset // 170
                    led_position_in_universe = current_offset % 170
                    
                    if universe_index < len(ctrl.universes):
                        universe = ctrl.universes[universe_index]
                        channel_start = (led_position_in_universe * 3) + 1
                        
                        # Validation des limites DMX
                        if channel_start + 2 <= 512:
                            self.entity_to_dmx[entity_id] = {
                                'controller_ip': ctrl.ip,
                                'universe': universe,
                                'r_channel': channel_start,
                                'g_channel': channel_start + 1,
                                'b_channel': channel_start + 2,
                            }
                break
```

### 2. Ajouter validation dans map_entities_to_dmx()
```python
def map_entities_to_dmx(self, entities: List[EntityUpdate]) -> List[DMXPacket]:
    dmx_packets = {}
    
    for entity in entities:
        # Validation RGB
        if not (0 <= entity.r <= 255 and 0 <= entity.g <= 255 and 0 <= entity.b <= 255):
            print(f"Valeurs RGB invalides pour entité {entity.id}")
            continue
            
        if entity.id not in self.entity_to_dmx:
            continue
            
        mapping = self.entity_to_dmx[entity.id]
        
        # Validation canaux DMX
        if any(ch > 512 for ch in [mapping['r_channel'], mapping['g_channel'], mapping['b_channel']]):
            print(f"Canaux DMX > 512 pour entité {entity.id}")
            continue
        
        # Création paquet DMX...
```

## 🧪 Tests de Validation

### Test 1 : Mapping basique
```python
def test_mapping_basic():
    # Tester entité 100 → contrôleur 1, univers 0, canaux 1-3
    # Tester entité 5100 → contrôleur 2, univers 32, canaux 1-3
    pass
```

### Test 2 : Limites DMX
```python
def test_dmx_limits():
    # Tester qu'aucun canal ne dépasse 512
    # Tester que les valeurs RGB sont 0-255
    pass
```

### Test 3 : Workflow complet
```python
def test_full_workflow():
    # 1. Envoyer message CONFIG
    # 2. Vérifier mapping construit
    # 3. Envoyer message UPDATE
    # 4. Vérifier paquets DMX générés
    # 5. Vérifier envoi ArtNet
    pass
```

## 📋 Checklist avant Déploiement

### Configuration
- [ ] config.json valide (4 contrôleurs, plages entités)
- [ ] Réseau configuré (192.168.1.45-48 accessibles)
- [ ] Port UDP 8765 ouvert

### Fonctionnalités
- [ ] Messages CONFIG traités correctement
- [ ] Messages UPDATE mappés correctement
- [ ] Paquets ArtNet envoyés aux bonnes IPs
- [ ] Monitoring fonctionnel

### Performance
- [ ] Pas de dépassement mémoire
- [ ] Taux de trame respecté (40 FPS)
- [ ] Latence acceptable (< 25ms)

### Debugging
- [ ] Logs détaillés activés
- [ ] Validation du mapping avec option 'v'
- [ ] Tests des 4 contrôleurs

## 🎯 Validation Finale

**Avant mise en production** :
1. **Corriger EntityMapper** (priorité critique)
2. **Tester le mapping** avec données réelles
3. **Valider les 4 contrôleurs** avec animations
4. **Vérifier les logs** pour détecter les erreurs
5. **Tester en conditions réelles** (réseau, latence)

**Commande de validation** :
```bash
python demo/animation_demo.py
# Choisir option 'v' pour validation complète
# Choisir option 7 pour test tous contrôleurs
```

---
**Status** : 🚨 **CORRECTIONS CRITIQUES NÉCESSAIRES**
L'EntityMapper doit être corrigé avant mise en production.