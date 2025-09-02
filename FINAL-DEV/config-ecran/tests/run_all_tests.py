#!/usr/bin/env python3
"""
🧪 SUITE DE TESTS - Configuration Écran
Lancement de tous les tests pour l'étape config-ecran
"""

import sys
import os
import subprocess

def run_test(test_file, description):
    """
    Lance un test et retourne le résultat
    """
    print(f"🧪 {description}")
    print(f"📄 Fichier: {test_file}")
    print("-" * 50)
    
    try:
        # Changer le répertoire de travail pour les imports
        original_dir = os.getcwd()
        os.chdir('/home/joel/projet_ecran/controlleur-ecran-led-unity')
        
        result = subprocess.run([
            'python3', 
            f'FINAL-DEV/config-ecran/tests/{test_file}'
        ], capture_output=True, text=True)
        
        os.chdir(original_dir)
        
        if result.returncode == 0:
            print("✅ TEST RÉUSSI")
            print(result.stdout)
            return True
        else:
            print("❌ TEST ÉCHOUÉ")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ ERREUR lors du test: {e}")
        return False
    
    finally:
        print("=" * 60)
        print()

def main():
    """
    Lance tous les tests de configuration écran
    """
    print("🚀 === SUITE DE TESTS CONFIG-ÉCRAN ===")
    print()
    
    tests = [
        ("test_etape_1_2.py", "Test complet de l'étape 1.2"),
        ("test_ecarts_irreguliers.py", "Test spécifique des écarts irréguliers")
    ]
    
    results = []
    
    for test_file, description in tests:
        success = run_test(test_file, description)
        results.append((test_file, success))
    
    # Résumé final
    print("📊 === RÉSUMÉ DES TESTS ===")
    print()
    
    all_passed = True
    for test_file, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
        print(f"{status} - {test_file}")
        if not success:
            all_passed = False
    
    print()
    
    if all_passed:
        print("🎉 === TOUS LES TESTS RÉUSSIS ! ===")
        print("✅ Configuration écran validée")
        print("✅ Prêt pour l'étape suivante")
        return 0
    else:
        print("❌ === DES TESTS ONT ÉCHOUÉ ===")
        print("⚠️ Corrections nécessaires avant de continuer")
        return 1

if __name__ == "__main__":
    exit(main())
