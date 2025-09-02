#!/usr/bin/env python3
"""
🧪 TEST CORRECTION ÉCARTS IRRÉGULIERS - Configuration Écran
Test pour vérifier que les écarts irréguliers sont bien gérés
"""

import sys
import os
sys.path.append('/home/joel/projet_ecran/controlleur-ecran-led-unity')

from config.screen_loader import ScreenConfigLoader

def test_ecarts_irreguliers():
    """
    Test spécifique pour les écarts irréguliers entre univers
    """
    print("🧪 === TEST CORRECTION ÉCARTS IRRÉGULIERS ===")
    print()
    
    # Chargement config
    print("📖 Chargement configuration...")
    loader = ScreenConfigLoader()
    success = loader.load_config()
    
    if not success:
        print("❌ ÉCHEC: Impossible de charger la configuration")
        return False
    
    # Tests spécifiques selon tes données
    test_cases = [
        # (entity_id, expected_universe, expected_channel_range)
        (100, 0, 1),       # Premier de l'univers 0
        (269, 0, 170),     # Dernier de l'univers 0 (170 entités)
        (270, 1, 1),       # Premier de l'univers 1
        (358, 1, 89),      # Dernier de l'univers 1 (89 entités)
        (400, 2, 1),       # Premier de l'univers 2
        (569, 2, 170),     # Dernier de l'univers 2 (170 entités)
        (570, 3, 1),       # Premier de l'univers 3
        (658, 3, 89),      # Dernier de l'univers 3 (89 entités)
    ]
    
    print("🔍 Tests spécifiques des écarts irréguliers:")
    
    all_tests_passed = True
    
    for entity_id, expected_universe, expected_channel in test_cases:
        mapping = loader.get_mapping_for_entity(entity_id)
        
        if not mapping:
            print(f"❌ ÉCHEC: Entité {entity_id} non trouvée")
            all_tests_passed = False
            continue
        
        # Vérification univers
        if mapping.universe != expected_universe:
            print(f"❌ ÉCHEC: Entité {entity_id} univers = {mapping.universe}, attendu {expected_universe}")
            all_tests_passed = False
            continue
        
        # Vérification canal
        if mapping.channel != expected_channel:
            print(f"❌ ÉCHEC: Entité {entity_id} canal = {mapping.channel}, attendu {expected_channel}")
            all_tests_passed = False
            continue
        
        print(f"✅ Entité {entity_id} → {mapping.controller_ip}:u{mapping.universe}:ch{mapping.channel}")
    
    print()
    
    # Vérification des plages d'univers
    print("📊 Vérification des tailles d'univers:")
    
    universe_sizes = {}
    for mapping in loader.mappings:
        key = f"{mapping.controller_ip}:u{mapping.universe}"
        if key not in universe_sizes:
            universe_sizes[key] = 0
        universe_sizes[key] += 1
    
    # Vérifier quelques tailles d'univers connues
    expected_sizes = {
        "192.168.1.45:u0": 170,  # 100-269
        "192.168.1.45:u1": 89,   # 270-358
        "192.168.1.45:u2": 170,  # 400-569
        "192.168.1.45:u3": 89,   # 570-658
    }
    
    for key, expected_size in expected_sizes.items():
        if key in universe_sizes:
            actual_size = universe_sizes[key]
            if actual_size == expected_size:
                print(f"✅ {key}: {actual_size} entités (correct)")
            else:
                print(f"❌ {key}: {actual_size} entités, attendu {expected_size}")
                all_tests_passed = False
        else:
            print(f"❌ {key}: non trouvé")
            all_tests_passed = False
    
    print()
    
    if all_tests_passed:
        print("🎉 === CORRECTION RÉUSSIE ! ===")
        print("✅ Écarts irréguliers correctement gérés")
        print("✅ Canaux DMX correctement calculés")
        print("✅ Prêt pour l'étape 2")
        return True
    else:
        print("❌ === CORRECTIONS NÉCESSAIRES ===")
        return False

if __name__ == "__main__":
    success = test_ecarts_irreguliers()
    if success:
        print("\n🚀 Configuration corrigée ! Passage à l'étape 2 autorisé !")
        exit(0)
    else:
        print("\n❌ Des corrections sont encore nécessaires")
        exit(1)
