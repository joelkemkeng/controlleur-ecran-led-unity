# Génération de la documentation du code Python

## Objectif
Permettre à tout développeur de générer facilement une documentation web à jour et navigable pour tout le code Python du projet, grâce à l'outil pdoc.

---

## Prérequis
- Avoir installé les dépendances du projet (voir `requirements.txt`)
- Avoir activé l'environnement virtuel Python (`venv`)
- Avoir documenté le code avec des docstrings (format Google, Numpy ou Markdown)

---

## Génération automatique de la documentation

1. **Ouvre un terminal PowerShell** à la racine du projet.
2. **Active l'environnement virtuel** (si ce n'est pas déjà fait) :
   ```powershell
   venv\Scripts\Activate
   ```
3. **Lance le script de génération** :
   ```powershell
   .\generate_doc.ps1
   ```
   - Ce script détecte automatiquement tous les modules/packages Python du projet (dossiers avec `__init__.py`).
   - Il lance pdoc pour générer et servir la documentation web.
4. **Ouvre ton navigateur** à l'adresse indiquée (par défaut http://localhost:8080) pour naviguer dans la documentation.

---

## Ajouter un nouveau module à la documentation
- Il suffit de créer un nouveau dossier avec un fichier `__init__.py` (même vide).
- Le script l'inclura automatiquement lors de la prochaine génération.

---

## Exporter la documentation en HTML statique (optionnel)
Si tu veux exporter la doc pour la mettre sur un serveur ou la partager :
```powershell
$modules = Get-ChildItem -Directory | Where-Object { Test-Path "$($_.FullName)\__init__.py" } | ForEach-Object { $_.Name }
python -m pdoc $modules -o docs
```
- Les fichiers HTML seront dans le dossier `docs/`.

---

## Bonnes pratiques
- Toujours commenter le code avec des docstrings claires et structurées.
- Regénérer la documentation à chaque évolution du code.
- Utiliser la doc web pour onboarder, relire ou partager le projet.

---

**Contact :** Pour toute question, voir le README principal ou demander à l'équipe technique. 