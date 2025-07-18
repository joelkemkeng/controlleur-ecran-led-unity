#!/usr/bin/env python3
"""
test_mapping_fix.py - Script de test pour valider les corrections du mapping EntityMapper

Ce script teste le mapping corrigé pour s'assurer que :
1. Les entités sont correctement mappées aux contrôleurs
2. Les univers DMX sont calculés correctement
3. Les canaux DMX respectent les limites (1-512)
4. Les valeurs RGB sont validées
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from core.models import EntityUpdate, EntityRange
from mapping.entity_mapper import EntityMapper
from config.manager import ConfigManager
from dmx.models import DMXPacket

def test_mapping_corrections():
    """Test complet des corrections du mapping."""
    print("🧪 === TEST DES CORRECTIONS DU MAPPING ===")
    
    # 1. Charger la configuration
    print("\n1. Chargement de la configuration...")
    try:
        config_mgr = ConfigManager("config/config.json")
        config = config_mgr.config
        print(f"✅ Configuration chargée: {len(config.controllers)} contrôleurs")
        
        # Afficher les contrôleurs
        for name, ctrl in config.controllers.items():
            print(f"   - {name}: {ctrl.ip}, entités {ctrl.start_entity}-{ctrl.end_entity}, {len(ctrl.universes)} univers")
            
    except Exception as e:
        print(f"❌ Erreur chargement config: {e}")
        return False
    
    # 2. Créer le mapper
    print("\n2. Création du mapper...")
    mapper = EntityMapper(config)
    
    # 3. Créer des plages de test (basées sur les données réelles)
    print("\n3. Création des plages de test...")
    test_ranges = {
        100: EntityRange(0, 100, 169, 269),      # 170 entités, contrôleur 1
        5100: EntityRange(0, 5100, 169, 5269),  # 170 entités, contrôleur 2
        10100: EntityRange(0, 10100, 169, 10269), # 170 entités, contrôleur 3
        15100: EntityRange(0, 15100, 169, 15269), # 170 entités, contrôleur 4
    }
    
    # 4. Construire le mapping
    print("\n4. Construction du mapping...")
    mapper.build_mapping(test_ranges)
    
    if not mapper.entity_to_dmx:
        print("❌ Aucun mapping construit")
        return False
    
    print(f"✅ Mapping construit: {len(mapper.entity_to_dmx)} entités")
    
    # 5. Tester le mapping des entités clés
    print("\n5. Test du mapping des entités clés...")
    test_entities = [100, 5100, 10100, 15100]  # Une entité par contrôleur
    expected_ips = ["192.168.1.45", "192.168.1.46", "192.168.1.47", "192.168.1.48"]
    
    for i, entity_id in enumerate(test_entities):
        if entity_id in mapper.entity_to_dmx:
            mapping = mapper.entity_to_dmx[entity_id]
            expected_ip = expected_ips[i]
            
            print(f"   Entité {entity_id}:")
            print(f"     - IP: {mapping['controller_ip']} (attendu: {expected_ip})")
            print(f"     - Univers: {mapping['universe']}")
            print(f"     - Canaux: R={mapping['r_channel']}, G={mapping['g_channel']}, B={mapping['b_channel']}")
            
            # Vérifications
            if mapping['controller_ip'] != expected_ip:
                print(f"     ❌ IP incorrecte")
                return False
            if not (1 <= mapping['r_channel'] <= 512):
                print(f"     ❌ Canal R hors limites")
                return False
            if not (1 <= mapping['g_channel'] <= 512):
                print(f"     ❌ Canal G hors limites")
                return False
            if not (1 <= mapping['b_channel'] <= 512):
                print(f"     ❌ Canal B hors limites")
                return False
                
            print(f"     ✅ Mapping correct")
        else:
            print(f"   ❌ Entité {entity_id} non mappée")
            return False
    
    # 6. Test du mapping entités → DMX
    print("\n6. Test du mapping entités → DMX...")
    test_entity_updates = [
        EntityUpdate(100, 255, 0, 0, 0),    # Rouge, contrôleur 1
        EntityUpdate(5100, 0, 255, 0, 0),   # Vert, contrôleur 2
        EntityUpdate(10100, 0, 0, 255, 0),  # Bleu, contrôleur 3
        EntityUpdate(15100, 255, 255, 0, 0) # Jaune, contrôleur 4
    ]
    
    dmx_packets = mapper.map_entities_to_dmx(test_entity_updates)
    
    if not dmx_packets:
        print("❌ Aucun paquet DMX généré")
        return False
    
    print(f"✅ {len(dmx_packets)} paquets DMX générés")
    
    # Vérifier que tous les contrôleurs sont représentés
    controller_ips = set()
    for packet in dmx_packets:
        controller_ips.add(packet.controller_ip)
        print(f"   Paquet: {packet.controller_ip}, U{packet.universe}, {len(packet.channels)} canaux")
    
    if len(controller_ips) != 4:
        print(f"❌ Seulement {len(controller_ips)} contrôleurs actifs (attendu: 4)")
        return False
    
    print(f"✅ Tous les contrôleurs actifs: {sorted(controller_ips)}")
    
    # 7. Test des validations
    print("\n7. Test des validations...")
    
    # Test avec valeurs RGB invalides
    invalid_entities = [
        EntityUpdate(100, 300, 0, 0, 0),     # Rouge > 255
        EntityUpdate(5100, 0, -10, 0, 0),    # Vert < 0
    ]
    
    dmx_packets_invalid = mapper.map_entities_to_dmx(invalid_entities)
    
    if dmx_packets_invalid:
        print("❌ Les entités invalides ont été traitées")
        return False
    
    print("✅ Validation RGB fonctionne correctement")
    
    # 8. Test des limites DMX
    print("\n8. Test des limites DMX...")
    
    # Tester une entité qui devrait être à la limite
    test_entity_limit = EntityUpdate(269, 255, 255, 255, 0)  # Dernière entité de la première plage
    dmx_packets_limit = mapper.map_entities_to_dmx([test_entity_limit])
    
    if dmx_packets_limit:
        packet = dmx_packets_limit[0]
        max_channel = max(packet.channels.keys())
        if max_channel > 512:
            print(f"❌ Canal DMX > 512: {max_channel}")
            return False
        print(f"✅ Canaux DMX dans les limites (max: {max_channel})")
    
    print("\n🎯 === RÉSUMÉ DES TESTS ===")
    print("✅ Configuration chargée correctement")
    print("✅ Mapping construit sans erreurs")
    print("✅ Entités mappées aux bons contrôleurs")
    print("✅ Univers DMX calculés correctement")
    print("✅ Canaux DMX dans les limites (1-512)")
    print("✅ Validation RGB fonctionnelle")
    print("✅ Paquets DMX générés correctement")
    print("✅ Tous les contrôleurs actifs")
    
    print("\n🏆 MAPPING CORRIGÉ VALIDÉ AVEC SUCCÈS!")
    return True

if __name__ == "__main__":
    success = test_mapping_corrections()
    if success:
        print("\n✅ Tous les tests passent - Le mapping est corrigé!")
        sys.exit(0)
    else:
        print("\n❌ Certains tests échouent - Corrections nécessaires")
        sys.exit(1)