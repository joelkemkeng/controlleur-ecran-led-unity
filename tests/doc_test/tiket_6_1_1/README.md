# Ticket 6.1.1 – Système de patches DMX dynamique et historisé

## Objectif
Mettre en place un système de patchs DMX permettant de rediriger dynamiquement les canaux (ex : 1→389) sans modifier la configuration globale, avec gestion de l'historique et possibilité de rejouer un patch à la demande.

## Importance pour le projet
- Permet de contourner rapidement une panne physique sur le terrain sans toucher à la config Excel ou au mapping principal.
- Historise chaque patch appliqué pour pouvoir rejouer ou documenter les interventions.
- Indispensable pour la robustesse et la maintenance des grandes installations LED.

## Explication détaillée
La classe `PatchHandler` permet de :
- Charger/sauvegarder des patchs depuis/vers un fichier CSV (format simple, lisible, portable)
- Appliquer dynamiquement les patchs sur les paquets DMX (avant envoi ArtNet)
- Activer/désactiver le patching à la volée (`enabled`)
- Ajouter/supprimer des patchs dynamiquement
- Enregistrer chaque patch appliqué dans un dossier `patch_record/` avec timestamp
- Rejouer un patch au choix ou le dernier patch appliqué

## Format CSV attendu
```csv
Source_Channel,Target_Channel
1,389
2,390
```
- **Première ligne** : en-tête (obligatoire)
- **Lignes suivantes** : chaque ligne = un patch (canal source → canal cible)

## Comment tester concrètement
1. Lancer les tests unitaires :
   ```bash
   pytest tests/test_patch_handler.py
   ```
2. Les tests vérifient :
   - Ajout, suppression, application de patchs
   - Sauvegarde/chargement CSV
   - Enregistrement et replay d'un patch dans l'historique
   - Désactivation du patching
3. Pour tester en vrai :
   - Créer un fichier `patches.csv` avec le format ci-dessus
   - Charger le patch dans le pipeline principal
   - Activer le patching (`handler.enabled = True`)
   - Observer l'effet sur les canaux DMX envoyés

## Exemples concrets de cas réels
- **Cas 1 :** Un circuit DMX tombe en panne (ex : 1 et 2). On recâble pour que 389 et 390 prennent la relève, on crée un patch-map (1→389, 2→390), on l'active, et tout fonctionne sans toucher au mapping global.
- **Cas 2 :** On veut documenter toutes les interventions : chaque patch appliqué est enregistré automatiquement dans `patch_record/` avec la date et l'heure.
- **Cas 3 :** On veut rejouer un patch précédent (ex : après une coupure de courant) : il suffit de recharger le fichier CSV correspondant.

## Portabilité et conseils pratiques
- Fonctionne sur Linux, Mac, Windows, Raspbian sans modification.
- Format CSV universel, éditable à la main ou avec Excel.
- Le dossier `patch_record/` est créé automatiquement si besoin.
- Pour rejouer le dernier patch appliqué : `handler.replay_patch()`
- Pour rejouer un patch précis : `handler.replay_patch('patch_record/patch_YYYY-MM-DD_HH-MM-SS.csv')`

## Intégration dans le pipeline principal et usage au lancement

- **Activation automatique** :
  - Au lancement du programme (`python main.py`), le système charge automatiquement le dernier patch appliqué (s'il existe dans `patch_record/`) ou un patch par défaut (`patches.csv`).
  - Le patching est activé par défaut (`enabled = True`).
  - À chaque message UPDATE, le patch est appliqué juste avant l'envoi ArtNet (voir TODO dans le code principal).

- **Rejouer un patch précis** :
  ```python
  patch_handler.replay_patch('patch_record/patch_YYYY-MM-DD_HH-MM-SS.csv')
  ```
- **Rejouer le dernier patch appliqué** :
  ```python
  patch_handler.replay_patch()
  ```
- **Désactiver le patching** :
  ```python
  patch_handler.enabled = False
  ```

- **Exemple d'intégration dans le pipeline** :
  ```python
  dmx_packets = mapper.map_entities_to_dmx(entities)
  patched_packets = patch_handler.apply_patches(dmx_packets)
  artnet_sender.send_dmx_packets(patched_packets)
  ```

Tout est documenté dans le code principal (`main.py`) pour guider l'utilisateur pas à pas.

## Modes d'exécution et utilisation des paramètres

Le programme principal (`main.py`) peut être lancé de plusieurs façons selon le besoin de patching :

- **Mode normal (pipeline complet)** :
    ```bash
    python main.py
    ```
    → Démarre le pipeline, écoute les messages eHuB, applique le patch par défaut (`patches.csv`) si présent.

- **Rejouer le dernier patch enregistré** :
    ```bash
    python main.py --replay-patch
    ```
    → Recharge et applique automatiquement le dernier patch enregistré dans le dossier `patch_record/`.

- **Rejouer un patch spécifique** :
    ```bash
    python main.py --replay-patch nom_du_patch.csv
    ```
    → Recharge et applique le patch spécifié (par nom de fichier, ex : `patch_2024-06-21_15-30-00.csv`).

- **Désactiver le patching** (dans le code ou en modifiant l'attribut) :
    ```python
    app.patch_handler.enabled = False
    ```

**Paramètres** :
- `--replay-patch` : (optionnel) Si présent, rejoue le dernier patch enregistré. Si un nom de fichier est donné, rejoue ce patch précis.
- Aucun paramètre : pipeline normal, patch par défaut si présent.

**Effet sur le pipeline** :
- Le patch est appliqué juste avant l'envoi ArtNet, après le mapping DMX.
- Si aucun patch n'est trouvé, le pipeline fonctionne sans patching.

Tout est documenté dans le code principal (`main.py`) pour guider l'utilisateur pas à pas.

---

**Prochaine étape :** Intégrer le PatchHandler dans le pipeline principal, et documenter chaque intervention pour la traçabilité. 