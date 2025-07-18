# Ticket 2.3.1 – Application principale (main.py)

## Objectif
Créer le point d’entrée principal du projet, qui initialise tous les composants (ConfigManager, EHubReceiver, etc.), lance l’écoute des messages eHuB, et prépare l’intégration future du mapping, du routage, du monitoring, etc.

## Ce que fait ce ticket
- Implémente la classe `LEDRoutingApp` dans `main.py`.
- Initialise la configuration réelle (config/config.json)
- Démarre le récepteur eHuB (port, univers)
- Affiche en console les messages UPDATE et CONFIG reçus (nombre d’entités, plages, exemples)
- Prépare les hooks pour intégrer le mapping DMX/ArtNet et le monitoring
- Docstring pdoc claire et exemples d’utilisation

## Pourquoi c'est important
- Point d’entrée unique et clair pour tout le pipeline
- Permet de tester l’intégration des composants (config, réseau, parsing)
- Sert de base à l’intégration future du mapping, du routage, du monitoring, etc.
- Facilite la maintenance et la compréhension du projet

## Comment tester concrètement
1. Lancer l’application principale :
   ```bash
   .\venv\Scripts\activate
   python main.py
   ```
2. Envoyer un message eHuB UPDATE ou CONFIG (ex : avec un script de test ou un outil UDP)
3. Observer la sortie console :
   - Affichage du nombre d’entités reçues (UPDATE)
   - Affichage du nombre de plages reçues (CONFIG)
   - Affichage des 3 premiers éléments de chaque type
4. Arrêter l’application avec Ctrl+C

## Exemples concrets
```python
# Lancer l’application
python main.py

# Exemple de sortie console réelle
Démarrage du routeur LED...
En attente de messages eHuB... (Ctrl+C pour arrêter)
[UPDATE] Reçu 1223 entités
  Entité 100: RGBW(255,0,0,0)
  Entité 101: RGBW(0,255,0,0)
  Entité 102: RGBW(0,0,255,0)
[CONFIG] Reçu 65 plages de configuration
  Plage: payload 0-169 = entités 100-269
  Plage: payload 0-89 = entités 270-358
  Plage: payload 0-169 = entités 400-569
```

## Lien avec le pipeline global
- Cette application principale est le socle sur lequel seront intégrés le mapping entités→DMX, le routage ArtNet, le monitoring, etc.
- Elle respecte la structure et la logique du plan de développement et du contexte technique du projet.

---

## Prochaine étape
Intégrer le mapping entités→DMX (Epic 3) et le routage ArtNet dans le pipeline principal. 