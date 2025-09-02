Basé sur l'analyse des documents, voici le format exact des messages **eHuB** que le logiciel de routage doit recevoir :

## Structure générale des messages eHuB

Le protocole eHuB utilise **UDP** avec **2 types de messages** :

### 1. Message "UPDATE" (Type 2)
**Envoyé à haute fréquence (40 fois par seconde)**

```
┌─────────────────────────────────────────────────────────────┐
│ Header (10 octets)                                          │
├─────────────────────────────────────────────────────────────┤
│ 4 octets : 'eHuB' (signature)                              │
│ 1 octet  : 2 (type "update")                               │
│ 1 octet  : [numéro univers eHuB à adresser]                │
│ 2 octets : [nombre d'entités] (unsigned short)             │
│ 2 octets : [taille payload compressé] (unsigned short)     │
├─────────────────────────────────────────────────────────────┤
│ X octets : [payload compressé avec GZip]                   │
└─────────────────────────────────────────────────────────────┘
```

**Payload décompressé** = série de **sextuors** (6 octets par entité) :
```
┌─────────────────────────────────────────────────────────────┐
│ Entité 1 : 2 octets ID + 1 octet R + 1 octet V + 1 octet B + 1 octet W │
│ Entité 2 : 2 octets ID + 1 octet R + 1 octet V + 1 octet B + 1 octet W │
│ ...                                                         │
└─────────────────────────────────────────────────────────────┘
```

### 2. Message "CONFIG" (Type 1)
**Envoyé à basse fréquence (1 fois par seconde)**

```
┌─────────────────────────────────────────────────────────────┐
│ Header (10 octets)                                          │
├─────────────────────────────────────────────────────────────┤
│ 4 octets : 'eHuB' (signature)                              │
│ 1 octet  : 1 (type "config")                               │
│ 1 octet  : [numéro univers eHuB à adresser]                │
│ 2 octets : [nombre de plages dans le message]              │
│ 2 octets : [taille payload compressé] (unsigned short)     │
├─────────────────────────────────────────────────────────────┤
│ X octets : [payload compressé avec GZip]                   │
└─────────────────────────────────────────────────────────────┘
```

**Payload décompressé** = série de **plages** (8 octets par plage) :
```
┌─────────────────────────────────────────────────────────────┐
│ Plage 1 : 2 octets début_sextuor + 2 octets début_entité + │
│           2 octets fin_sextuor + 2 octets fin_entité       │
│ Plage 2 : ...                                              │
└─────────────────────────────────────────────────────────────┘
```

## Exemple concret (araignée avec 8 pattes)

### Message CONFIG :
```
Plage 1: sextuors 0-169 → entités 1-170 (patte 1)
Plage 2: sextuors 170-339 → entités 200-370 (patte 2)
...
```

### Message UPDATE :
```
Sextuor 0: ID=1, R=255, V=0, B=0, W=0 (entité 1 rouge)
Sextuor 1: ID=2, R=0, V=255, B=0, W=0 (entité 2 verte)
...
Sextuor 170: ID=200, R=255, V=255, B=0, W=0 (entité 200 jaune)
```

## Points techniques importants

- **Limite UDP** : ~65 Ko max → peut nécessiter plusieurs messages pour grandes installations
- **Compression GZip** obligatoire sur le payload
- **Ordre des entités** : croissant par ID dans le payload UPDATE
- **Optimisation** : les IDs non-séquentiels sont compactés (entité 200 après entité 170 = position 171*6, pas 200*6)

Le logiciel de routage doit donc :
1. **Écouter** sur un port UDP configuré
2. **Décompresser** le payload GZip
3. **Parser** les structures binaires selon le type de message
4. **Maintenir** la correspondance entités ↔ contrôleurs/univers/canaux