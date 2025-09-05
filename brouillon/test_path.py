#!/usr/bin/env python3
"""Test de calcul du chemin vers l'étape-04"""

from pathlib import Path
import sys

# Simuler le chemin du fichier pipeline_monitor.py
pipeline_monitor_path = Path(__file__).parent / "app" / "core" / "pipeline_monitor.py"
print(f"Chemin simulé pipeline_monitor: {pipeline_monitor_path}")

# Calculer comme dans le code original
project_root = pipeline_monitor_path.parent.parent.parent.parent
print(f"Project root calculé: {project_root}")

etape4_path = project_root / "etape-04-send-artnet"
print(f"Chemin étape-04 calculé: {etape4_path}")
print(f"Existe: {etape4_path.exists()}")

# Le bon chemin
correct_path = Path.cwd() / "FINAL-DEV" / "etape-04-send-artnet"
print(f"Vrai chemin: {correct_path}")
print(f"Existe: {correct_path.exists()}")

# Test import
if correct_path.exists():
    sys.path.insert(0, str(correct_path))
    try:
        from ehub_pipeline_optimized_working_ok_1 import EHubOptimizedPipeline
        print("✅ Import réussi avec le vrai chemin")
    except ImportError as e:
        print(f"❌ Import échoué: {e}")
