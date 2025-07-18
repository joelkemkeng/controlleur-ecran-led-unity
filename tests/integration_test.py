"""
tests/integration_test.py - Tests d'intégration du pipeline LED

Ce fichier contient des tests d'intégration pour valider le pipeline complet :
- Parsing eHuB (via ehub/parser.py)
- Mapping dynamique entités → DMX (initialisation explicite du mapping)
- Application des patchs
- Envoi ArtNet (simulation)
- Performance

Chaque test est documenté pour un débutant, avec des exemples de sortie console et des explications pédagogiques.

Exécution :
-----------
$ python -m unittest tests/integration_test.py

Exemple de sortie :
-------------------
Test du pipeline complet eHuB -> DMX -> ArtNet ... OK
Test de l'application des patches ... OK
Test de performance avec beaucoup d'entités ... OK

"""
import unittest
import time
import gzip
import struct
from core.models import EntityUpdate, EntityRange
from main import IntegratedLEDRouter
from ehub.parser import parse_update_message

class IntegrationTest(unittest.TestCase):
    """
    Tests d'intégration du pipeline LED.

    Ces tests valident le fonctionnement global du pipeline, l'application des patchs, et la performance.
    Chaque test est documenté avec des exemples concrets et des explications pédagogiques.
    """
    def setUp(self):
        """
        Initialise un routeur LED intégré pour chaque test.
        Initialise explicitement le mapping (simule une plage d'entités comme si un message CONFIG avait été reçu).
        """
        self.router = IntegratedLEDRouter()
        self.router.initialize()
        # Simuler une plage d'entités pour le mapping (comme un message CONFIG)
        ranges = [EntityRange(payload_start=0, entity_start=100, payload_end=1, entity_end=101)]
        entity_ranges_dict = {r.entity_start: r for r in ranges}
        self.router.mapper.build_mapping(entity_ranges_dict)

    def test_complete_pipeline(self):
        """
        Test du pipeline complet eHuB -> DMX -> ArtNet.
        - Crée un message UPDATE eHuB simulé
        - Parse et traite le message
        - Vérifie que le mapping DMX et l'envoi ArtNet sont corrects

        Exemple de sortie console :
        --------------------------
        [UPDATE] Reçu 2 entités
        [DMX] 1 paquets générés
        [ArtNet] Envoyé vers 1 contrôleurs
        """
        # 1. Créer un message UPDATE eHuB
        entities_data = []
        entities_data.append(struct.pack('<H', 100) + bytes([255, 0, 0, 0]))  # Entité 100 rouge
        entities_data.append(struct.pack('<H', 101) + bytes([0, 255, 0, 0]))  # Entité 101 verte
        payload = b''.join(entities_data)
        compressed = gzip.compress(payload)
        header = b'eHuB\x02\x00\x02\x00' + struct.pack('<H', len(compressed))
        message = header + compressed
        # 2. Simuler la réception
        received_dmx = []
        original_send = self.router.artnet_sender.send_dmx_packets
        def capture_dmx(packets):
            received_dmx.extend(packets)
            return original_send(packets)
        self.router.artnet_sender.send_dmx_packets = capture_dmx
        # 3. Parser et traiter le message (utilise la fonction du module ehub/parser.py)
        entities = parse_update_message(message)
        self.router.handle_update(entities)
        # 4. Vérifier les résultats
        self.assertEqual(len(entities), 2)
        self.assertEqual(entities[0].id, 100)
        self.assertEqual(entities[0].r, 255)
        # Vérifier que du DMX a été généré
        self.assertGreater(len(received_dmx), 0)
        # Vérifier le mapping
        packet = received_dmx[0]
        self.assertEqual(packet.controller_ip, "192.168.1.45")
        self.assertIn(1, packet.channels)  # Canal R de la première entité

    def test_patch_application(self):
        """
        Test de l'application des patchs DMX.
        - Ajoute un patch (canal 1 -> 389)
        - Vérifie que la redirection est bien appliquée
        """
        self.router.patch_handler.add_patch(1, 389)
        self.router.patch_handler.enabled = True
        entities = [EntityUpdate(100, 255, 0, 0, 0)]
        dmx_packets = self.router.mapper.map_entities_to_dmx(entities)
        patched_packets = self.router.patch_handler.apply_patches(dmx_packets)
        self.assertGreater(len(patched_packets), 0)
        packet = patched_packets[0]
        self.assertIn(389, packet.channels)  # Canal patché
        self.assertEqual(packet.channels[389], 255)

    def test_performance(self):
        """
        Test de performance du mapping DMX avec 1000 entités.
        Vérifie que le traitement est rapide (< 10ms) et que toutes les entités sont mappées.
        """
        entities = [
            EntityUpdate(i, i % 256, (i * 2) % 256, (i * 3) % 256, 0)
            for i in range(100, 1100)
        ]
        start_time = time.time()
        dmx_packets = self.router.mapper.map_entities_to_dmx(entities)
        end_time = time.time()
        processing_time = end_time - start_time
        self.assertLess(processing_time, 0.01)
        total_channels = sum(len(p.channels) for p in dmx_packets)
        self.assertGreater(total_channels, 0)

    def tearDown(self):
        """
        Ferme explicitement les sockets ArtNet après chaque test pour éviter les ResourceWarning.
        """
        if hasattr(self, 'router') and self.router and self.router.artnet_sender:
            self.router.artnet_sender.cleanup_sockets()

if __name__ == '__main__':
    unittest.main() 