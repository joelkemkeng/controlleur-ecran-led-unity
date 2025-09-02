# Répartition des entités, univers et contrôleurs (données asset)

## Vue d'ensemble
Ce document synthétise la logique de répartition des entités (LEDs), univers DMX et adresses IP des contrôleurs pour l'installation LED du projet, d'après le fichier Excel fourni (`Ecran.xlsx`).

---

## Organisation logique
- **Chaque LED (entité) a un ID unique.**
- Les entités sont réparties en "lignes verticales" (colonnes) sur l'écran LED.
- Chaque quart d'écran est géré par un contrôleur distinct, avec une plage d'entités, d'univers et une IP dédiée.

### Répartition par contrôleur
| Contrôleur IP      | Entités (IDs)         | Univers DMX      |
|--------------------|-----------------------|------------------|
| 192.168.1.45       | 100 – 4858            | 0 – 31           |
| 192.168.1.46       | 5100 – 9858           | 32 – 63          |
| 192.168.1.47       | 10100 – 14858         | 64 – 95          |
| 192.168.1.48       | 15100 – 19858         | 96 – 127         |

- **Chaque univers DMX** gère environ 170 LEDs RGB (512 canaux / 3).
- **Chaque port** du contrôleur gère 2 univers, donc ≈ 341 LEDs RGB.

### Logique de mapping
- La première colonne commence à l'entité 100, la troisième à 400, la cinquième à 700, etc.
- Cela continue jusqu'à la colonne 31 (entité 4600 à 4858).
- Le schéma se répète pour chaque quart d'écran, avec des offsets d'ID (5100, 10100, 15100).

### Cas particulier : projecteur de test
- Un projecteur est connecté au contrôleur 192.168.1.45, univers 200, canaux 1-3.
- Peut être utilisé pour tester l'envoi DMX sur l'installation.

---

## Conseils d'utilisation
- Pour piloter une LED, il faut connaître son ID, l'univers DMX et l'IP du contrôleur associé.
- Le mapping complet est disponible dans le fichier Excel `Ecran.xlsx`.
- Pour se connecter à l'installation :
  - SSID : GLASS_RESEAUX
  - Mot de passe : networks

---

## À retenir
- Cette organisation permet de scaler facilement sur de grandes installations.
- Le mapping doit être respecté pour garantir le bon fonctionnement du routage LED.
- Utiliser le projecteur de test pour valider les premiers envois DMX. 