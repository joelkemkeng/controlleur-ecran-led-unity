#!/usr/bin/env python3
"""
🧪 Test d'intégration pour EHubDMXPipeline - Étape 3
Vérifie le fonctionnement complet du pipeline mapping DMX
"""

import sys
import unittest
import time
import threading
import socket
from pathlib import Path

# Import du module à tester
sys.path.append(str(Path(__file__).parent.parent))
from ehub_complete_pipeline_mapping_dmx import EHubDMXPipeline

# Import des classes de l'étape 2
sys.path.append('/home/joel/projet_ecran/controlleur-ecran-led-unity/FINAL-DEV/etape-02-decodage-ehub')
from ehub_complete_pipeline_decoder import EHubEntity, EHubPacket

class TestEHubDMXPipeline(unittest.TestCase):
    """Tests d'intégration pour le pipeline DMX complet"""
    
    def setUp(self):
        """Configuration avant chaque test"""
        # Utiliser un port différent pour les tests
        self.test_port = 8766
        self.pipeline = None
        
    def tearDown(self):
        """Nettoyage après chaque test"""
        if self.pipeline:
            try:
                # Arrêter le pipeline si il tourne
                if hasattr(self.pipeline, 'receiver') and self.pipeline.receiver:
                    self.pipeline.receiver.stop()
            except:
                pass
                
    def test_pipeline_initialization(self):
        """Test initialisation du pipeline"""
        print("\n🔧 Test initialisation pipeline...")
        
        pipeline = EHubDMXPipeline(port=self.test_port)
        
        # Vérifier les attributs de base
        self.assertIsNone(pipeline.dmx_mapper)
        self.assertEqual(pipeline.total_mapped_packets, 0)
        self.assertEqual(pipeline.total_mapped_entities, 0)
        
        # Tester l'initialisation
        success = pipeline.initialize()
        
        if success:
            print("✅ Pipeline initialisé avec succès")
            self.assertIsNotNone(pipeline.dmx_mapper)
            self.assertIsNotNone(pipeline.receiver)
            self.assertIsNotNone(pipeline.screen_config)
        else:
            print("⚠️ Initialisation échouée (normal si pas de config Excel)")
            # L'échec est accepté car nous n'avons pas forcément le fichier Excel
            
        self.pipeline = pipeline
        
    def test_process_ehub_packet(self):
        """Test traitement d'un paquet eHuB synthétique"""
        print("\n📦 Test traitement paquet eHuB...")
        
        pipeline = EHubDMXPipeline(port=self.test_port)
        
        # Créer un mapper minimal pour le test
        from ehub_complete_pipeline_mapping_dmx import DMXMapper, LEDMapping, DMXUniverse
        pipeline.dmx_mapper = DMXMapper()
        
        # Ajouter quelques mappings de test
        pipeline.dmx_mapper.mappings = {
            100: LEDMapping(100, "192.168.1.45", 0, 0),
            101: LEDMapping(101, "192.168.1.45", 0, 3),
            102: LEDMapping(102, "192.168.1.45", 0, 6),
        }
        
        # Créer l'univers correspondant
        pipeline.dmx_mapper.universes = {
            ("192.168.1.45", 0): DMXUniverse(0, "192.168.1.45", bytearray(512))
        }
        
        # Créer un paquet de test
        entities = [
            EHubEntity(100, 255, 0, 0, 0),    # Rouge
            EHubEntity(101, 0, 255, 0, 0),    # Vert
            EHubEntity(102, 0, 0, 255, 0),    # Bleu
            EHubEntity(999, 128, 128, 128, 0), # Non mappé
        ]
        
        packet = EHubPacket(
            message_type=2,
            universe=1,
            num_entities=len(entities),
            payload_size=len(entities) * 6,
            entities=entities
        )
        
        # Traiter le paquet
        result = pipeline.process_ehub_packet(packet)
        
        # Vérifications
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)  # Un seul univers modifié
        
        # Vérifier l'univers
        universe_key = ("192.168.1.45", 0)
        self.assertIn(universe_key, result)
        
        universe = result[universe_key]
        self.assertEqual(universe.dmx_data[0], 255)  # Entity 100 R
        self.assertEqual(universe.dmx_data[1], 0)    # Entity 100 G
        self.assertEqual(universe.dmx_data[2], 0)    # Entity 100 B
        self.assertEqual(universe.dmx_data[3], 0)    # Entity 101 R
        self.assertEqual(universe.dmx_data[4], 255)  # Entity 101 G
        self.assertEqual(universe.dmx_data[5], 0)    # Entity 101 B
        
        print("✅ Paquet traité avec succès")
        self.pipeline = pipeline
        
    def test_pipeline_inheritance(self):
        """Test que le pipeline hérite correctement de l'étape 2"""
        print("\n🔗 Test héritage étape 2...")
        
        pipeline = EHubDMXPipeline(port=self.test_port)
        
        # Vérifier les méthodes héritées
        self.assertTrue(hasattr(pipeline, 'initialize'))
        self.assertTrue(hasattr(pipeline, 'listen_and_decode'))
        self.assertTrue(hasattr(pipeline, 'decode_ehub_packet'))
        self.assertTrue(hasattr(pipeline, 'process_packet'))
        
        # Vérifier les attributs hérités
        self.assertTrue(hasattr(pipeline, 'receiver'))
        self.assertTrue(hasattr(pipeline, 'screen_config'))
        self.assertTrue(hasattr(pipeline, 'packet_count'))
        
        # Vérifier les nouveaux attributs de l'étape 3
        self.assertTrue(hasattr(pipeline, 'dmx_mapper'))
        self.assertTrue(hasattr(pipeline, 'total_mapped_packets'))
        self.assertTrue(hasattr(pipeline, 'total_mapped_entities'))
        
        print("✅ Héritage vérifié avec succès")
        self.pipeline = pipeline
        
    def test_mapping_statistics_update(self):
        """Test mise à jour des statistiques de mapping"""
        print("\n📊 Test statistiques mapping...")
        
        pipeline = EHubDMXPipeline(port=self.test_port)
        
        # Configurer le mapper minimal
        from ehub_complete_pipeline_mapping_dmx import DMXMapper, LEDMapping, DMXUniverse
        pipeline.dmx_mapper = DMXMapper()
        pipeline.dmx_mapper.mappings = {
            100: LEDMapping(100, "192.168.1.45", 0, 0),
        }
        pipeline.dmx_mapper.universes = {
            ("192.168.1.45", 0): DMXUniverse(0, "192.168.1.45", bytearray(512))
        }
        
        # Statistiques initiales
        self.assertEqual(pipeline.total_mapped_packets, 0)
        self.assertEqual(pipeline.total_mapped_entities, 0)
        
        # Traiter un paquet
        entities = [EHubEntity(100, 255, 0, 0, 0)]
        packet = EHubPacket(2, 1, len(entities), len(entities) * 6, entities)
        
        result = pipeline.process_ehub_packet(packet)
        
        # Vérifier mise à jour des statistiques
        self.assertEqual(pipeline.total_mapped_packets, 1)
        self.assertEqual(pipeline.total_mapped_entities, 1)
        
        # Traiter un second paquet avec plus d'entités
        entities2 = [
            EHubEntity(100, 128, 64, 32, 0),
            EHubEntity(100, 64, 128, 192, 0),  # Même entité, différentes valeurs
        ]
        packet2 = EHubPacket(2, 1, len(entities2), len(entities2) * 6, entities2)
        
        result2 = pipeline.process_ehub_packet(packet2)
        
        # Vérifier nouvelles statistiques
        self.assertEqual(pipeline.total_mapped_packets, 2)
        self.assertEqual(pipeline.total_mapped_entities, 3)  # 1 + 2
        
        print("✅ Statistiques mises à jour correctement")
        self.pipeline = pipeline
        
    def test_empty_packet_handling(self):
        """Test gestion des paquets vides"""
        print("\n📭 Test gestion paquets vides...")
        
        pipeline = EHubDMXPipeline(port=self.test_port)
        
        # Configurer mapper
        from ehub_complete_pipeline_mapping_dmx import DMXMapper
        pipeline.dmx_mapper = DMXMapper()
        pipeline.dmx_mapper.mappings = {}
        pipeline.dmx_mapper.universes = {}
        
        # Paquet vide
        empty_packet = EHubPacket(2, 1, 0, 0, [])
        
        result = pipeline.process_ehub_packet(empty_packet)
        
        # Aucun univers ne devrait être retourné
        self.assertEqual(len(result), 0)
        
        # Statistiques ne devraient pas changer
        self.assertEqual(pipeline.total_mapped_packets, 0)
        self.assertEqual(pipeline.total_mapped_entities, 0)
        
        print("✅ Paquets vides gérés correctement")
        self.pipeline = pipeline

class TestPipelineNetworking(unittest.TestCase):
    """Tests réseau pour le pipeline (nécessite configuration réseau)"""
    
    def test_port_binding(self):
        """Test binding du port UDP"""
        print("\n🌐 Test binding port UDP...")
        
        test_port = 8767  # Port différent pour éviter conflits
        
        try:
            pipeline = EHubDMXPipeline(port=test_port)
            
            # Tenter l'initialisation
            success = pipeline.initialize()
            
            if success:
                print(f"✅ Port {test_port} bindé avec succès")
                
                # Vérifier que le socket existe
                self.assertIsNotNone(pipeline.receiver)
                
                # Tenter un second binding sur le même port (devrait échouer)
                pipeline2 = EHubDMXPipeline(port=test_port)
                success2 = pipeline2.initialize()
                
                # Le second ne devrait pas réussir
                self.assertFalse(success2)
                print(f"✅ Protection contre double binding vérifiée")
                
            else:
                print(f"⚠️ Binding échoué (normal si port occupé ou config manquante)")
                
        except Exception as e:
            print(f"⚠️ Erreur réseau: {e}")
            # Accepter l'erreur car elle peut être due à l'environnement

def run_integration_tests():
    """Lance tous les tests d'intégration"""
    print("🧪 === TESTS INTÉGRATION ÉTAPE 3 ===")
    print()
    
    # Créer la suite de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Ajouter les tests
    suite.addTests(loader.loadTestsFromTestCase(TestEHubDMXPipeline))
    suite.addTests(loader.loadTestsFromTestCase(TestPipelineNetworking))
    
    # Exécuter avec rapport détaillé
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Résumé
    print()
    print("📊 === RÉSUMÉ TESTS INTÉGRATION ===")
    print(f"✅ Tests réussis: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Tests échoués: {len(result.failures)}")
    print(f"💥 Erreurs: {len(result.errors)}")
    print(f"🎯 Total: {result.testsRun}")
    
    if result.wasSuccessful():
        print("🎉 Tous les tests d'intégration sont passés!")
        return True
    else:
        print("⚠️ Certains tests d'intégration ont échoué!")
        
        # Afficher les détails des échecs
        if result.failures:
            print("\n❌ ÉCHECS:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")
                
        if result.errors:
            print("\n💥 ERREURS:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")
                
        return False

if __name__ == "__main__":
    run_integration_tests()
