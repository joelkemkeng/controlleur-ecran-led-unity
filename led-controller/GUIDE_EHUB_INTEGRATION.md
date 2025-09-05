# 🚀 Guide d'Intégration eHub

Ce guide explique comment ajouter l'émission de données eHub à votre logiciel LED actuel pour tester le monitoring.

## 📁 Fichiers Ajoutés

- `core/ehub_sender.py` - Module émetteur eHub
- `ehub_integration.py` - Module d'intégration simple  
- `test_ehub_sender.py` - Script de test émetteur
- `test_ehub_receiver.py` - Script de test récepteur

## 🚀 Test Rapide

### 1. Tester la Communication eHub

**Terminal 1 - Récepteur (logs détaillés):**
```bash
python test_ehub_receiver.py
```

**Terminal 2 - Émetteur (envoi de test):**
```bash
python test_ehub_sender.py basic
```

Vous devriez voir des logs détaillés dans le récepteur !

### 2. Tests Disponibles

```bash
# Test basique (quelques entités colorées)
python test_ehub_sender.py basic

# Test arc-en-ciel (50 entités multicolores)
python test_ehub_sender.py rainbow

# Test continu (10 secondes de flux)
python test_ehub_sender.py continuous

# Test simulation jeu (raquettes + balle)
python test_ehub_sender.py integration
```

## 🔗 Intégration dans Votre Logiciel Actuel

### Option 1: Intégration Simple (Recommandée)

Ajoutez ces lignes à votre code existant :

```python
# Au début du fichier
from ehub_integration import enable_ehub_output, send_frame_to_ehub

# Dans votre fonction d'initialisation
enable_ehub_output()  # Active l'envoi eHub

# Dans votre boucle de rendu (là où vous envoyez vers Art-Net)
def your_render_function(frame):
    # Votre code existant
    self._send_frame_to_artnet(frame)
    
    # NOUVEAU: Envoi vers eHub aussi
    send_frame_to_ehub(frame)
```

### Option 2: Intégration pour les Jeux

Pour les jeux (Pong, Snake, Tetris), ajoutez :

```python
# Au début du fichier
from ehub_integration import send_pixels_to_ehub

# Dans votre logique de jeu
def update_game_display(self):
    pixels = []
    
    # Exemple pour Pong
    # Balle
    pixels.append((self.ball_x, self.ball_y, 255, 0, 0))  # Rouge
    
    # Raquettes
    for i in range(10):
        pixels.append((5, self.paddle1_y + i, 0, 255, 0))    # Vert gauche
        pixels.append((120, self.paddle2_y + i, 0, 255, 0))  # Vert droite
    
    # Envoyer vers eHub
    send_pixels_to_ehub(pixels)
```

### Option 3: Intégration Avancée

```python
from ehub_integration import EHubIntegrator

class YourLEDController:
    def __init__(self):
        # Votre code existant
        self.ehub = EHubIntegrator("127.0.0.1", 8765)
        self.ehub.start_integration()
    
    def render_frame(self, frame):
        # Votre code existant
        # ...
        
        # Envoi vers eHub
        self.ehub.update_frame(frame)
```

## 🎯 Test avec Votre Logiciel

### 1. Lancez le Récepteur de Test
```bash
python test_ehub_receiver.py
```

### 2. Modifiez Votre Code
Ajoutez quelques lignes d'intégration (voir exemples ci-dessus)

### 3. Lancez Votre Logiciel
Démarrez votre application LED normale

### 4. Observez les Logs
Le récepteur devrait afficher :
- ✅ Paquets reçus avec timestamp
- ✅ Nombre d'entités par paquet  
- ✅ Valeurs RGB des premières entités
- ✅ Statistiques de débit

## 📊 Exemple de Logs Attendus

```
📦 [14:32:15.123] Paquet reçu de 127.0.0.1:52341
   📏 Taille: 245 bytes
   🔢 Entités: 25
   🎨 Premières entités:
      #   1: R:255 G:  0 B:  0
      #   2: R:  0 G:255 B:  0
      #   3: R:  0 G:  0 B:255
      #   4: R:255 G:255 B:  0
      #   5: R:255 G:  0 B:255
      ... et 20 autres

============================================================
📊 STATISTIQUES  
   ⏱️  Durée: 12.3s
   📦 Paquets reçus: 123
   🔢 Entités reçues: 2540
   ❌ Erreurs: 0
   📈 Débit paquets: 10.0 pkt/s
   📈 Débit entités: 206.5 ent/s
============================================================
```

## 🔧 Configuration

### Changer le Port
```python
# Dans le récepteur
python test_ehub_receiver.py 9999

# Dans l'émetteur  
enable_ehub_output("127.0.0.1", 9999)
```

### Changer l'IP Cible
```python
# Pour envoyer vers un autre PC
enable_ehub_output("192.168.1.100", 8765)
```

## 🚀 Prochaines Étapes

Une fois que vous voyez des données dans les logs :

1. ✅ **Communication fonctionne** - Vos données arrivent !
2. 🎯 **Créer le logiciel de routage V2** - Avec interface monitoring avancée
3. 📊 **Implémenter les exigences manquantes** - Patching, ArtNet monitor, etc.

## ❓ Dépannage

**"Aucune donnée reçue"**
- Vérifiez que le port n'est pas utilisé
- Vérifiez l'IP/port dans votre intégration
- Vérifiez que votre logiciel appelle bien les fonctions d'envoi

**"Erreur socket"**  
- Port déjà utilisé → Changez le port
- Permissions réseau → Lancez en administrateur

**"Données corrompues"**
- Vérifiez la version de Python (recommandé: 3.8+)
- Vérifiez les dépendances (struct, gzip)

## 📝 Todo Technique

- [ ] Test de la première communication
- [ ] Intégration dans un jeu (Pong/Snake/Tetris)  
- [ ] Vérification du format des données
- [ ] Mesure des performances (FPS, latence)
- [ ] Préparation du logiciel de routage V2
