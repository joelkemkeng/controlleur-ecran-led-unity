# Récepteur de Données eHub

## Rôle et Objectif

Ce script Python (`receive_ehub.py`) est un outil de diagnostic et de développement conçu pour intercepter et analyser les données transmises par le système eHub en temps réel. Il agit comme un moniteur réseau spécialisé pour comprendre le format et la structure des données eHub.

## Importance dans le Projet

### Debugging et Développement
- **Validation des données** : Vérifier que les données eHub sont correctement transmises
- **Analyse du protocole** : Comprendre la structure et le format des paquets eHub
- **Détection d'anomalies** : Identifier les problèmes de transmission ou de corruption des données

### Intégration Système
- **Interface de test** : Tester la communication entre eHub et le contrôleur d'écran LED
- **Monitoring en temps réel** : Surveiller le flux de données pendant le développement
- **Documentation du protocole** : Analyser et documenter le format des messages eHub

## Niveau d'Action sur le Projet

### Architecture Réseau
```
eHub → UDP (127.0.0.1:8765) → receive_ehub.py → Console (Affichage)
                            → Contrôleur LED Unity (Production)
```

### Impact sur les Composants
1. **Couche Réseau** : Analyse du trafic UDP entre eHub et le système
2. **Couche Application** : Compréhension du protocole eHub pour l'intégration Unity
3. **Couche Debug** : Outil de diagnostic pour le développement et la maintenance

## Comment l'Exécuter

### Prérequis
- Python 3.x installé
- Port UDP 8765 disponible
- eHub configuré pour transmettre sur 127.0.0.1:8765

### Commandes d'Exécution
```bash
# Se placer dans le dossier
cd labo_test/receive_ehub_data/

# Exécuter le script
python receive_ehub.py

# Ou avec Python 3 explicitement
python3 receive_ehub.py
```

### Arrêt du Script
- Appuyer sur `Ctrl+C` pour arrêter le script proprement

## Types de Réponses en Sortie

### Démarrage Normal
```
Démarrage du récepteur de données eHub...
Écoute sur 127.0.0.1:8765
En attente de données eHub...
```

### Réception de Données
```
--- Données reçues de ('192.168.1.100', 12345) ---
Données brutes: b'\x01\x02\x03\x04...'
Taille: 256 bytes
Données décodées: {"type":"screen_data","values":[...]}
```

### Données Binaires
```
--- Données reçues de ('192.168.1.100', 12345) ---
Données brutes: b'\xff\xfe\xfd\xfc...'
Taille: 512 bytes
Données binaires (non décodables en UTF-8)
```

### Gestion des Erreurs
```
Erreur: [Errno 98] Address already in use
```

### Arrêt Propre
```
Arrêt du récepteur...
Socket fermé.
```

## Utilisation pour le Développement

### Analyse des Données
1. **Format JSON** : Si les données sont en JSON, elles seront affichées lisiblement
2. **Données binaires** : Affichage hexadécimal pour l'analyse des protocoles binaires
3. **Métadonnées** : Adresse source, taille des paquets, timestamp implicite

### Intégration avec Unity
Les informations collectées par ce script peuvent être utilisées pour :
- Développer le parser de données eHub dans Unity
- Optimiser la taille des buffers de réception
- Valider la fréquence de transmission
- Tester différents scénarios de données

## Configuration Avancée

Pour modifier le comportement du script :
- **Port d'écoute** : Modifier `UDP_PORT = 8765`
- **Adresse IP** : Modifier `UDP_IP = "127.0.0.1"`
- **Taille du buffer** : Ajuster `sock.recvfrom(64*1024)`

## Troubleshooting

### Port Déjà Utilisé
Si le port 8765 est occupé, modifier la configuration ou arrêter l'autre application.

### Aucune Donnée Reçue
1. Vérifier que eHub transmet bien sur 127.0.0.1:8765
2. Vérifier la configuration réseau
3. Tester avec un autre port

### Données Corrompues
Si les données semblent corrompues, vérifier :
- L'endianness des données binaires
- L'encodage des chaînes de caractères
- La synchronisation des paquets