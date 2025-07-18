# Ticket 8.1.1 – Test d'intégration complet du pipeline LED

## Note sur la cohérence et la robustesse

Avant toute correction ou ajout, **une analyse complète du code source a été réalisée** pour garantir que :
- Les tests utilisent strictement les fonctions et classes existantes (ex : parsing via `ehub/parser.py`, initialisation explicite du mapping, etc.)
- Aucun doublon, aucun appel à une méthode ou un attribut inexistant
- Les conventions et interfaces publiques du projet sont respectées
- Les tests fonctionnent sans matériel ni réseau, en simulation pure

---

## 1. **But du ticket**

Valider, par des tests d'intégration automatisés, le bon fonctionnement du pipeline LED dans son ensemble :
- Parsing eHuB
- Mapping dynamique entités → DMX
- Application des patchs
- Envoi ArtNet
- Performance

**Objectif** : garantir que tous les modules fonctionnent ensemble, sans bug, et que le pipeline est robuste et performant.

---

## 2. **Importance pour le projet**

- **Validation globale** : s'assurer que l'intégration de tous les modules est correcte
- **Robustesse** : détecter les régressions ou bugs d'intégration
- **Pédagogie** : fournir des exemples concrets de tests pour l'onboarding
- **Performance** : vérifier que le pipeline tient la charge (1000 entités en <10ms)

---

## 3. **Explication détaillée des tests**

### a) Test du pipeline complet eHuB → DMX → ArtNet
- Crée un message UPDATE eHuB simulé (2 entités)
- Parse et traite le message via le pipeline (en utilisant `parse_update_message` du module `ehub/parser.py`)
- Vérifie que le mapping DMX et l'envoi ArtNet sont corrects
- **Exemple de sortie console**
    ```
    [UPDATE] Reçu 2 entités
    [DMX] 1 paquets générés
    [ArtNet] Envoyé vers 1 contrôleurs
    ```

### b) Test de l'application des patchs
- Ajoute un patch (canal 1 → 389)
- Vérifie que la redirection est bien appliquée dans le mapping DMX

### c) Test de performance
- Crée 1000 entités
- Vérifie que le mapping DMX est effectué en moins de 10ms
- Vérifie que toutes les entités sont bien mappées

---

## 4. **Comment exécuter les tests**

```bash
python -m unittest tests/integration_test.py
```

**Exemple de sortie**
```
Test du pipeline complet eHuB -> DMX -> ArtNet ... OK
Test de l'application des patches ... OK
Test de performance avec beaucoup d'entités ... OK
```

---

## 4bis. **Exemple de log détaillé**

Pour mieux comprendre ce qui se passe lors des tests, voici un exemple de log enrichi :

```
[TEST] 2 entités envoyées, 1 paquet DMX généré, 0 patchs actifs
[UPDATE] Reçu 2 entités
[DMX] 1 paquets générés
[ArtNet] Envoyé vers 1 contrôleurs
```

Dans le test de patch :
```
[TEST] Patch ajouté : 1→389
[TEST] Patchs actifs : {1: 389}
```

Dans le test de performance :
```
[TEST] 1000 entités envoyées, X paquets DMX générés, 0 patchs actifs
```

---

## 4ter. **Tester l'enregistrement et le chargement de patchs**

Pour tester l'enregistrement d'un patch (et vérifier que le dossier `patch_record/` est bien créé automatiquement) :

```python
# Ajout d'un patch
self.router.patch_handler.add_patch(1, 389)
# Enregistrement du patch dans l'historique
self.router.patch_handler.record_patch()  # Crée patch_record/ si besoin
```

Pour charger un patch enregistré :

```python
# Rejouer le dernier patch enregistré
self.router.patch_handler.replay_patch()
# Ou charger un patch précis
self.router.patch_handler.replay_patch('patch_record/patch_YYYY-MM-DD_HH-MM-SS.csv')
```

Après ces opérations, tu peux vérifier le nombre de patchs actifs :
```python
print(f"Patchs actifs : {self.router.patch_handler.patches}")
```

---

## 5. **Conseils pédagogiques et bonnes pratiques**

- Lire les docstrings pdoc dans `tests/integration_test.py` pour comprendre chaque test
- S'inspirer de ces tests pour écrire d'autres tests d'intégration ou de non-régression
- Utiliser ces tests pour valider toute évolution du pipeline (refacto, ajout de fonctionnalité, etc.)
- Ne jamais modifier le pipeline sans relancer ces tests

---

## 6. **Conclusion**

Cette étape garantit que le pipeline LED est **fiable, robuste, et performant**.  
Elle permet de détecter rapidement toute régression et de valider l'intégration de tous les modules.

**Bravo, tu as maintenant un pipeline LED testé de bout en bout !**

---

**Pour toute question, se référer à la documentation pdoc ou aux autres README de tâches dans `tests/doc_test/`.** 