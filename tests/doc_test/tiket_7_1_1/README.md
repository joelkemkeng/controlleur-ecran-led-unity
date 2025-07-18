# Ticket 7.1.1 – Config avancée (multi-contrôleurs, validation, export Excel)

## Objectif
Permettre de gérer des configurations complexes pour le routeur LED (plusieurs contrôleurs, plages d’entités, univers, validation, export Excel) de façon robuste, portable et pédagogique.

## Importance pour le projet
- Permet de décrire fidèlement toute l’installation réelle (mur LED, plusieurs contrôleurs, mapping précis)
- Garantit la cohérence de la config (pas de chevauchement d’entités)
- Facilite la documentation et la préparation du mapping via un export Excel
- Indispensable pour la maintenance et l’évolution du système

## Explication détaillée
La classe `AdvancedConfigManager` permet de :
- Générer une config avancée (ex : mur LED 128x128, 4 contrôleurs, plages d’entités, univers)
- Valider la cohérence de la config (pas de chevauchement d’entités entre contrôleurs)
- Exporter un template Excel du mapping (entités → contrôleurs/univers/canaux)
- Utiliser la config dans tout le pipeline (chargement, validation, documentation)

**Format de la config** : voir `config/manager.py` et `config/advanced_config.py` (attributs, structure, exemples)

## Comment tester concrètement
1. Lancer les tests unitaires :
   ```bash
   pytest tests/test_advanced_config.py
   ```
2. Les tests vérifient :
   - Génération d’une config avancée
   - Validation de la cohérence (pas de chevauchement)
   - Export d’un template Excel (fichier temporaire)
3. Pour tester en vrai :
   - Générer un template Excel avec `export_excel_template`
   - Vérifier la cohérence de la config avec `validate_config`

## Exemples concrets de cas réels
- **Cas 1 :** Préparer une installation mur LED 128x128 avec 4 contrôleurs, plages d’entités, univers, IP, etc.
- **Cas 2 :** Vérifier qu’aucun contrôleur ne gère deux fois la même entité (pas de chevauchement)
- **Cas 3 :** Générer un fichier Excel pour documenter le mapping ou préparer la config pour l’équipe terrain

## Portabilité et conseils pratiques
- Fonctionne sur Linux, Mac, Windows, Raspbian sans modification
- Nécessite pandas et openpyxl pour l’export Excel (`pip install pandas openpyxl`)
- Le template Excel généré peut être édité à la main ou partagé avec l’équipe
- La validation de la config doit être faite avant tout déploiement réel

---

**Prochaine étape :** Intégrer la config avancée dans le pipeline principal, et documenter chaque modification pour la traçabilité. 