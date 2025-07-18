"""
demo/animation_demo.py - Démonstration artistique LED

Ce script lance des animations artistiques (vague, arc-en-ciel, chenillard, pulsation) sur le pipeline LED existant.
- Utilise le pipeline principal (IntegratedLEDRouter)
- Menu interactif pour choisir l'animation
- Gestion d'erreur robuste et logs pédagogiques
- Compatible Windows, Linux, Mac, Raspbian

Utilisation :
-------------
$ python demo/animation_demo.py

"""
import time
import math
import threading
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.models import EntityUpdate
from main import IntegratedLEDRouter
from ehub.parser import parse_config_message

import socket
import struct
import gzip

def send_config_messages(port=8765, repeat=2):
    """
    Envoie deux messages CONFIG pour initialiser le mapping avant chaque animation.
    """
    # Plages extraites du tableau Excel fourni (mapping réel)
    ranges = [
        (0, 100, 169, 269), (0, 270, 399, 569), (0, 400, 569, 1169), (0, 700, 869, 1569),
        (0, 1000, 1169, 2339), (0, 1300, 1469, 2569), (0, 1600, 1769, 3369), (0, 1900, 2069, 3969),
        (0, 2200, 2369, 4569), (0, 2500, 2669, 5169), (0, 2800, 2969, 5769), (0, 3100, 3269, 6369),
        (0, 3400, 3569, 6969), (0, 3700, 3869, 7569), (0, 4000, 4169, 8169), (0, 4300, 4469, 8769),
        (0, 4600, 4769, 9369), (0, 4770, 4858, 9457), # controller1
        (0, 5100, 5269, 10269), (0, 5270, 5358, 10357), (0, 5400, 5569, 10569), (0, 5700, 5869, 10769),
        (0, 6000, 6169, 10969), (0, 6300, 6469, 11169), (0, 6600, 6769, 11369), (0, 6900, 7069, 11569),
        (0, 7200, 7369, 11769), (0, 7500, 7669, 11969), (0, 7800, 7969, 12169), (0, 8100, 8269, 12369),
        (0, 8400, 8569, 12569), (0, 8700, 8869, 12769), (0, 9000, 9169, 12969), (0, 9300, 9469, 13169),
        (0, 9600, 9769, 13369), (0, 9770, 9858, 13457), # controller2
        (0, 10100, 10269, 13839), (0, 10270, 10358, 13927), (0, 10400, 10569, 14139), (0, 10700, 10869, 14339),
        (0, 11000, 11169, 14569), (0, 11300, 11469, 14769), (0, 11600, 11769, 14969), (0, 11900, 12069, 15169),
        (0, 12200, 12369, 15369), (0, 12500, 12669, 15569), (0, 12800, 12969, 15769), (0, 13100, 13269, 15969),
        (0, 13400, 13569, 16169), (0, 13700, 13869, 16369), (0, 14000, 14169, 16569), (0, 14300, 14469, 16769),
        (0, 14700, 14858, 16927), # controller3
        (0, 15100, 15269, 17369), (0, 15270, 15358, 17457), (0, 15400, 15569, 17669), (0, 15700, 15869, 17869),
        (0, 16000, 16169, 18069), (0, 16300, 16469, 18269), (0, 16600, 16769, 18469), (0, 16900, 17069, 18669),
        (0, 17200, 17369, 18869), (0, 17500, 17669, 19069), (0, 17800, 17969, 19269), (0, 18100, 18269, 19469),
        (0, 18400, 18569, 19669), (0, 18700, 18869, 19869), (0, 19000, 19169, 20069), (0, 19300, 19469, 20269),
        (0, 19700, 19858, 20427), # controller4
    ]
    payload = b''.join([struct.pack('<HHHH', *r) for r in ranges])
    compressed = gzip.compress(payload)
    header = b'eHuB\x01\x00' + struct.pack('<H', len(ranges)) + struct.pack('<H', len(compressed))
    message = header + compressed
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for _ in range(repeat):
        sock.sendto(message, ('127.0.0.1', port))
    sock.close()
    print(f"[CONFIG] {repeat} messages CONFIG envoyés pour initialiser le mapping.")

class AnimationDemo:
    """
    Classe de démonstration artistique LED.
    Propose plusieurs animations (vague, arc-en-ciel, chenillard, pulsation).
    """
    def __init__(self, router):
        self.router = router
        self.running = False

    def start(self):
        self.running = True
        print("\n🎨 Démonstration artistique démarrée")
        print("Avant chaque animation, le mapping va être initialisé (messages CONFIG envoyés).")
        print("Animations disponibles :")
        print("1. Vague de couleur")
        print("2. Arc-en-ciel rotatif")
        print("3. Chenillard")
        print("4. Pulsation globale")
        print("5. Balayage multi-contrôleurs (2 contrôleurs)")
        print("6. Balayage 3 contrôleurs")
        print("q. Quitter la démo")
        self.router.receiver.start_listening(self.router.handle_update, self.router.handle_config)
        while self.running:
            choice = input("Choix (1-6/q) : ").strip()
            if choice in ["1", "2", "3", "4", "5", "6"]:
                send_config_messages()
                time.sleep(0.5)  # Laisse le temps au thread de traiter le message CONFIG
                confirm = input("Messages CONFIG envoyés. Appuie sur Entrée pour lancer l'animation, ou 'q' pour annuler : ").strip().lower()
                if confirm == 'q':
                    continue
                if choice == "1":
                    self.color_wave_animation()
                elif choice == "2":
                    self.rainbow_animation()
                elif choice == "3":
                    self.chenillard_animation()
                elif choice == "4":
                    self.pulse_animation()
                elif choice == "5":
                    self.multi_controller_sweep()
                elif choice == "6":
                    self.three_controller_sweep()
            elif choice == "q":
                self.running = False
            else:
                print("Entrée invalide. Choisis 1, 2, 3, 4, 5, 6 ou q.")
        print("🛑 Démonstration arrêtée.")

    def color_wave_animation(self, duration=10.0):
        """Animation de vague de couleur traversant l'écran."""
        print("[ANIMATION] Vague de couleur (10s)")
        start_time = time.time()
        try:
            while time.time() - start_time < duration and self.running:
                t = time.time() - start_time
                entities = []
                for entity_id in range(100, 300):
                    pos = (entity_id - 100) / 200.0
                    wave = math.sin(pos * 2 * math.pi + t * 2)
                    intensity = int((wave + 1) * 127.5)
                    r = intensity if pos < 0.33 else 0
                    g = intensity if 0.33 <= pos < 0.66 else 0
                    b = intensity if pos >= 0.66 else 0
                    entities.append(EntityUpdate(entity_id, r, g, b, 0))
                self.router.handle_update(entities)
                time.sleep(1/30)
        except Exception as e:
            print(f"[ERREUR] Animation vague : {e}")

    def rainbow_animation(self, duration=8.0):
        """Effet arc-en-ciel rotatif."""
        print("[ANIMATION] Arc-en-ciel rotatif (8s)")
        start_time = time.time()
        try:
            while time.time() - start_time < duration and self.running:
                t = time.time() - start_time
                entities = []
                for entity_id in range(100, 200):
                    pos = (entity_id - 100) / 100.0
                    hue = (pos + t * 0.5) % 1.0
                    r, g, b = self.hsv_to_rgb(hue, 1.0, 1.0)
                    entities.append(EntityUpdate(entity_id, r, g, b, 0))
                self.router.handle_update(entities)
                time.sleep(1/25)
        except Exception as e:
            print(f"[ERREUR] Animation arc-en-ciel : {e}")

    def chenillard_animation(self, duration=8.0):
        """Chenillard classique (une LED allumée à la fois)."""
        print("[ANIMATION] Chenillard (8s)")
        start_time = time.time()
        try:
            while time.time() - start_time < duration and self.running:
                t = int((time.time() - start_time) * 10) % 100
                entities = []
                for entity_id in range(100, 200):
                    if entity_id - 100 == t:
                        entities.append(EntityUpdate(entity_id, 255, 255, 255, 0))
                    else:
                        entities.append(EntityUpdate(entity_id, 0, 0, 0, 0))
                self.router.handle_update(entities)
                time.sleep(0.1)
        except Exception as e:
            print(f"[ERREUR] Animation chenillard : {e}")

    def pulse_animation(self, duration=6.0):
        """Pulsation douce de toutes les LEDs."""
        print("[ANIMATION] Pulsation globale (6s)")
        start_time = time.time()
        try:
            while time.time() - start_time < duration and self.running:
                t = time.time() - start_time
                pulse = math.sin(t * 2 * math.pi / 2)
                intensity = int((pulse + 1) * 127.5)
                entities = [EntityUpdate(entity_id, intensity, intensity, intensity, 0) for entity_id in range(100, 200)]
                self.router.handle_update(entities)
                time.sleep(1/20)
        except Exception as e:
            print(f"[ERREUR] Animation pulsation : {e}")

    def multi_controller_sweep(self, duration=5.0):
        """Balayage simple sur deux contrôleurs (ex : entités 100 et 5100)."""
        print("[ANIMATION] Balayage multi-contrôleurs (2 contrôleurs, 5s)")
        ids = [100, 5100]  # 100 = contrôleur 1, 5100 = contrôleur 2
        start_time = time.time()
        try:
            while time.time() - start_time < duration and self.running:
                entities = []
                for eid in ids:
                    t = time.time() - start_time
                    r = int((math.sin(t) + 1) * 127.5)
                    g = int((math.cos(t) + 1) * 127.5)
                    b = int((math.sin(t + 1) + 1) * 127.5)
                    entities.append(EntityUpdate(eid, r, g, b, 0))
                    # Log du contrôleur ciblé
                    mapping = self.router.mapper.entity_to_dmx.get(eid)
                    ctrl_num = self.get_controller_number(mapping['controller_ip']) if mapping else '?'
                    print(f"[LOG] Entité {eid} → Contrôleur {ctrl_num} (IP {mapping['controller_ip'] if mapping else '?'}) : RGB({r},{g},{b})")
                self.router.handle_update(entities)
                time.sleep(1/10)
        except Exception as e:
            print(f"[ERREUR] Animation multi-contrôleurs : {e}")

    def three_controller_sweep(self, duration=5.0):
        """Balayage simple sur trois contrôleurs (ex : entités 100, 5100, 10100)."""
        print("[ANIMATION] Balayage 3 contrôleurs (5s)")
        ids = [100, 5100, 10100]  # 100 = ctrl1, 5100 = ctrl2, 10100 = ctrl3
        start_time = time.time()
        try:
            while time.time() - start_time < duration and self.running:
                entities = []
                for eid in ids:
                    t = time.time() - start_time
                    r = int((math.sin(t + eid) + 1) * 127.5)
                    g = int((math.cos(t + eid) + 1) * 127.5)
                    b = int((math.sin(t + 2 + eid) + 1) * 127.5)
                    entities.append(EntityUpdate(eid, r, g, b, 0))
                    mapping = self.router.mapper.entity_to_dmx.get(eid)
                    ctrl_num = self.get_controller_number(mapping['controller_ip']) if mapping else '?'
                    print(f"[LOG] Entité {eid} → Contrôleur {ctrl_num} (IP {mapping['controller_ip'] if mapping else '?'}) : RGB({r},{g},{b})")
                self.router.handle_update(entities)
                time.sleep(1/10)
        except Exception as e:
            print(f"[ERREUR] Animation 3 contrôleurs : {e}")

    def get_controller_number(self, ip):
        """Retourne le numéro du contrôleur (1, 2, 3, ...) à partir de l'IP, selon la config."""
        for idx, (name, ctrl) in enumerate(self.router.config_mgr.config.controllers.items(), 1):
            if ctrl.ip == ip:
                return idx
        return '?'

    @staticmethod
    def hsv_to_rgb(h, s, v):
        """Conversion HSV vers RGB (0-255)"""
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return int(r * 255), int(g * 255), int(b * 255)

if __name__ == "__main__":
    print("🚦 Initialisation du routeur LED pour la démo...")
    try:
        router = IntegratedLEDRouter()
        if not router.initialize():
            print("❌ Impossible d'initialiser le pipeline. Vérifie la config et relance.")
        else:
            demo = AnimationDemo(router)
            demo.start()
            router.stop()
    except KeyboardInterrupt:
        print("\n🛑 Démo interrompue par l'utilisateur.")
    except Exception as e:
        print(f"❌ Erreur fatale : {e}") 