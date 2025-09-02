#!/usr/bin/env python3
"""
🚀 Test de performance pour Étape 3
Valide les performances et capacités du pipeline DMX
"""

import sys
import time
import threading
import random
from pathlib import Path

# Import du module à tester
sys.path.append(str(Path(__file__).parent.parent))
from ehub_complete_pipeline_mapping_dmx import EHubDMXPipeline, DMXMapper, LEDMapping, DMXUniverse

# Import des classes de l'étape 2
sys.path.append('/home/joel/projet_ecran/controlleur-ecran-led-unity/FINAL-DEV/etape-02-decodage-ehub')
from ehub_complete_pipeline_decoder import EHubEntity, EHubPacket

class PerformanceValidator:
    """Validateur de performance pour l'étape 3"""
    
    def __init__(self):
        self.pipeline = None
        self.test_port = 8768
        
    def setup_test_environment(self):
        """Configure l'environnement de test"""
        print("🔧 Configuration environnement de test...")
        
        # Créer le pipeline
        self.pipeline = EHubDMXPipeline(port=self.test_port)
        
        # Créer un mapper avec beaucoup d'entités pour les tests
        mapper = DMXMapper()
        
        # Simuler 1000 entités sur 4 contrôleurs
        controllers = ["192.168.1.45", "192.168.1.46", "192.168.1.47", "192.168.1.48"]
        entity_id = 1
        
        for controller in controllers:
            for universe in range(32):  # 32 univers par contrôleur
                for channel in range(0, 512, 3):  # RGB tous les 3 canaux
                    if entity_id <= 1000:
                        mapping = LEDMapping(entity_id, controller, universe, channel)
                        mapper.mappings[entity_id] = mapping
                        
                        # Créer l'univers si pas existant
                        universe_key = (controller, universe)
                        if universe_key not in mapper.universes:
                            mapper.universes[universe_key] = DMXUniverse(
                                universe, controller, bytearray(512)
                            )
                        
                        entity_id += 1
        
        self.pipeline.dmx_mapper = mapper
        
        print(f"✅ Configuré {len(mapper.mappings)} entités sur {len(mapper.universes)} univers")
        return True
        
    def test_single_packet_performance(self):
        """Test performance traitement d'un paquet"""
        print("\n⚡ Test performance paquet unique...")
        
        # Créer un gros paquet avec 500 entités
        entities = []
        for i in range(1, 501):
            entities.append(EHubEntity(
                i, 
                random.randint(0, 255),
                random.randint(0, 255), 
                random.randint(0, 255),
                0
            ))
        
        packet = EHubPacket(2, 1, len(entities), len(entities) * 6, entities)
        
        # Mesurer le temps de traitement
        start_time = time.time()
        result = self.pipeline.process_ehub_packet(packet)
        process_time = time.time() - start_time
        
        print(f"📊 Paquet de {len(entities)} entités traité en {process_time:.4f}s")
        print(f"📊 {len(result)} univers modifiés")
        print(f"📊 Vitesse: {len(entities)/process_time:.0f} entités/seconde")
        
        # Vérifications
        assert process_time < 0.1, f"Traitement trop lent: {process_time}s"
        assert len(result) > 0, "Aucun univers modifié"
        
        print("✅ Performance acceptable")
        return True
        
    def test_sustained_performance(self):
        """Test performance soutenue"""
        print("\n🔄 Test performance soutenue...")
        
        total_entities = 0
        total_packets = 0
        start_time = time.time()
        
        # Traiter 100 paquets rapidement
        for packet_num in range(100):
            # Paquet aléatoire de 50-200 entités
            num_entities = random.randint(50, 200)
            entities = []
            
            for i in range(num_entities):
                entity_id = random.randint(1, 1000)
                entities.append(EHubEntity(
                    entity_id,
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                    0
                ))
            
            packet = EHubPacket(2, 1, len(entities), len(entities) * 6, entities)
            result = self.pipeline.process_ehub_packet(packet)
            
            total_entities += len(entities)
            total_packets += 1
            
            # Petit délai pour simuler la réception réseau
            if packet_num % 10 == 0:
                time.sleep(0.001)
        
        total_time = time.time() - start_time
        
        print(f"📊 {total_packets} paquets traités en {total_time:.3f}s")
        print(f"📊 {total_entities} entités totales")
        print(f"📊 Vitesse moyenne: {total_packets/total_time:.1f} paquets/s")
        print(f"📊 Débit entités: {total_entities/total_time:.0f} entités/s")
        
        # Vérifications
        packets_per_sec = total_packets / total_time
        entities_per_sec = total_entities / total_time
        
        assert packets_per_sec > 100, f"Débit paquets trop faible: {packets_per_sec:.1f}/s"
        assert entities_per_sec > 5000, f"Débit entités trop faible: {entities_per_sec:.0f}/s"
        
        print("✅ Performance soutenue acceptable")
        return True
        
    def test_memory_usage(self):
        """Test usage mémoire"""
        print("\n🧠 Test usage mémoire...")
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"📊 Mémoire initiale: {initial_memory:.1f} MB")
        
        # Traiter beaucoup de paquets
        for i in range(500):
            entities = []
            for j in range(100):
                entities.append(EHubEntity(
                    random.randint(1, 1000),
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                    0
                ))
            
            packet = EHubPacket(2, 1, len(entities), len(entities) * 6, entities)
            result = self.pipeline.process_ehub_packet(packet)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"📊 Mémoire finale: {final_memory:.1f} MB")
        print(f"📊 Augmentation: {memory_increase:.1f} MB")
        
        # Vérification
        assert memory_increase < 50, f"Augmentation mémoire excessive: {memory_increase:.1f}MB"
        
        print("✅ Usage mémoire acceptable")
        return True
        
    def test_universe_capacity(self):
        """Test capacité des univers"""
        print("\n🌍 Test capacité univers...")
        
        mapper = self.pipeline.dmx_mapper
        
        print(f"📊 Univers configurés: {len(mapper.universes)}")
        print(f"📊 Entités mappées: {len(mapper.mappings)}")
        
        # Vérifier quelques univers
        universe_sample = list(mapper.universes.items())[:5]
        for (controller, universe_num), universe in universe_sample:
            entities_in_universe = 0
            for entity_id, mapping in mapper.mappings.items():
                if mapping.controller_ip == controller and mapping.universe == universe_num:
                    entities_in_universe += 1
            
            print(f"📊 Univers {controller}:{universe_num} = {entities_in_universe} entités")
        
        # Tester saturation d'un univers
        test_universe = universe_sample[0][1] if universe_sample else None
        if test_universe:
            # Remplir complètement l'univers
            for i in range(0, 512, 3):
                test_universe.set_rgb(i, 255, 128, 64)
            
            # Vérifier que les données sont correctes
            assert test_universe.dmx_data[0] == 255
            assert test_universe.dmx_data[1] == 128
            assert test_universe.dmx_data[2] == 64
            
            print("✅ Saturation univers testée")
        
        return True
        
    def test_error_resilience(self):
        """Test résistance aux erreurs"""
        print("\n🛡️ Test résistance erreurs...")
        
        # Test avec entités non mappées
        unmapped_entities = [
            EHubEntity(99999, 255, 0, 0, 0),  # ID inexistant
            EHubEntity(88888, 0, 255, 0, 0),  # ID inexistant
        ]
        
        packet = EHubPacket(2, 1, len(unmapped_entities), len(unmapped_entities) * 6, unmapped_entities)
        
        try:
            result = self.pipeline.process_ehub_packet(packet)
            print("✅ Entités non mappées gérées sans crash")
        except Exception as e:
            print(f"❌ Erreur avec entités non mappées: {e}")
            return False
        
        # Test avec données invalides
        try:
            invalid_packet = EHubPacket(2, 1, 1, 6, [])  # Données incohérentes
            result = self.pipeline.process_ehub_packet(invalid_packet)
            print("✅ Données invalides gérées")
        except Exception as e:
            print(f"⚠️ Erreur données invalides (acceptable): {e}")
        
        return True
        
    def run_all_tests(self):
        """Lance tous les tests de performance"""
        print("🚀 === TESTS PERFORMANCE ÉTAPE 3 ===")
        print()
        
        tests = [
            ("Configuration environnement", self.setup_test_environment),
            ("Performance paquet unique", self.test_single_packet_performance),
            ("Performance soutenue", self.test_sustained_performance),
            ("Usage mémoire", self.test_memory_usage),
            ("Capacité univers", self.test_universe_capacity),
            ("Résistance erreurs", self.test_error_resilience),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                print(f"\n{'='*50}")
                print(f"🧪 {test_name}")
                print('='*50)
                
                success = test_func()
                if success:
                    passed += 1
                    print(f"✅ {test_name} - RÉUSSI")
                else:
                    print(f"❌ {test_name} - ÉCHOUÉ")
                    
            except Exception as e:
                print(f"💥 {test_name} - ERREUR: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n🎯 === RÉSUMÉ PERFORMANCE ===")
        print(f"✅ Tests réussis: {passed}/{total}")
        print(f"📊 Taux de réussite: {passed/total*100:.1f}%")
        
        if passed == total:
            print("🎉 Tous les tests de performance sont passés!")
            print("🚀 L'étape 3 est validée et prête pour l'étape 4!")
        else:
            print("⚠️ Certains tests ont échoué, vérification nécessaire")
            
        return passed == total

def main():
    """Point d'entrée principal"""
    validator = PerformanceValidator()
    return validator.run_all_tests()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
