# 🎧 Moniteur eHub

Module de réception et monitoring des données eHub en temps réel.

## 📁 Fichiers

- `ehub_monitor.py` - Moniteur complet avec stats détaillées
- `simple_ehub_receiver.py` - Récepteur simple et léger
- `start_ehub_monitor.py` - Menu de sélection interactif

## 🚀 Utilisation Rapide

### Option 1: Menu Interactif (Recommandé)
```bash
python start_ehub_monitor.py
```
Puis sélectionnez votre mode de monitoring.

### Option 2: Moniteur Complet
```bash
python ehub_monitor.py
```

### Option 3: Récepteur Simple
```bash
python simple_ehub_receiver.py
```

## ⚙️ Configuration

### Changer le Port
```bash
python ehub_monitor.py 9999          # Écouter sur port 9999
python simple_ehub_receiver.py 9999  # Version simple sur port 9999
```

### Changer l'IP et le Port
```bash
python ehub_monitor.py 8765 192.168.1.100  # IP spécifique
```

## 📊 Affichage

### Moniteur Complet
```
📦 [10:47:32.123] Paquet #5
   👤 Expéditeur: 127.0.0.1:52341
   📏 Taille: 245 bytes
   🔢 Entités: 25
   🎨 Entités reçues:
      #   1: 🟥 R:255 G:  0 B:  0
      #   2: 🟩 R:  0 G:255 B:  0
      #   3: 🟦 R:  0 G:  0 B:255
      ... et 22 autres entités
   📊 Stats: 5 pkt | 125 ent | 10 FPS | 12.3s
```

### Récepteur Simple
```
[10:47:32] Paquet #5: 25 entités (245 bytes) de 127.0.0.1
   #1: R255 G  0 B  0
   #2: R  0 G255 B  0
   #3: R  0 G  0 B255
   ... et 22 autres
```

## 🎯 Test avec Votre Logiciel

1. **Lancez le moniteur:**
   ```bash
   python ehub_monitor.py
   ```

2. **Lancez votre logiciel LED principal**

3. **Chargez votre fichier Excel** (Configuration → Sélectionner fichier)

4. **Démarrez le système** (bouton ▶ Démarrer)

5. **Activez eHub Monitor** (bouton 📡 eHub Monitor)

6. **Lancez une animation** ou un jeu

7. **Observez les données** dans le moniteur !

## 🔍 Que Surveiller

### ✅ Bon Fonctionnement
- Paquets reçus régulièrement
- Entités avec valeurs RGB cohérentes
- FPS stable (10-45 FPS)
- Pas d'erreurs

### ❌ Problèmes Possibles
- **Aucun paquet:** Vérifiez que eHub Monitor est activé
- **0 entités:** Fichier Excel non chargé ou mapping vide
- **Erreurs décodage:** Format de paquet incorrect
- **FPS irrégulier:** Problème de performance

## 🛠️ Dépannage

**"Address already in use"**
- Port déjà utilisé → Utilisez un port différent
- Arrêtez l'autre application ou changez de port

**"No module named 'core.ehub'"**
- Lancez depuis le bon répertoire
- Vérifiez que le dossier `core/` existe

**"Permission denied"**
- Port privilégié → Utilisez un port > 1024
- Lancez en administrateur si nécessaire

## 🎮 Exemples d'Utilisation

### Test avec Pong
1. Lancez le moniteur
2. Dans votre logiciel: Page Pong → Démarrer jeu
3. Vous devriez voir les entités de la balle et des raquettes

### Test avec Animation
1. Lancez le moniteur  
2. Dans votre logiciel: Page Animations → Lancer animation
3. Vous devriez voir les entités colorées de l'animation

### Debug du Mapping
Si vous voyez "0 entités" mais l'animation fonctionne:
- Vérifiez que le fichier Excel est chargé
- Vérifiez le format du fichier (colonnes ID, X, Y)
- Consultez les logs de mapping au démarrage
