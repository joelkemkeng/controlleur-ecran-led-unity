#!/usr/bin/env python3
"""
🧪 LANCEUR DE TOUS LES TESTS - Réception eHub
Suite complète de tests pour l'étape 0
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
            f'FINAL-DEV/etape-00-reception-ehub/tests/{test_file}'
        ], capture_output=True, text=True)
        
        os.chdir(original_dir)
        
        if result.returncode == 0:
            print("✅ TEST RÉUSSI")
            # Afficher seulement les dernières lignes importantes
            lines = result.stdout.strip().split('\n')
            important_lines = [line for line in lines if any(marker in line for marker in ['✅', '❌', '🎉', '===', 'IP WSL:', 'Port:', 'Configuration'])]
            for line in important_lines[-10:]:  # 10 dernières lignes importantes
                print(line)
            return True
        else:
            print("❌ TEST ÉCHOUÉ")
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
    Lance tous les tests de réception eHub
    """
    print("🚀 === SUITE DE TESTS RÉCEPTION eHUB ===")
    print()
    
    tests = [
        ("test_network.py", "Test connectivité réseau Unity ↔ WSL"),
        ("test_etape_0.py", "Test complet réception eHub")
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
        print("🎉 === ÉTAPE 0 COMPLÈTEMENT VALIDÉE ! ===")
        print("✅ Réception eHub opérationnelle")
        print("✅ Connectivité réseau validée")
        print("✅ Gestion d'erreurs robuste")
        print("✅ Prêt pour l'étape 1 (Configuration écran)")
        return 0
    else:
        print("❌ === DES TESTS ONT ÉCHOUÉ ===")
        print("⚠️ Vérifiez la configuration réseau")
        print("⚠️ Assurez-vous qu'aucun autre processus n'utilise le port 8765")
        return 1

if __name__ == "__main__":
    exit(main())
