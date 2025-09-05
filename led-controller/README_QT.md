# Interface PyQt - Contrôleur LED

## Description

Interface graphique moderne et nodale pour le contrôleur LED, inspirée d'Emitter Hub. Cette interface permet de contrôler le backend eHub → Art-Net de manière intuitive et visuelle.

## Fonctionnalités

### 🎛️ Interface Nodale
- **Nœuds connectables** : Ajoutez et configurez des modules selon vos besoins
- **Workflow visuel** : Suivez le flux de données de manière intuitive
- **Configuration flexible** : Adaptez l'interface à votre setup

### 📡 Modules Disponibles

#### eHub Receiver
- **Port** : Configurez le port d'écoute (défaut: 8765)
- **Universe** : Définissez l'univers eHub
- **Status** : Visualisez l'état de la connexion

#### Excel Config
- **Sélection de fichier** : Chargez votre fichier de configuration Excel
- **Validation** : Vérification automatique du format
- **Status** : Confirmation du chargement

#### Art-Net Sender
- **IP** : Adresse du contrôleur Art-Net
- **Universe** : Univers Art-Net de destination
- **Status** : État de l'envoi

#### Data Monitor
- **Logs en temps réel** : Visualisez les données reçues et envoyées
- **Historique** : Gardez une trace des événements
- **Nettoyage** : Effacez les logs si nécessaire

### 📊 Monitoring
- **Statistiques en temps réel** :
  - Paquets eHub reçus
  - Entités traitées
  - Paquets Art-Net envoyés
- **Gestion d'erreurs** : Notifications visuelles des problèmes

## Installation

### Prérequis
```bash
pip install -r requirements.txt
```

### Lancement
```bash
python main_qt.py
```

## Utilisation

### 1. Configuration Initiale

1. **Ajoutez un nœud Excel Config**
   - Cliquez sur "+ Excel Config" dans le panneau de gauche
   - Sélectionnez votre fichier Excel de configuration

2. **Ajoutez un nœud eHub Receiver**
   - Cliquez sur "+ eHub Receiver"
   - Configurez le port et l'univers selon votre setup

3. **Ajoutez un nœud Art-Net Sender** (optionnel)
   - Pour des configurations avancées
   - Définissez l'IP et l'univers de destination

4. **Ajoutez un nœud Data Monitor**
   - Pour surveiller le trafic de données
   - Visualisez les logs en temps réel

### 2. Démarrage du Système

1. **Vérifiez la configuration** :
   - Assurez-vous qu'un fichier Excel est sélectionné
   - Vérifiez les paramètres des nœuds

2. **Démarrez le système** :
   - Cliquez sur "Démarrer" dans le panneau de gauche
   - Le système commence à écouter les données eHub

3. **Surveillez l'activité** :
   - Observez les statistiques dans le panneau de droite
   - Consultez les logs dans le Data Monitor

### 3. Arrêt du Système

- Cliquez sur "Arrêter" pour interrompre le traitement
- Tous les nœuds retournent à leur état d'arrêt

## Architecture Technique

### Backend Integration
L'interface utilise directement les modules backend :
- `core.ehub` : Traitement des paquets eHub
- `core.artnet` : Envoi des paquets Art-Net
- `core.excel` : Chargement de la configuration

### Threading
- **Thread principal** : Interface utilisateur
- **Thread de réception** : Écoute eHub en arrière-plan
- **Signaux PyQt** : Communication thread-safe entre backend et interface

### Gestion des Erreurs
- **Validation des données** : Vérification des formats
- **Gestion des exceptions** : Messages d'erreur explicites
- **Recovery automatique** : Tentatives de reconnexion

## Personnalisation

### Ajout de Nouveaux Nœuds
Pour ajouter un nouveau type de nœud :

1. Créez une classe héritant de `NodeWidget`
2. Implémentez `create_content()` et `get_config()`
3. Ajoutez le bouton d'ajout dans `create_left_panel()`

### Modification du Style
Le style sombre peut être personnalisé en modifiant les feuilles de style CSS dans le code.

## Dépannage

### Problèmes Courants

**"Erreur chargement Excel"**
- Vérifiez que le fichier Excel existe
- Assurez-vous qu'il contient les colonnes requises

**"Erreur socket"**
- Vérifiez que le port n'est pas déjà utilisé
- Assurez-vous d'avoir les permissions réseau

**"Erreur réception"**
- Vérifiez que la source eHub envoie bien des données
- Contrôlez le format des paquets

### Logs
Consultez les logs dans le Data Monitor pour diagnostiquer les problèmes.

## Support

Pour toute question ou problème, consultez la documentation du backend ou contactez l'équipe de développement. 