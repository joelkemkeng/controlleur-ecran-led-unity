# Ticket 9.1.1 – Démonstration artistique LED (demo/animation_demo.py)

## 1. **But du ticket**

Fournir un script de démonstration artistique permettant de :
- Générer des animations LED (vague de couleur, arc-en-ciel, chenillard, pulsation)
- Utiliser le pipeline existant (mapping, patchs, monitoring, etc.)
- Proposer un menu interactif pour choisir l'animation
- Gérer les erreurs proprement et documenter chaque étape

**Objectif** : Permettre de valider visuellement le pipeline, de présenter le projet, et de tester la réactivité et la cohérence de l'installation LED.

---

## 2. **Importance pour le projet**

- **Validation visuelle** du pipeline complet (mapping, patchs, ArtNet, etc.)
- **Outil de présentation/démo** pour jury, profs, ou clients
- **Test de performance et de réactivité** en conditions réelles
- **Facilite l'onboarding et la compréhension du pipeline**

---

## 3. **Explication détaillée des fonctionnalités**

- **Animations proposées** :
    - Vague de couleur (sinus)
    - Arc-en-ciel rotatif
    - Chenillard (LED qui défile)
    - Pulsation globale
- **Menu interactif** pour choisir l'animation à lancer
- **Utilisation du pipeline existant** (`IntegratedLEDRouter`, `EntityUpdate`)
- **Gestion d'erreur robuste** : chaque animation est protégée, logs clairs en cas de souci
- **Arrêt propre** du pipeline même en cas d'erreur ou d'interruption

---

## 4. **Comment utiliser la démonstration**

```bash
python demo/animation_demo.py
```

Menu interactif :
```
1. Vague de couleur
2. Arc-en-ciel rotatif
3. Chenillard
4. Pulsation globale
q. Quitter la démo
```

- Choisir l'animation à lancer (1-4)
- Appuyer sur `q` pour quitter proprement

---

## 5. **Exemples concrets de cas réels**

- **Test de mapping** : lancer une vague ou un chenillard pour vérifier que chaque LED s'allume au bon endroit
- **Test de patch** : appliquer un patch, lancer une animation, vérifier la redirection
- **Présentation** : lancer l'arc-en-ciel ou la pulsation pour montrer la fluidité et la synchronisation

---

## 6. **Conseils pédagogiques et bonnes pratiques**

- **Toujours initialiser le pipeline avant de lancer une animation**
- **Lire les logs pour comprendre le déroulement de chaque animation**
- **Arrêter proprement la démo avec `q` ou Ctrl+C**
- **Documenter chaque test ou démo dans le README de la tâche**
- **Consulter la documentation pdoc pour comprendre chaque fonction**

---

## 7. **Portabilité et robustesse**

- Fonctionne sur Windows, Linux, Mac, Raspbian
- Nécessite uniquement Python 3.7+ (aucune dépendance exotique)
- Utilise le pipeline et le mapping réels (aucun hardcoding inutile)
- Gestion d'erreur et logs pédagogiques pour chaque animation

---

## 8. **Checklist de validation de la tâche**

- [x] Génération d'animations variées (vague, arc-en-ciel, chenillard, pulsation)
- [x] Utilisation du pipeline existant (mapping, patchs, monitoring)
- [x] Menu interactif et arrêt propre
- [x] Gestion d'erreur robuste et logs pédagogiques
- [x] Documentation pdoc et README pédagogique
- [x] Portabilité testée sur plusieurs OS

---

**Bravo, tu as maintenant une démo artistique complète, pédagogique, et prête pour la présentation ou la validation finale du projet !** 