# Routeur LED - Documentation Générale

Ce projet est un pipeline complet de routage LED pour installations artistiques, conçu pour être **modulaire, portable, robuste et pédagogique**.

---

## 0. Structure du projet

- `code/` : modules principaux (parsing, mapping, patch, monitoring, etc.)
- `tools/` : scripts utilitaires (réseau, config, parsing, debug)
- `demo/` : scripts de démonstration artistique (animations LED)
- `tests/` : tests unitaires et d'intégration
- `tests/doc_test/` : documentation détaillée par ticket/fonctionnalité
- `patch_record/` : historique des patchs DMX
- `html/` : documentation web générée (pdoc)

---

## 1. Vue d'ensemble du pipeline

Le pipeline LED intègre :
- **Réception eHuB** (UDP, GZip, UPDATE/CONFIG)
- **Parsing dynamique** des messages
- **Mapping entités → DMX** (aucun hardcoding, basé sur la config réelle)
- **Application des patchs DMX dynamiques** (PatchHandler)
- **Envoi ArtNet** (multi-contrôleurs, limitation FPS)
- **Monitoring temps réel** (logs, stats, debug)
- **Interface utilisateur simple** (stats, patches, arrêt)
- **Gestion d'erreur robuste** et logs pédagogiques

**Portabilité** : Windows, Linux, Mac, Raspbian. Aucun module exotique requis (sauf pandas/openpyxl pour l'export Excel).

---

## 2. Installation et setup

### Clonage du projet
```bash
git clone <url-du-repo>
cd CONTROLLEUR-LED
```

### Création et activation de l'environnement virtuel
```bash
python -m venv venv
# Windows :
venv\Scripts\activate
# Linux/Mac :
source venv/bin/activate
```

### Installation des dépendances
```bash
pip install -r requirements.txt
# Pour l'export Excel (optionnel) :
pip install pandas openpyxl
```

---

## 3. Lancement du pipeline principal

```bash
python main.py
```
- Démarre l'écoute des messages eHuB, applique le patch par défaut si présent.
- Pour rejouer le dernier patch :
  ```bash
  python main.py --replay-patch
  ```
- Pour rejouer un patch spécifique :
  ```bash
  python main.py --replay-patch patch_YYYY-MM-DD_HH-MM-SS.csv
  ```

### Exemple de session console
```
🚀 Initialisation du routeur LED...
✅ 2 patches chargés
✅ Initialisation terminée
🎯 Routeur démarré - En attente de messages eHuB...
📊 Affichage des stats toutes les 10 secondes
🔧 Fichiers: config.json, patches.csv
==================================================
COMMANDES DISPONIBLES:
  's' + Enter : Afficher les statistiques
  'p' + Enter : Afficher les patches actifs
  'q' + Enter : Quitter
==================================================
[CONFIG] Reçu 3 plages de configuration
  Plage: payload 0-169 = entités 100-269
  Plage: payload 0-89 = entités 270-358
  Plage: payload 0-169 = entités 400-569
[UPDATE] Reçu 1223 entités
  Entité 100: RGB(255,0,0)
  Entité 101: RGB(0,255,0)
  Entité 102: RGB(0,0,255)
[DMX] 8 paquets générés
  192.168.1.45 U0: Ch1=255, Ch2=0, Ch3=0
[ArtNet] Envoyé vers 1 contrôleurs
=== STATISTIQUES ===
eHuB: 2 msg, 1223 entités
DMX: 8 paquets, 24 canaux
ArtNet: 8 envois vers 1 contrôleurs
==================
```

---

## 3bis. Démo artistique (animations LED)

Pour lancer la démo artistique (vague, arc-en-ciel, chenillard, pulsation) :
```bash
python demo/animation_demo.py
```
- Utilise le pipeline réel, sans matériel nécessaire (simulation).
- Permet de valider le mapping, le routage, et la performance.
- Voir la doc pdoc de `demo/animation_demo.py` pour les options et exemples.

---

## 4. Génération et consultation de la documentation pdoc

### Sous Windows (PowerShell)
```bash
./generate_doc.ps1
```
### Sous Linux/Mac
```bash
bash generate_doc.sh
```
- Ouvre le dossier `html/` généré dans un navigateur (ouvrir `html/index.html`).
- Toutes les classes, scripts et modules sont documentés (pdoc).

---

## 5. Configuration avancée (validation, export Excel)

- Pour valider la cohérence de la config :
  ```python
  from config.advanced_config import AdvancedConfigManager
  mgr = AdvancedConfigManager()
  assert mgr.validate_config()
  ```
- Pour exporter un template Excel :
  ```python
  mgr.export_excel_template('template_mapping.xlsx')
  ```

---

## 6. Test de connectivité réseau

```bash
python tools/check_network.py
```
- Affiche [OK] ou [FAIL] pour chaque IP de contrôleur (test UDP ArtNet 6454).

---

## 7. Affichage de la configuration utilisée

```bash
python tools/show_config.py
```
- Affiche tous les contrôleurs, plages d'entités, univers, IP, etc.

---

## 8. Utilisation et lecture du monitoring

- Le monitoring s'affiche automatiquement dans la console lors de l'exécution du pipeline.
- Pour désactiver/activer un type de monitoring :
  ```python
  monitor.ehub_enabled = False
  monitor.dmx_enabled = True
  monitor.artnet_enabled = True
  ```
- Voir la doc pdoc de `monitoring/display.py` pour plus d'exemples.

---

## 9. Parsing manuel d'un message CONFIG

```bash
python tools/parse_config_message.py --file message_config.bin
# ou
python tools/parse_config_message.py --hex "65487542010001000600..."
```
- Affiche les plages d'entités extraites du message CONFIG.

---

## 10. Utilisation du patching (replay, désactivation, etc.)

- Pour rejouer le dernier patch :
  ```bash
  python main.py --replay-patch
  ```
- Pour rejouer un patch précis :
  ```bash
  python main.py --replay-patch patch_YYYY-MM-DD_HH-MM-SS.csv
  ```
- Pour désactiver le patching dans le code :
  ```python
  app.patch_handler.enabled = False
  ```
- Voir la doc pdoc de `patching/handler.py` pour plus d'exemples.

---

## 11. Comment tester concrètement le pipeline

- Lancer le pipeline :
  ```bash
  python main.py
  ```
- Simuler des messages eHuB :
  ```bash
  python tools/debug_tools.py
  ```
- Afficher la configuration active :
  ```bash
  python tools/show_config.py
  ```
- Vérifier la connectivité réseau :
  ```bash
  python tools/check_network.py
  ```
- Exporter un template Excel du mapping :
  ```python
  from config.advanced_config import AdvancedConfigManager
  mgr = AdvancedConfigManager()
  mgr.export_excel_template('template_mapping.xlsx')
  ```

---

## 12. Conseils, bonnes pratiques et cas réels d'usage

- Toujours valider la config avant déploiement réel.
- Tester la connectivité réseau avant chaque show.
- Utiliser le monitoring pour diagnostiquer les problèmes en temps réel.
- Documenter chaque patch appliqué (le système enregistre automatiquement l'historique dans `patch_record/`).
- Utiliser les scripts utilitaires pour vérifier la config, le réseau, ou parser des messages à la main.
- **Cas 1 :** Un contrôleur tombe en panne → ajouter un patch pour rediriger les canaux défaillants, sauvegarder/rejouer le patch.
- **Cas 2 :** Changement de configuration (nouvelle plage, nouvel univers) → envoyer un message CONFIG, le mapping est reconstruit dynamiquement.
- **Cas 3 :** Débogage sur le terrain → utiliser la commande `s` pour voir les stats, `p` pour les patchs actifs.

---

## 13. Liens utiles

- Documentation web générée (pdoc) : ouvrir `html/index.html` après génération
- Documentation détaillée de l'intégration finale : `tests/doc_test/tiket_7_2_1/README.md`
- Scripts utilitaires :
  - `tools/check_network.py` : test réseau
  - `tools/show_config.py` : affichage config
  - `tools/parse_config_message.py` : parsing manuel CONFIG
  - `tools/debug_tools.py` : génération/simulation de messages eHuB
  - `demo/animation_demo.py` : démo artistique (animations LED)

---

## 14. Tests automatisés (unitaires, intégration, démo)

Pour lancer tous les tests :
```bash
pytest tests
```
- Tous les tests doivent passer (unitaires, intégration, outils, démo).
- Les résultats s'affichent en console : chaque test correspond à un module ou une fonctionnalité clé.
- Les tests couvrent : parsing eHuB, mapping, patch system, ArtNet, monitoring, outils utilitaires, démo artistique, etc.
- Pour plus de détails, voir les fichiers dans `tests/` et la doc pdoc.

---

## 15. Portabilité et conseils Raspberry Pi

- Le projet fonctionne sur Windows, Linux, Mac, et **Raspberry Pi (Raspbian)** sans adaptation particulière.
- Vérifier simplement que Python 3.8+ est installé, ainsi que les dépendances (`pip install -r requirements.txt`).
- Les scripts utilitaires et le pipeline principal sont testés sur Raspberry Pi (modèle 3B+ et 4).

---

## 16. Liens utiles (mis à jour)

- Documentation web générée (pdoc) : ouvrir `html/index.html` après génération
- Documentation détaillée de l'intégration finale : `tests/doc_test/tiket_7_2_1/README.md`
- Scripts utilitaires :
  - `tools/check_network.py` : test réseau
  - `tools/show_config.py` : affichage config
  - `tools/parse_config_message.py` : parsing manuel CONFIG
  - `tools/debug_tools.py` : génération/simulation de messages eHuB
  - `demo/animation_demo.py` : démo artistique (animations LED)
- Tests automatisés : voir `tests/` et lancer `pytest tests`

---

**Pour toute question, se référer à la documentation pdoc (ouvrir `html/index.html`), aux README de chaque tâche dans `tests/doc_test/`, ou poser la question à l'assistant.** 