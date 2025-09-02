# 🎭 Tests Fonctionnels ArtNet - Étape 3

## ✅ Scripts Validés avec l'Écran LED Réel

Ce dossier contient les scripts de test ArtNet qui ont été **validés avec succès** sur l'écran LED réel.

### 📁 Contenu

#### `test_artnet_direct.py` ⭐
**Script complet avec animations**
- ✅ Testé et validé sur écran LED
- 🎨 Séquence complète : Noir → Rouge → Vert → Bleu → Blanc → Dégradé → Animation
- 📡 128 paquets ArtNet par frame (4 contrôleurs × 32 univers)
- 🎮 Adaptation du code Windows fonctionnel pour WSL Ubuntu
- 📊 Performance : ~4000 paquets/seconde

#### `test_simple_artnet.py` ⚡
**Script simple et rapide**
- ✅ Testé et validé sur écran LED  
- 🎨 Test couleurs de base : Noir → Rouge → Vert → Bleu → Blanc
- 📡 Code simplifié pour tests rapides
- ⚡ Idéal pour vérifications ponctuelles

### 🎯 Utilisation

```bash
# Test complet avec animations
cd tests-fonctionnel
python3 test_artnet_direct.py

# Test rapide couleurs de base
python3 test_simple_artnet.py
```

### 🌐 Configuration Réseau

**Contrôleurs BC216 :**
- 192.168.1.45:6454 (Contrôleur 1)
- 192.168.1.46:6454 (Contrôleur 2)  
- 192.168.1.47:6454 (Contrôleur 3)
- 192.168.1.48:6454 (Contrôleur 4)

**Format ArtNet :**
- Port : 6454 (standard Art-Net)
- Protocole : UDP
- Taille paquet : 530 bytes (18 header + 512 DMX)

### 🎨 Écran LED 128×128

**Architecture physique :**
- 64 bandes de 259 LEDs chacune
- Mapping serpentin (montée/descente)
- 4 contrôleurs de 32 univers chacun
- Total : 16 384 LEDs (128×128)

### ✅ Validation

**Tests réussis :**
- ✅ Communication réseau opérationnelle
- ✅ Format ArtNet correct  
- ✅ Couleurs affichées correctement
- ✅ Animations fluides
- ✅ Extinction/allumage fonctionnel
- ✅ Performance temps réel

---

🎉 **Scripts prêts pour intégration au pipeline complet !**
