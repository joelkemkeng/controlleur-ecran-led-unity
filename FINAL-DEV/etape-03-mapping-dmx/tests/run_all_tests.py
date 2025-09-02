#!/usr/bin/env python3
"""
🧪 Suite de tests complète pour l'Étape 3 - DMX Mapping Pipeline
Lance tous les tests et génère un rapport complet
"""

import sys
import time
import subprocess
from pathlib import Path

def print_header(title):
    """Affiche un en-tête stylisé"""
    print()
    print("=" * 60)
    print(f"🧪 {title}")
    print("=" * 60)
    print()

def run_test_file(test_file, description):
    """Lance un fichier de test et retourne le résultat"""
    print(f"🚀 Lancement: {description}")
    print(f"📁 Fichier: {test_file}")
    print("-" * 40)
    
    try:
        # Lancer le test avec Python
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=120  # Timeout de 2 minutes
        )
        
        # Afficher la sortie
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        # Retourner le code de sortie
        success = result.returncode == 0
        print(f"📊 Résultat: {'✅ RÉUSSI' if success else '❌ ÉCHOUÉ'}")
        return success
        
    except subprocess.TimeoutExpired:
        print("⏰ TIMEOUT - Test trop long")
        return False
    except Exception as e:
        print(f"💥 ERREUR: {e}")
        return False

def check_dependencies():
    """Vérifie les dépendances nécessaires"""
    print_header("VÉRIFICATION DÉPENDANCES")
    
    dependencies = [
        ("psutil", "Monitoring mémoire"),
        ("unittest", "Framework de test (builtin)"),
    ]
    
    missing = []
    for module, description in dependencies:
        try:
            __import__(module)
            print(f"✅ {module}: {description}")
        except ImportError:
            print(f"❌ {module}: {description} - MANQUANT")
            missing.append(module)
    
    if missing:
        print(f"\n⚠️ Dépendances manquantes: {', '.join(missing)}")
        print("📝 Installer avec: pip install " + " ".join(missing))
        return False
    else:
        print("\n✅ Toutes les dépendances sont présentes")
        return True

def main():
    """Lance la suite de tests complète"""
    start_time = time.time()
    
    print_header("SUITE DE TESTS ÉTAPE 3 - DMX MAPPING PIPELINE")
    print("🎯 Objectif: Valider l'étape 3 avant passage à l'étape 4")
    print("📦 Composants testés: DMXMapper, DMXUniverse, EHubDMXPipeline")
    print()
    
    # Vérifier les dépendances
    if not check_dependencies():
        print("❌ Tests annulés - dépendances manquantes")
        return False
    
    # Définir les tests à lancer
    test_directory = Path(__file__).parent
    tests = [
        {
            "file": test_directory / "test_dmx_mapper.py",
            "description": "Tests unitaires des classes DMX",
            "required": True
        },
        {
            "file": test_directory / "test_pipeline_integration.py", 
            "description": "Tests d'intégration du pipeline",
            "required": True
        },
        {
            "file": test_directory / "test_performance.py",
            "description": "Tests de performance et validation",
            "required": False  # Optionnel car peut échouer sur petit matériel
        }
    ]
    
    # Vérifier que tous les fichiers existent
    for test in tests:
        if not test["file"].exists():
            print(f"❌ Fichier manquant: {test['file']}")
            return False
    
    # Lancer les tests
    results = []
    
    for i, test in enumerate(tests, 1):
        print_header(f"TEST {i}/{len(tests)}: {test['description']}")
        
        success = run_test_file(str(test["file"]), test["description"])
        results.append({
            "name": test["description"],
            "success": success,
            "required": test["required"]
        })
        
        # Pause entre les tests
        if i < len(tests):
            print("\n⏸️ Pause de 2 secondes...")
            time.sleep(2)
    
    # Génération du rapport final
    total_time = time.time() - start_time
    
    print_header("RAPPORT FINAL")
    print(f"⏱️ Temps total d'exécution: {total_time:.1f} secondes")
    print()
    
    # Statistiques
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["success"])
    failed_tests = total_tests - passed_tests
    required_failed = sum(1 for r in results if not r["success"] and r["required"])
    
    print("📊 STATISTIQUES:")
    print(f"   Total tests: {total_tests}")
    print(f"   ✅ Réussis: {passed_tests}")
    print(f"   ❌ Échoués: {failed_tests}")
    print(f"   🔴 Critiques échoués: {required_failed}")
    print()
    
    # Détail des résultats
    print("📋 DÉTAIL DES RÉSULTATS:")
    for result in results:
        status = "✅ RÉUSSI" if result["success"] else "❌ ÉCHOUÉ"
        criticality = "🔴 REQUIS" if result["required"] else "🟡 OPTIONNEL"
        print(f"   {status} - {result['name']} ({criticality})")
    
    # Déterminer le succès global
    all_required_passed = required_failed == 0
    
    print()
    print("🎯 VERDICT FINAL:")
    if all_required_passed:
        if passed_tests == total_tests:
            print("🎉 SUCCÈS COMPLET - Tous les tests sont passés!")
            print("🚀 L'étape 3 est complètement validée et prête pour l'étape 4!")
        else:
            print("✅ SUCCÈS PARTIEL - Tous les tests requis sont passés")
            print("🚀 L'étape 3 est validée pour l'étape 4 (tests optionnels échoués)")
        
        print()
        print("📝 PROCHAINES ÉTAPES:")
        print("   1. ✅ Documentation complète")
        print("   2. ✅ Tests fonctionnels validés") 
        print("   3. 🎯 Prêt pour l'Étape 4: Formulation et envoi ArtNet")
        
        return True
    else:
        print("❌ ÉCHEC - Des tests requis ont échoué")
        print("🔧 Correction nécessaire avant passage à l'étape 4")
        
        print()
        print("📝 ACTIONS REQUISES:")
        for result in results:
            if not result["success"] and result["required"]:
                print(f"   🔧 Corriger: {result['name']}")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
