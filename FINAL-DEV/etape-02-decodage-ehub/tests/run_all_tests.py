#!/usr/bin/env python3
"""
🧪 LANCEUR DE TOUS LES TESTS - Étape 2 Décodage eHub
Suite complète de tests pour l'intégration et le décodage
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
        # Changer le répertoire de travail
        original_dir = os.getcwd()
        os.chdir('/home/joel/projet_ecran/controlleur-ecran-led-unity')
        
        result = subprocess.run([
            'python3', 
            f'FINAL-DEV/etape-02-decodage-ehub/tests/{test_file}'
        ], capture_output=True, text=True)
        
        os.chdir(original_dir)
        
        if result.returncode == 0:
            print("✅ TEST RÉUSSI")
            # Afficher les dernières lignes importantes
            lines = result.stdout.strip().split('\n')
            important_lines = [line for line in lines if any(marker in line for marker in ['✅', '❌', '🎉', '===', 'RÉUSSI', 'ÉCHOUÉ'])]
            for line in important_lines[-8:]:
                print(line)
            return True
        else:
            print("❌ TEST ÉCHOUÉ")
            print("STDERR:", result.stderr[-500:])  # Derniers 500 chars d'erreur
            return False
            
    except Exception as e:
        print(f"❌ ERREUR lors du test: {e}")
        return False
    
    finally:
        print("=" * 60)
        print()

def main():
    """
    Lance tous les tests de l'étape 2
    """
    print("🚀 === SUITE DE TESTS ÉTAPE 2 : DÉCODAGE eHUB ===")
    print()
    
    tests = [
        ("test_etape_2.py", "Test complet intégration et décodage")
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
        print("🎉 === ÉTAPE 2 COMPLÈTEMENT VALIDÉE ! ===")
        print("✅ Intégration Réception + Config + Décodage")
        print("✅ Messages eHub correctement décodés")
        print("✅ Mapping vers contrôleurs opérationnel")
        print("✅ Gestion d'erreurs robuste")
        print("✅ Prêt pour l'étape 3 (Mapping DMX complet)")
        print()
        print("🧪 TESTS OPTIONNELS:")
        print("📄 python3 tests/test_real_data.py - Test avec vraies données Unity")
        return 0
    else:
        print("❌ === DES TESTS ONT ÉCHOUÉ ===")
        print("⚠️ Vérifiez les modules précédents (étape 0 et config-ecran)")
        print("⚠️ Assurez-vous que les dépendances sont installées")
        return 1

if __name__ == "__main__":
    exit(main())
