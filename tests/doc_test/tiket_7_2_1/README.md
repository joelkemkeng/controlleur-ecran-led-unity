# Ticket 7.2.1 – Application Intégrée Finale du Pipeline LED

## 1. **But du ticket**

**Assembler et valider l'intégration complète de tous les modules du pipeline LED** :  
- Parsing eHuB (UDP, GZip, UPDATE/CONFIG)
- Mapping dynamique entités → DMX (aucun hardcoding, basé sur la config réelle)
- Application des patchs DMX dynamiques (PatchHandler)
- Envoi ArtNet (multi-contrôleurs, limitation FPS)
- Monitoring temps réel (logs, stats, debug)
- Interface utilisateur simple (stats, patches, arrêt)
- Gestion d'erreur robuste et logs pédagogiques

**Objectif** :  
Avoir une application principale (`main.py`) qui orchestre tout le pipeline, prête à être utilisée, testée, déployée, et comprise par un débutant.

---

## 2. **Importance pour le projet**

- **Cœur du système** : c'est le point d'entrée qui fait fonctionner toute l'architecture.
- **Robustesse** : garantit que chaque module fonctionne bien ensemble, sans bug caché.
- **Pédagogie** : permet à n'importe qui (même sans expérience) de comprendre, tester, et déboguer le pipeline.
- **Portabilité** : assure que le système fonctionne sur Windows, Linux, Mac, Raspbian, sans manipulation complexe.
- **Déploiement réel** : c'est ce code qui sera utilisé sur le vrai mur LED, en conditions de production.

---

## 3. **Explication détaillée de l'intégration**

### a) **Initialisation**

- **Chargement de la configuration avancée** (AdvancedConfigManager)
    - Vérification de la cohérence (pas de chevauchement d'entités, univers valides)
    - Affichage d'un message d'erreur explicite si la config est invalide

- **Initialisation des modules**
    - `EHubReceiver` : écoute UDP sur le port/univers défini
    - `EntityMapper` : mapping dynamique, reconstruit à chaque message CONFIG
    - `PatchHandler` : chargement des patchs depuis `patches.csv` (ou vide si absent)
    - `ArtNetSender` : envoi DMX, limitation du taux de trame (max_fps)
    - `MonitoringDisplay` : logs temps réel, stats, debug

- **Exemple de sortie console**
    ```
    🚀 Initialisation du routeur LED...
    ✅ 2 patches chargés
    ✅ Initialisation terminée
    ```

---

### b) **Pipeline de traitement**

#### **Message CONFIG**
- Parsing du message, extraction des plages dynamiques (ex : 170, 89, 170, 89…)
- Reconstruction du mapping entité→DMX (aucune valeur codée en dur)
- Log du nombre de plages, détails, confirmation mapping
- **Exemple de sortie**
    ```
    [CONFIG] Reçu 3 plages de configuration
      Plage: payload 0-169 = entités 100-269
      Plage: payload 0-89 = entités 270-358
      Plage: payload 0-169 = entités 400-569
    🔄 Configuration mise à jour: 3 plages
    ```

#### **Message UPDATE**
- Parsing des entités (ID, RGBW)
- Log du nombre d'entités, premiers exemples
- Mapping dynamique entité→DMX (en utilisant la config/plages courantes)
- Log des paquets DMX générés, premiers exemples
- Application des patchs (si activé)
- Log des patchs appliqués, détails si besoin
- Envoi ArtNet (avec gestion du taux de trame)
- Log des paquets envoyés, stats ArtNet
- **Exemple de sortie**
    ```
    [UPDATE] Reçu 1223 entités
      Entité 100: RGB(255,0,0)
      Entité 101: RGB(0,255,0)
      Entité 102: RGB(0,0,255)
    [DMX] 8 paquets générés
      192.168.1.45 U0: Ch1=255, Ch2=0, Ch3=0
    [ArtNet] Envoyé vers 1 contrôleurs
    ```

#### **Monitoring/statistiques**
- Affichage périodique (toutes les 10s) : nombre de messages, entités, paquets, canaux, contrôleurs touchés, etc.
- **Exemple de sortie**
    ```
    === STATISTIQUES ===
    eHuB: 2 msg, 1223 entités
    DMX: 8 paquets, 24 canaux
    ArtNet: 8 envois vers 1 contrôleurs
    ==================
    ```

#### **Interface utilisateur**
- Commandes :  
    - `s` + Entrée : afficher les stats
    - `p` + Entrée : afficher les patches actifs
    - `q` + Entrée : quitter proprement
- **Exemple de session**
    ```
    COMMANDES DISPONIBLES:
      's' + Enter : Afficher les statistiques
      'p' + Enter : Afficher les patches actifs
      'q' + Enter : Quitter
    ```

---

### c) **Gestion d'erreur et logs**

- **Chaque étape** (initialisation, update, config, patch, envoi) est entourée de `try/except`
- En cas d'erreur, un message explicite est affiché, exemple :
    ```
    ❌ Erreur traitement UPDATE: KeyError: 1234
    ❌ Erreur traitement CONFIG: ValueError: Plage incohérente
    ```
- Les erreurs de parsing, de réseau, de mapping, etc. sont toutes loguées avec le contexte.

---

### d) **Robustesse et portabilité**

- Fonctionne sur tous les OS (aucune dépendance exotique)
- Arrêt propre : gestion du `KeyboardInterrupt`, fermeture des sockets, sauvegarde si besoin
- Documentation pdoc générée automatiquement, avec exemples concrets

---

## 4. **Comment tester concrètement**

### **Lancer le pipeline**
```bash
python main.py
```

### **Simuler des messages eHuB**
```bash
python tools/debug_tools.py
```
- Choisir un test séquentiel ou couleur pour voir le pipeline en action

### **Afficher la configuration active**
```bash
python tools/show_config.py
```

### **Vérifier la connectivité réseau**
```bash
python tools/check_network.py
```

### **Exporter un template Excel du mapping**
```python
from config.advanced_config import AdvancedConfigManager
mgr = AdvancedConfigManager()
mgr.export_excel_template('template_mapping.xlsx')
```

---

## 5. **Exemples de cas réels**

- **Cas 1 : Un contrôleur tombe en panne**
    - Ajouter un patch pour rediriger les canaux défaillants vers un autre univers/canal
    - Sauvegarder le patch, le rejouer à la demande

- **Cas 2 : Changement de configuration (nouvelle plage, nouvel univers)**
    - Envoyer un message CONFIG avec les nouvelles plages
    - Le mapping est reconstruit dynamiquement, sans redémarrer le pipeline

- **Cas 3 : Débogage sur le terrain**
    - Utiliser la commande `s` pour voir les stats en temps réel
    - Utiliser la commande `p` pour vérifier les patchs actifs

---

## 6. **Conseils et bonnes pratiques**

- **Toujours valider la configuration** avant de lancer le pipeline (voir logs d'initialisation)
- **Ne jamais coder en dur** les tailles de plages, univers, etc. : tout doit venir de la config ou des messages reçus
- **Utiliser les outils de test** pour simuler des messages et vérifier le pipeline sans matériel réel
- **Lire les logs et les stats** pour diagnostiquer rapidement tout problème
- **Consulter la documentation pdoc** pour comprendre chaque module, chaque classe, chaque méthode

---

## 7. **Conclusion**

Cette étape est **fondamentale** : elle garantit que tout le pipeline LED fonctionne de façon cohérente, robuste, et pédagogique.  
Grâce à cette intégration, le projet est prêt pour :
- Les tests sur le vrai mur LED
- Le déploiement sur n'importe quelle plateforme
- L'onboarding de nouveaux développeurs ou techniciens, même débutants

**Bravo, tu as maintenant un pipeline LED professionnel, documenté, et prêt à l'emploi !**

---

**Si tu veux des schémas Mermaid, des diagrammes UML, ou des cas d'usage encore plus détaillés, demande-le-moi : je peux enrichir cette doc à volonté !** 