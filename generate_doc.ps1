# Script PowerShell pour générer la documentation web de tous les modules Python du projet
# Utilisation : .\generate_doc.ps1

$modules = Get-ChildItem -Directory | Where-Object { Test-Path "$($_.FullName)\__init__.py" } | ForEach-Object { $_.Name }
$modules += 'main'  # Ajoute explicitement main.py (fichier racine)
python -m pdoc $modules 