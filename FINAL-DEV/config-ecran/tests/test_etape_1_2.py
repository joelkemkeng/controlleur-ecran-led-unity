#!/usr/bin/env python3
"""
🧪 TEST ÉTAPE 1.2 - Configuration Écran
Test simple et clair pour valider le chargement de configuration
"""

import sys
import os
sys.path.append('/home/joel/projet_ecran/controlleur-ecran-led-unity')

from config.screen_loader import ScreenConfigLoader

def test_etape_1_2():
    """
    Test de l'étape 1.2 : Chargement configuration écran
    """
    print("🧪 === TEST ÉTAPE 1.2 : CONFIGURATION ÉCRAN ===")
    print()
    
    # Test 1: Initialisation
    print("🔧 Test 1: Initialisation du chargeur...")
    loader = ScreenConfigLoader()
    print("✅ Chargeur initialisé")
    print()
    
    # Test 2: Chargement config
    print("📖 Test 2: Chargement configuration Excel...")
    success = loader.load_config()
    if not success:
        print("❌ ÉCHEC: Impossible de charger la configuration")
        return False
    print("✅ Configuration chargée")
    print()
    
    # Test 3: Vérification des contrôleurs
    print("🎮 Test 3: Vérification des contrôleurs...")
    expected_controllers = ["192.168.1.45", "192.168.1.46", "192.168.1.47", "192.168.1.48"]
    
    for ip in expected_controllers:
        if ip not in loader.controllers:
            print(f"❌ ÉCHEC: Contrôleur {ip} non trouvé")
            return False
        count = loader.controllers[ip]
        print(f"✅ Contrôleur {ip}: {count} entités")
    print()
    
    # Test 4: Vérification mappings spécifiques
    print("🗺️  Test 4: Vérification mappings spécifiques...")
    
    # Test entité 100 (première entité)
    mapping_100 = loader.get_mapping_for_entity(100)
    if not mapping_100:
        print("❌ ÉCHEC: Entité 100 non trouvée")
        return False
    
    expected = {
        'controller_ip': '192.168.1.45',
        'universe': 0,
        'channel': 1
    }
    
    for key, value in expected.items():
        if getattr(mapping_100, key) != value:
            print(f"❌ ÉCHEC: Entité 100 {key} = {getattr(mapping_100, key)}, attendu {value}")
            return False
    
    print(f"✅ Entité 100 → {mapping_100.controller_ip}:u{mapping_100.universe}:ch{mapping_100.channel}")
    
    # Test entité milieu de plage
    mapping_200 = loader.get_mapping_for_entity(200)
    if mapping_200:
        print(f"✅ Entité 200 → {mapping_200.controller_ip}:u{mapping_200.universe}:ch{mapping_200.channel}")
    
    print()
    
    # Test 5: Statistiques globales
    print("📊 Test 5: Statistiques globales...")
    total_mappings = len(loader.mappings)
    total_controllers = len(loader.controllers)
    
    if total_mappings < 10000:
        print(f"⚠️  ATTENTION: Seulement {total_mappings} mappings (attendu > 10000)")
    else:
        print(f"✅ {total_mappings} mappings créés")
    
    if total_controllers != 4:
        print(f"❌ ÉCHEC: {total_controllers} contrôleurs trouvés (attendu 4)")
        return False
    else:
        print(f"✅ {total_controllers} contrôleurs détectés")
    
    print()
    
    # Résumé
    loader.print_summary()
    
    print("🎉 === ÉTAPE 1.2 RÉUSSIE ! ===")
    print("✅ Configuration écran chargée et validée")
    print("✅ 4 contrôleurs BC216 détectés")
    print("✅ Mappings entités → DMX opérationnels")
    print("✅ Prêt pour l'étape 2 (Décodage eHub)")
    
    return True

if __name__ == "__main__":
    success = test_etape_1_2()
    if success:
        print("\n🚀 Vous pouvez passer à l'étape 2 !")
        exit(0)
    else:
        print("\n❌ Des corrections sont nécessaires")
        exit(1)
