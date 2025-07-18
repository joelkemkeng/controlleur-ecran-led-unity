"""
tests/test_animation_demo.py - Test d'intégration de la démonstration artistique LED

Ce test vérifie que chaque animation du script demo/animation_demo.py fonctionne correctement avec le pipeline réel.
- Initialise le pipeline (IntegratedLEDRouter)
- Lance chaque animation pour une courte durée
- Vérifie qu'aucune exception n'est levée
- Arrête proprement le pipeline

Utilisation :
-------------
$ python -m unittest tests/test_animation_demo.py
"""
import unittest
import time
from main import IntegratedLEDRouter
from demo.animation_demo import AnimationDemo

class AnimationDemoIntegrationTest(unittest.TestCase):
    def setUp(self):
        print("\n[TEST] Initialisation du pipeline pour la démo...")
        self.router = IntegratedLEDRouter()
        ok = self.router.initialize()
        self.assertTrue(ok, "Le pipeline n'a pas pu être initialisé.")
        self.demo = AnimationDemo(self.router)

    def tearDown(self):
        print("[TEST] Arrêt du pipeline après la démo.")
        self.router.stop()

    def test_color_wave_animation(self):
        print("[TEST] Animation : vague de couleur (1s)")
        self.demo.color_wave_animation(duration=1.0)

    def test_rainbow_animation(self):
        print("[TEST] Animation : arc-en-ciel rotatif (1s)")
        self.demo.rainbow_animation(duration=1.0)

    def test_chenillard_animation(self):
        print("[TEST] Animation : chenillard (1s)")
        self.demo.chenillard_animation(duration=1.0)

    def test_pulse_animation(self):
        print("[TEST] Animation : pulsation globale (1s)")
        self.demo.pulse_animation(duration=1.0)

if __name__ == "__main__":
    unittest.main() 