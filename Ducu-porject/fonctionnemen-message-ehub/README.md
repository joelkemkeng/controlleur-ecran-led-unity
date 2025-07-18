# Fonctionnement des messages eHuB

## 1. Introduction

Ce document explique de façon claire et concrète comment fonctionnent les messages eHuB dans le projet de contrôleur LED, la différence entre univers eHuB, univers ArtNet, contrôleur, et la logique de mapping. Il s'adresse à toute personne débutante ou souhaitant comprendre le pipeline de bout en bout.

---

## 2. Les concepts clés

### **Contrôleur**
- Un boîtier physique (ex : BC216) qui pilote un groupe de LEDs.
- Chaque contrôleur a une **adresse IP** unique (ex : 192.168.1.45).
- Chaque contrôleur gère plusieurs univers ArtNet (souvent 32).

### **Univers ArtNet**
- Un univers DMX512 (0 à 127) = 512 canaux DMX = 170 LEDs RGB max.
- Chaque univers ArtNet est associé à un segment de LEDs sur un contrôleur.

### **Univers eHuB**
- Un **groupe logique** de contrôleurs (ex : tout le mur LED principal).
- Permet de filtrer les messages sur le réseau.
- Un message eHuB peut configurer plusieurs univers ArtNet sur plusieurs contrôleurs.

---

## 3. Les types de messages eHuB

### **Message CONFIG**
- Sert à transmettre la **configuration du mapping** (qui va où ?).
- Contient une liste de **plages** (une par univers ArtNet).
- Fréquence : **1 Hz** (rare, seulement si la topologie change).

**Structure d'une plage :**
- `payload_start` : position de début dans le payload UPDATE
- `entity_start` : ID de la première LED de la plage
- `payload_end` : position de fin dans le payload UPDATE
- `entity_end` : ID de la dernière LED de la plage
- (souvent, chaque plage = 1 univers ArtNet sur 1 contrôleur)

**Exemple :**
| Plage | payload_start | entity_start | payload_end | entity_end | ArtNet IP      | ArtNet Universe |
|-------|--------------|-------------|-------------|------------|---------------|----------------|
| 1     | 0            | 100         | 169         | 269        | 192.168.1.45  | 0              |
| 2     | 0            | 270         | 89          | 358        | 192.168.1.45  | 1              |


### **Message UPDATE**
- Sert à transmettre les **valeurs à afficher** (R,G,B,W) pour chaque LED.
- Contient une suite de blocs (ID, R, G, B, W) pour chaque entité.
- Fréquence : **40 Hz** (animation fluide).

**Exemple de payload UPDATE :**
| Position | ID  | R   | G   | B   | W   |
|----------|-----|-----|-----|-----|-----|
| 0        | 100 | 255 | 0   | 0   | 0   |
| 1        | 101 | 0   | 255 | 0   | 0   |
| ...      | ... | ... | ... | ... | ... |

---

## 4. Pipeline de traitement

1. **Réception du message CONFIG**
   - Le routeur mémorise le mapping entre positions du payload UPDATE et IDs d'entités, pour chaque univers ArtNet et chaque contrôleur.
2. **Réception du message UPDATE**
   - Le routeur lit chaque bloc du payload UPDATE, retrouve à quelle LED (ID) et à quel contrôleur/univers ArtNet il correspond grâce au mapping mémorisé.
   - Il prépare les paquets DMX/ArtNet et les envoie aux bonnes adresses IP/Univers.

---

## 5. Schéma textuel

```
Message CONFIG (Univers eHuB = 1)
┌──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│ Plage       │ payload_start│ entity_start │ payload_end  │ entity_end   │ ArtNet IP    │ ArtNet Univ. │
├──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ 1           │ 0            │ 100          │ 169          │ 269          │ 192.168.1.45 │ 0            │
│ 2           │ 0            │ 270          │ 89           │ 358          │ 192.168.1.45 │ 1            │
│ ...         │ ...          │ ...          │ ...          │ ...          │ ...          │ ...          │
└──────────────┴──────────────┴──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘

Message UPDATE (Univers eHuB = 1)
┌──────────┬─────┬─────┬─────┬─────┐
│ Position │ ID  │ R   │ G   │ B   │
├──────────┼─────┼─────┼─────┼─────┤
│ 0        │ 100 │ 255 │ 0   │ 0   │
│ 1        │ 101 │ 0   │ 255 │ 0   │
│ ...      │ ... │ ... │ ... │ ... │
└──────────┴─────┴─────┴─────┴─────┘

Le mapping CONFIG permet de savoir que la position 0 du payload UPDATE correspond à l'entité 100 sur l'univers ArtNet 0 du contrôleur 192.168.1.45, etc.
```

---

## 6. FAQ et points de vigilance

- **Univers eHuB ≠ Univers ArtNet** :
  - Univers eHuB = groupe logique pour filtrer les messages
  - Univers ArtNet = univers DMX512 physique sur un contrôleur
- **Un message CONFIG peut configurer plusieurs univers ArtNet et plusieurs contrôleurs**
- **Le mapping est dynamique** : il peut changer si la topologie change (maintenance, ajout/retrait de LEDs)
- **Toujours utiliser le mapping CONFIG pour interpréter les messages UPDATE**

---

## 7. Exemples concrets

- **Si tu reçois un message UPDATE pour univers eHuB=1** :
  - Utilise le dernier mapping CONFIG reçu pour univers eHuB=1
  - Pour chaque position du payload, retrouve l'entité, le contrôleur, l'univers ArtNet, et envoie la bonne valeur DMX

- **Si tu ajoutes un contrôleur** :
  - Un nouveau message CONFIG sera envoyé avec de nouvelles plages
  - Le routeur mettra à jour son mapping automatiquement

---

## 8. Pour aller plus loin

- Voir le fichier Excel `/asset-execices/Ecran.xlsx` pour la correspondance complète entités/univers/contrôleurs
- Voir les exemples de messages binaires dans `/asset-execices/sample-messages-ehub.txt`
- Voir la doc technique du projet pour les détails sur le protocole eHuB 