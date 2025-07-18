# Fonctionnement d'un canal DMX

## 1. Qu'est-ce qu'un canal DMX ?
- Un **canal DMX** est une "case" dans un univers DMX512 qui transporte une valeur (0-255).
- Il contrôle **un paramètre précis** d'un appareil d'éclairage (ex : l'intensité du rouge d'une LED).
- Un univers DMX = 512 canaux (numérotés de 1 à 512).

## 2. Une LED ≠ un canal !
- **Une LED RGB** = 3 canaux DMX (R, G, B)
- **Une LED RGBW** = 4 canaux DMX (R, G, B, W)
- **Chaque couleur d'une LED** occupe un canal distinct.

## 3. Exemple de mapping (LEDs RGB)
| LED  | Canal R | Canal G | Canal B |
|------|---------|---------|---------|
| 1    | 1       | 2       | 3       |
| 2    | 4       | 5       | 6       |
| 3    | 7       | 8       | 9       |
| ...  | ...     | ...     | ...     |

- Pour allumer la LED 2 en rouge :
  - Canal 4 = 255 (R)
  - Canal 5 = 0   (G)
  - Canal 6 = 0   (B)

## 4. Structure d'un univers DMX
- 1 univers = 512 canaux
- Nombre max de LEDs RGB par univers = 170 (car 170 × 3 = 510)
- Les 2 derniers canaux sont souvent inutilisés

## 5. Dans le code (exemple de dictionnaire channels)
```python
channels = {
    1: 255,  # Rouge LED 1
    2: 0,    # Vert LED 1
    3: 0,    # Bleu LED 1
    4: 255,  # Rouge LED 2
    5: 0,    # Vert LED 2
    6: 0,    # Bleu LED 2
    # ...
}
```
- **La clé** = numéro de canal DMX (dans l'univers)
- **La valeur** = valeur à envoyer (0-255)

## 6. Schéma textuel
```
Univers DMX 0 (512 canaux)
┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│  1  │  2  │  3  │  4  │  5  │  6  │ ... │ 510 │ 511 │
├─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
│R LED1│G LED1│B LED1│R LED2│G LED2│B LED2│ ... │ ... │ ... │
└─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
```

## 7. À retenir
- **Un canal = 1 couleur d'1 LED**
- **Une LED = plusieurs canaux consécutifs**
- **Le mapping channels = {canal: valeur}** permet de piloter chaque couleur de chaque LED individuellement

---

*Cette logique est universelle et fonctionne sur toutes les plateformes (Linux, Raspbian, Mac, Windows) sans adaptation.* 