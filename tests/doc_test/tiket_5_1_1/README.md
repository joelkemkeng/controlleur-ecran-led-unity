# Ticket 5.1.1 – Monitoring Console temps réel

## Comment activer et voir le monitoring ?

- **Activation automatique** :
  Dès que tu crées une instance de `MonitoringDisplay` et que tu appelles ses méthodes (`log_ehub_data`, `log_dmx_data`, `log_artnet_send`, `display_stats`), les logs s'affichent automatiquement dans la console.

- **Affichage** :
  Les logs apparaissent en temps réel dans la console où tu exécutes ton application (ex : `python main.py`).

- **Désactivation/activation dynamique** :
  Tu peux désactiver ou réactiver chaque type de monitoring à tout moment :
  ```python
  monitor.ehub_enabled = False   # Désactive l'affichage eHuB
  monitor.dmx_enabled = True     # Active l'affichage DMX
  monitor.artnet_enabled = True  # Active l'affichage ArtNet
  ```
  Quand un moniteur est désactivé, rien ne s'affiche pour cette étape.

- **Exemple d'intégration dans le pipeline** :
  ```python
  from monitoring.display import MonitoringDisplay
  monitor = MonitoringDisplay()

  def handle_update(entities):
      monitor.log_ehub_data(entities)
      dmx_packets = mapper.map_entities_to_dmx(entities)
      monitor.log_dmx_data(dmx_packets)
      artnet_sender.send_dmx_packets(dmx_packets)
      monitor.log_artnet_send(dmx_packets)
  ```

## Objectif
Mettre en place un système d'affichage temps réel du pipeline LED (eHuB, DMX, ArtNet) via la classe `MonitoringDisplay`, pour diagnostiquer rapidement les problèmes de mapping, de routage ou de réseau.

## Importance pour le projet
- Permet de visualiser en direct le flux de données à chaque étape du pipeline.
- Facilite le débogage lors des tests sur le vrai mur LED ou en simulation.
- Indispensable pour garantir la robustesse et la compréhension du système, même pour un débutant.

## Explication détaillée
La classe `MonitoringDisplay` permet de logger et d'afficher :
- Les entités reçues via eHuB (ID, couleurs)
- Les paquets DMX générés (univers, canaux, valeurs)
- Les paquets envoyés via ArtNet (IP, univers)
- Les statistiques globales (nombre de messages, entités, paquets, etc.)

Chaque type de monitoring peut être activé/désactivé dynamiquement (attributs `ehub_enabled`, `dmx_enabled`, `artnet_enabled`).

**Exemple d'utilisation :**
```python
from monitoring.display import MonitoringDisplay
monitor = MonitoringDisplay()
monitor.log_ehub_data([EntityUpdate(1,255,0,0,0)])
monitor.log_dmx_data([DMXPacket('192.168.1.45',0,{1:255,2:0,3:0})])
monitor.log_artnet_send([DMXPacket('192.168.1.45',0,{1:255,2:0,3:0})])
monitor.display_stats()
```

## Comment tester concrètement
1. Lancer les tests unitaires :
   ```bash
   pytest tests/test_monitoring_display.py
   ```
2. Le test `test_monitoring_display_basic` vérifie :
   - Que les compteurs augmentent correctement
   - Que l'affichage ne plante pas
   - Que l'activation/désactivation fonctionne
3. Pour tester en vrai :
   - Intégrer `MonitoringDisplay` dans le pipeline principal
   - Observer la console lors de la réception de messages eHuB, du mapping DMX, et de l'envoi ArtNet

## Exemples concrets de cas réels
- **Cas 1 :** On reçoit 10 entités eHuB, le monitoring affiche les IDs et couleurs → on vérifie la cohérence avec le mapping Excel.
- **Cas 2 :** Un univers DMX ne reçoit pas de données, le monitoring DMX permet de voir si le mapping est correct ou s'il manque des entités.
- **Cas 3 :** Un contrôleur ArtNet ne reçoit rien, le monitoring ArtNet permet de vérifier si les paquets sont bien envoyés à la bonne IP.

## Portabilité et conseils pratiques
- Fonctionne sur Linux, Mac, Windows, Raspbian sans modification.
- Peut être utilisé en mode console SSH ou sur un laptop de test.
- Pour les grandes installations, permet de surveiller en temps réel l'activité de chaque contrôleur.

## Format de retour du monitoring et comment le lire

Chaque appel à une méthode de log du monitoring affiche une ou plusieurs lignes dans la console, au format suivant :

- [eHuB] <N> entités reçues
    Entité <id>: RGB(<r>,<g>,<b>)
  Exemple :
    [eHuB] 2 entités reçues
      Entité 1: RGB(255,0,0)
      Entité 2: RGB(0,255,0)

- [DMX] <N> paquets générés
    <IP> U<univers>: Ch<canal>=<valeur>, Ch<canal>=<valeur>, ...
  Exemple :
    [DMX] 1 paquets générés
      192.168.1.45 U0: Ch1=255, Ch2=0, Ch3=0

- [ArtNet] Envoyé vers <N> contrôleurs
  Exemple :
    [ArtNet] Envoyé vers 1 contrôleurs

- === STATISTIQUES ===
    eHuB: <nb_msg> msg, <nb_entités> entités
    DMX: <nb_paquets> paquets, <nb_canaux> canaux
    ArtNet: <nb_envois> envois vers <nb_ctrl> contrôleurs
  Exemple :
    === STATISTIQUES ===
    eHuB: 2 msg, 4 entités
    DMX: 2 paquets, 6 canaux
    ArtNet: 2 envois vers 1 contrôleurs
    ==================

### Comment lire ces logs (explication pédagogique)
- **[eHuB]** : Affiche le nombre d'entités reçues et leurs couleurs. Permet de vérifier que le parsing fonctionne et que les IDs/couleurs sont cohérents avec la config réelle.
- **[DMX]** : Affiche le nombre de paquets DMX générés, l'IP du contrôleur, l'univers DMX, et les premiers canaux modifiés. Permet de vérifier le mapping entité → DMX.
- **[ArtNet]** : Affiche combien de contrôleurs ont reçu des paquets ArtNet. Permet de vérifier que l'envoi réseau fonctionne.
- **STATISTIQUES** : Affiche un résumé global de l'activité depuis le démarrage (nombre de messages, entités, paquets, etc.).

**Conseil** : Si une étape ne s'affiche pas, vérifier que le moniteur correspondant est activé (`ehub_enabled`, `dmx_enabled`, `artnet_enabled`).

Ce format est conçu pour être lisible d'un coup d'œil, même pour un débutant, et pour permettre de repérer rapidement les problèmes (ex : entités non mappées, paquets non envoyés, etc).

---

**Prochaine étape :** Passer à l'intégration du monitoring dans l'application principale, ou à l'ajout de logs avancés (fichiers, alertes, etc.) si besoin. 