# Ticket 8.2.1 – Outils de débogage eHuB/LED (tools/debug_tools.py)

## 1. **But du ticket**

Fournir un outil de débogage interactif permettant de :
- Générer et envoyer des messages eHuB UPDATE simulés (séquentiel, balayage couleur, entité unique)
- Envoyer un message CONFIG conforme à la configuration réelle (mapping complet)
- Vérifier l'environnement et les prérequis (checklist automatique)

**Objectif** : Permettre de tester le pipeline LED sans Unity, valider le mapping, le patching, la configuration, et faciliter l'onboarding/débogage terrain.

---

## 2. **Importance pour le projet**

- **Indispensable pour tester le pipeline sans matériel Unity**
- **Permet de valider la configuration réelle (mapping, plages, patchs)**
- **Facilite le debug terrain et l'onboarding débutant**
- **Assure la portabilité et la robustesse du système**

---

## 3. **Explication détaillée des fonctionnalités**

### a) Génération de messages UPDATE
- Test séquentiel (chenillard) : allume une série d'entités une à une
- Test balayage couleurs : envoie différentes couleurs sur plusieurs entités
- Test entité unique : permet de choisir une entité et une couleur à envoyer

### b) Envoi d'un message CONFIG réel
- Envoie un message CONFIG conforme au tableau de mapping réel (toutes les plages, codées en dur)
- Permet d'initialiser le mapping dynamique du pipeline comme sur le terrain

### c) Checklist de prérequis
- Vérifie la version de Python, la présence des fichiers essentiels, la disponibilité du port UDP, la présence du dossier patch_record, etc.
- Affiche des messages pédagogiques et des solutions concrètes en cas de problème

---

## 4. **Comment utiliser l'outil de debug**

```bash
python tools/debug_tools.py
```

Menu interactif :
```
1. Test séquentiel (chenillard)
2. Test balayage couleurs
3. Test entité unique
4. Checklist de prérequis
5. Envoyer message CONFIG réel (full mapping)
q. Quitter
```

- **Toujours commencer par l'option 5** pour envoyer le message CONFIG réel avant d'envoyer des UPDATE !
- Utiliser ensuite les options 1, 2 ou 3 pour simuler des entités et tester le pipeline.
- L'option 4 permet de vérifier que tout l'environnement est prêt avant de commencer.

---

## 5. **Exemples concrets de cas réels**

- **Test du mapping** :
    1. Envoyer le message CONFIG réel (option 5)
    2. Envoyer un chenillard (option 1) pour vérifier que chaque LED s'allume au bon endroit
- **Test d'un patch** :
    1. Appliquer un patch dans le pipeline
    2. Envoyer un UPDATE sur l'entité concernée (option 3)
    3. Vérifier que la redirection fonctionne
- **Debug terrain** :
    1. Lancer la checklist (option 4) pour s'assurer que tout est prêt
    2. Envoyer des UPDATE pour diagnostiquer un problème

---

## 6. **Conseils pédagogiques et bonnes pratiques**

- **Toujours envoyer un message CONFIG avant les UPDATE** pour initialiser le mapping
- **Lire les logs [DEBUG]** pour comprendre ce qui est envoyé et reçu
- **Utiliser la checklist** pour éviter les erreurs de setup
- **Documenter chaque test ou manipulation dans le README de la tâche**
- **Consulter la documentation pdoc pour comprendre chaque fonction**

---

## 7. **Portabilité et robustesse**

- Fonctionne sur Windows, Linux, Mac, Raspbian
- Nécessite uniquement Python 3.7+ (aucune dépendance exotique)
- Les messages sont conformes au protocole eHuB utilisé dans tout le projet

---

## 8. **Checklist de validation de la tâche**

- [x] Génération de messages UPDATE (séquentiel, couleur, unique)
- [x] Envoi d'un message CONFIG réel (full mapping)
- [x] Checklist automatique des prérequis
- [x] Documentation pdoc et README pédagogique
- [x] Portabilité testée sur plusieurs OS

---

**Bravo, tu as maintenant un outil de debug complet, pédagogique, et prêt pour tous les tests et déploiements terrain !** 