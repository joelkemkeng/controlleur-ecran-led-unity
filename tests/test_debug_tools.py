"""
tests/test_debug_tools.py - Test d'intégration des outils de débogage eHuB/LED

Ce test vérifie que chaque fonctionnalité de tools/debug_tools.py fonctionne sans erreur.
- Mock le socket pour éviter les envois réels
- Teste la génération/envoi de messages UPDATE (séquentiel, couleur, unique)
- Teste l'envoi du message CONFIG réel
- Teste la checklist de prérequis
- Vérifie qu'aucune exception n'est levée

Utilisation :
-------------
$ python -m unittest tests/test_debug_tools.py
"""
import unittest
from unittest.mock import patch
import tools.debug_tools as dbg

class DebugToolsIntegrationTest(unittest.TestCase):
    @patch('socket.socket')
    def test_create_sequential_test(self, mock_socket):
        print("[TEST] Test séquentiel (chenillard)")
        dbg.create_sequential_test(count=3, delay=0)  # 3 entités, pas d'attente

    @patch('socket.socket')
    def test_create_color_sweep_test(self, mock_socket):
        print("[TEST] Test balayage couleurs")
        dbg.create_color_sweep_test(count=3, delay=0)

    @patch('socket.socket')
    def test_send_real_config_message(self, mock_socket):
        print("[TEST] Envoi message CONFIG réel")
        dbg.send_real_config_message()

    def test_checklist_prerequis(self):
        print("[TEST] Checklist de prérequis")
        dbg.checklist_prerequis()

    @patch('socket.socket')
    @patch('builtins.input', side_effect=["123", "10", "20", "30"])
    def test_send_single_entity(self, mock_input, mock_socket):
        print("[TEST] Envoi entité unique (mock input)")
        dbg.send_single_entity()

if __name__ == "__main__":
    unittest.main() 