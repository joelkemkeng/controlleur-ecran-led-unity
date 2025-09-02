#!/usr/bin/env python3
"""
🧪 Test unitaire pour DMXMapper - Étape 3
Vérifie le mapping des entités eHuB vers structure DMX
"""

import sys
import unittest
from pathlib import Path

# Import du module à tester
sys.path.append(str(Path(__file__).parent.parent))
from ehub_complete_pipeline_mapping_dmx import DMXMapper, DMXUniverse, LEDMapping

# Import des classes de l'étape 2 pour les entités
sys.path.append('/home/joel/projet_ecran/controlleur-ecran-led-unity/FINAL-DEV/etape-02-decodage-ehub')
from ehub_complete_pipeline_decoder import EHubEntity

class TestDMXMapper(unittest.TestCase):
    """Tests pour la classe DMXMapper"""
    
    def setUp(self):
        """Configuration avant chaque test"""
        self.mapper = DMXMapper()
        
        # Créer des mappings de test
        self.test_mappings = {
            100: LEDMapping(100, "192.168.1.45", 0, 0),
            101: LEDMapping(101, "192.168.1.45", 0, 3),
            102: LEDMapping(102, "192.168.1.45", 0, 6),
            4044: LEDMapping(4044, "192.168.1.45", 26, 45),
            8189: LEDMapping(8189, "192.168.1.46", 52, 90),
        }
        
        # Configurer le mapper avec nos mappings de test
        self.mapper.mappings = self.test_mappings
        
        # Créer les univers correspondants
        self.mapper.universes = {
            ("192.168.1.45", 0): DMXUniverse(0, "192.168.1.45", bytearray(512)),
            ("192.168.1.45", 26): DMXUniverse(26, "192.168.1.45", bytearray(512)),
            ("192.168.1.46", 52): DMXUniverse(52, "192.168.1.46", bytearray(512)),
        }
        
    def test_mapping_single_entity(self):
        """Test mapping d'une seule entité"""
        # Créer une entité de test
        entity = EHubEntity(100, 255, 128, 64, 0)
        
        # Mapper l'entité
        result = self.mapper.map_entities_to_dmx([entity])
        
        # Vérifications
        self.assertEqual(len(result), 1)
        self.assertIn(("192.168.1.45", 0), result)
        
        # Vérifier les valeurs dans l'univers DMX
        universe = result[("192.168.1.45", 0)]
        self.assertEqual(universe.dmx_data[0], 255)  # R
        self.assertEqual(universe.dmx_data[1], 128)  # G
        self.assertEqual(universe.dmx_data[2], 64)   # B
        
    def test_mapping_multiple_entities(self):
        """Test mapping de plusieurs entités"""
        entities = [
            EHubEntity(100, 255, 0, 0, 0),    # Rouge
            EHubEntity(101, 0, 255, 0, 0),    # Vert
            EHubEntity(102, 0, 0, 255, 0),    # Bleu
        ]
        
        result = self.mapper.map_entities_to_dmx(entities)
        
        # Vérifications
        self.assertEqual(len(result), 1)  # Toutes dans le même univers
        universe = result[("192.168.1.45", 0)]
        
        # Vérifier les couleurs
        self.assertEqual(universe.dmx_data[0], 255)  # Entity 100 R
        self.assertEqual(universe.dmx_data[1], 0)    # Entity 100 G
        self.assertEqual(universe.dmx_data[2], 0)    # Entity 100 B
        
        self.assertEqual(universe.dmx_data[3], 0)    # Entity 101 R
        self.assertEqual(universe.dmx_data[4], 255)  # Entity 101 G
        self.assertEqual(universe.dmx_data[5], 0)    # Entity 101 B
        
        self.assertEqual(universe.dmx_data[6], 0)    # Entity 102 R
        self.assertEqual(universe.dmx_data[7], 0)    # Entity 102 G
        self.assertEqual(universe.dmx_data[8], 255)  # Entity 102 B
        
    def test_mapping_multiple_universes(self):
        """Test mapping vers plusieurs univers"""
        entities = [
            EHubEntity(4044, 161, 59, 223, 0),  # Univers 26
            EHubEntity(8189, 9, 223, 161, 0),   # Univers 52
        ]
        
        result = self.mapper.map_entities_to_dmx(entities)
        
        # Vérifications
        self.assertEqual(len(result), 2)  # Deux univers différents
        
        # Vérifier univers 26
        self.assertIn(("192.168.1.45", 26), result)
        universe26 = result[("192.168.1.45", 26)]
        self.assertEqual(universe26.dmx_data[45], 161)  # R
        self.assertEqual(universe26.dmx_data[46], 59)   # G
        self.assertEqual(universe26.dmx_data[47], 223)  # B
        
        # Vérifier univers 52
        self.assertIn(("192.168.1.46", 52), result)
        universe52 = result[("192.168.1.46", 52)]
        self.assertEqual(universe52.dmx_data[90], 9)    # R
        self.assertEqual(universe52.dmx_data[91], 223)  # G
        self.assertEqual(universe52.dmx_data[92], 161)  # B
        
    def test_mapping_unknown_entity(self):
        """Test mapping d'entité non mappée"""
        # Entité qui n'existe pas dans nos mappings
        entity = EHubEntity(99999, 255, 255, 255, 0)
        
        result = self.mapper.map_entities_to_dmx([entity])
        
        # Aucun univers ne devrait être modifié
        self.assertEqual(len(result), 0)
        
    def test_mapping_empty_list(self):
        """Test mapping d'une liste vide"""
        result = self.mapper.map_entities_to_dmx([])
        self.assertEqual(len(result), 0)

class TestDMXUniverse(unittest.TestCase):
    """Tests pour la classe DMXUniverse"""
    
    def test_universe_creation(self):
        """Test création d'un univers DMX"""
        universe = DMXUniverse(42, "192.168.1.45", bytearray(512))
        
        self.assertEqual(universe.universe_id, 42)
        self.assertEqual(universe.controller_ip, "192.168.1.45")
        self.assertEqual(len(universe.dmx_data), 512)
        
        # Tous les canaux doivent être à 0 par défaut
        for i in range(512):
            self.assertEqual(universe.dmx_data[i], 0)
            
    def test_set_rgb(self):
        """Test configuration RGB dans l'univers"""
        universe = DMXUniverse(0, "192.168.1.45", bytearray(512))
        
        # Configurer RGB au canal 100
        universe.set_rgb(100, 255, 128, 64)
        
        self.assertEqual(universe.dmx_data[100], 255)  # R
        self.assertEqual(universe.dmx_data[101], 128)  # G
        self.assertEqual(universe.dmx_data[102], 64)   # B
        
        # Les autres canaux restent à 0
        self.assertEqual(universe.dmx_data[99], 0)
        self.assertEqual(universe.dmx_data[103], 0)
        
    def test_set_rgb_overflow(self):
        """Test protection contre débordement"""
        universe = DMXUniverse(0, "192.168.1.45", bytearray(512))
        
        # Essayer de configurer RGB trop près de la fin
        universe.set_rgb(511, 255, 128, 64)  # Devrait être ignoré
        
        # Aucune modification ne devrait avoir lieu
        self.assertEqual(universe.dmx_data[511], 0)
        
    def test_clear_universe(self):
        """Test remise à zéro de l'univers"""
        universe = DMXUniverse(0, "192.168.1.45", bytearray(512))
        
        # Configurer quelques valeurs
        universe.set_rgb(0, 255, 255, 255)
        universe.set_rgb(10, 128, 128, 128)
        
        # Vérifier qu'elles sont configurées
        self.assertEqual(universe.dmx_data[0], 255)
        self.assertEqual(universe.dmx_data[10], 128)
        
        # Remettre à zéro
        universe.clear()
        
        # Vérifier que tout est à zéro
        for i in range(512):
            self.assertEqual(universe.dmx_data[i], 0)

class TestLEDMapping(unittest.TestCase):
    """Tests pour la classe LEDMapping"""
    
    def test_mapping_creation(self):
        """Test création d'un mapping LED"""
        mapping = LEDMapping(4044, "192.168.1.45", 26, 45)
        
        self.assertEqual(mapping.entity_id, 4044)
        self.assertEqual(mapping.controller_ip, "192.168.1.45")
        self.assertEqual(mapping.universe, 26)
        self.assertEqual(mapping.channel_start, 45)
        
    def test_mapping_string_representation(self):
        """Test représentation string du mapping"""
        mapping = LEDMapping(4044, "192.168.1.45", 26, 45)
        
        # La représentation doit contenir les infos essentielles
        str_repr = str(mapping)
        self.assertIn("4044", str_repr)
        self.assertIn("192.168.1.45", str_repr)
        self.assertIn("26", str_repr)
        self.assertIn("45", str_repr)

def run_tests():
    """Lance tous les tests avec un rapport détaillé"""
    print("🧪 === TESTS ÉTAPE 3 - DMX MAPPER ===")
    print()
    
    # Créer la suite de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Ajouter tous les tests
    suite.addTests(loader.loadTestsFromTestCase(TestDMXMapper))
    suite.addTests(loader.loadTestsFromTestCase(TestDMXUniverse))
    suite.addTests(loader.loadTestsFromTestCase(TestLEDMapping))
    
    # Exécuter les tests avec rapport détaillé
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Résumé final
    print()
    print("📊 === RÉSUMÉ TESTS ===")
    print(f"✅ Tests réussis: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Tests échoués: {len(result.failures)}")
    print(f"💥 Erreurs: {len(result.errors)}")
    print(f"🎯 Total: {result.testsRun}")
    
    if result.wasSuccessful():
        print("🎉 Tous les tests sont passés avec succès!")
        return True
    else:
        print("⚠️ Certains tests ont échoué!")
        return False

if __name__ == "__main__":
    run_tests()
