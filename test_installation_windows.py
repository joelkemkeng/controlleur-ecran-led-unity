#!/usr/bin/env python3
"""
🧪 TEST D'INSTALLATION - Windows
Script de validation complète de l'environnement
"""

import sys
import os
from pathlib import Path

def test_python_version():
    """Test version Python"""
    print("🐍 Test version Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Incompatible (requis 3.7+)")
        return False

def test_required_packages():
    """Test des packages requis"""
    print("\n📦 Test des packages requis...")
    
    packages = {
        'pandas': 'Lecture fichiers Excel',
        'openpyxl': 'Support Excel avancé', 
        'pytest': 'Tests unitaires'
    }
    
    success = True
    for package, description in packages.items():
        try:
            exec(f"import {package}")
            print(f"✅ {package} - {description}")
        except ImportError:
            print(f"❌ {package} - {description} - MANQUANT")
            success = False
    
    return success

def test_standard_modules():
    """Test des modules standard"""
    print("\n🔧 Test des modules standard...")
    
    modules = {
        'socket': 'Communications réseau',
        'gzip': 'Décompression eHub',
        'struct': 'Données binaires',
        'dataclasses': 'Classes de données',
        'typing': 'Annotations types',
        'pathlib': 'Gestion chemins'
    }
    
    success = True
    for module, description in modules.items():
        try:
            exec(f"import {module}")
            print(f"✅ {module} - {description}")
        except ImportError:
            print(f"❌ {module} - {description} - MANQUANT")
            success = False
    
    return success

def test_project_structure():
    """Test structure du projet"""
    print("\n📁 Test structure du projet...")
    
    base_path = Path(__file__).parent
    required_dirs = [
        'FINAL-DEV/config-ecran',
        'FINAL-DEV/etape-00-reception-ehub', 
        'FINAL-DEV/etape-02-decodage-ehub',
        'FINAL-DEV/etape-03-mapping-dmx',
        'FINAL-DEV/etape-04-send-artnet',
        'assets/data_config'
    ]
    
    success = True
    for dir_path in required_dirs:
        full_path = base_path / dir_path
        if full_path.exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} - MANQUANT")
            success = False
    
    return success

def test_excel_file():
    """Test fichier Excel de configuration"""
    print("\n📊 Test fichier de configuration...")
    
    base_path = Path(__file__).parent
    excel_path = base_path / 'assets/data_config/Ecran.xlsx'
    
    if excel_path.exists():
        print(f"✅ Ecran.xlsx trouvé")
        try:
            import pandas as pd
            df = pd.read_excel(excel_path)
            print(f"✅ Ecran.xlsx lisible - {len(df)} lignes")
            return True
        except Exception as e:
            print(f"❌ Erreur lecture Ecran.xlsx: {e}")
            return False
    else:
        print(f"❌ Ecran.xlsx manquant dans {excel_path}")
        return False

def test_basic_import():
    """Test import des modules principaux"""
    print("\n🔗 Test import des modules du projet...")
    
    # Tester ScreenConfigLoader
    try:
        sys.path.insert(0, str(Path(__file__).parent / 'FINAL-DEV/config-ecran'))
        from screen_loader import ScreenConfigLoader
        print("✅ screen_loader importé")
        
        # Test rapide
        loader = ScreenConfigLoader()
        print("✅ ScreenConfigLoader instancié")
        return True
        
    except Exception as e:
        print(f"❌ Erreur import screen_loader: {e}")
        return False

def main():
    """Test principal"""
    print("🚀 === TEST D'INSTALLATION WINDOWS ===")
    print("🎯 Validation environnement projet LED Unity")
    print()
    
    tests = [
        ("Version Python", test_python_version),
        ("Packages requis", test_required_packages), 
        ("Modules standard", test_standard_modules),
        ("Structure projet", test_project_structure),
        ("Fichier Excel", test_excel_file),
        ("Import modules", test_basic_import)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"💥 Erreur {test_name}: {e}")
            results.append((test_name, False))
        print()
    
    # Résumé
    print("📊 === RÉSUMÉ DES TESTS ===")
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
        print(f"{status} - {test_name}")
        if success:
            passed += 1
    
    print()
    print(f"🎯 RÉSULTAT FINAL: {passed}/{total} tests réussis ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 INSTALLATION COMPLÈTE ET FONCTIONNELLE !")
        print("✅ Vous pouvez maintenant lancer le projet")
        print()
        print("🚀 COMMANDES SUIVANTES:")
        print("   • Activer l'environnement: .\\venv_windows\\Scripts\\Activate.ps1")
        print("   • Tester config écran: cd FINAL-DEV\\config-ecran && python screen_loader.py")
        print("   • Lancer pipeline: cd FINAL-DEV\\etape-04-send-artnet && python ehub_complete_pipeline_send_artnet.py")
        return 0
    else:
        print("⚠️ INSTALLATION INCOMPLÈTE")
        print("🔧 Veuillez corriger les erreurs avant de continuer")
        return 1

if __name__ == "__main__":
    exit(main())
