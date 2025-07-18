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

def validate_mapping_strategy(router):
    """
    Stratégie de validation complète du mapping pour s'assurer que tout fonctionne.
    """
    print("\n🔍 === VALIDATION STRATÉGIQUE DU MAPPING ===")
    
    # Test 1: Vérifier que le mapping a été construit
    mapping_count = len(router.mapper.entity_to_dmx)
    print(f"✅ Test 1 - Mapping construit: {mapping_count} entités mappées")
    
    if mapping_count == 0:
        print("❌ ERREUR: Aucune entité mappée - Envoi CONFIG nécessaire")
        return False
    
    # Test 2: Vérifier la couverture des contrôleurs
    controller_coverage = {}
    for entity_id, mapping in router.mapper.entity_to_dmx.items():
        ctrl_ip = mapping['controller_ip']
        if ctrl_ip not in controller_coverage:
            controller_coverage[ctrl_ip] = []
        controller_coverage[ctrl_ip].append(entity_id)
    
    print(f"✅ Test 2 - Couverture contrôleurs: {len(controller_coverage)} contrôleurs détectés")
    for ip, entities in controller_coverage.items():
        ctrl_num = None
        for idx, (name, ctrl) in enumerate(router.config_mgr.config.controllers.items(), 1):
            if ctrl.ip == ip:
                ctrl_num = idx
                break
        print(f"   - Contrôleur {ctrl_num} ({ip}): {len(entities)} entités ({min(entities)}-{max(entities)})")
    
    # Test 3: Vérifier les plages d'entités attendues
    expected_ranges = [
        (100, 4858, "192.168.1.45"),
        (5100, 9858, "192.168.1.46"),
        (10100, 14858, "192.168.1.47"),
        (15100, 19858, "192.168.1.48")
    ]
    
    print("✅ Test 3 - Validation des plages d'entités:")
    all_ranges_ok = True
    for start_id, end_id, expected_ip in expected_ranges:
        # Tester quelques entités dans cette plage
        test_entities = [start_id, start_id + 100, start_id + 500, min(start_id + 1000, end_id)]
        range_ok = True
        for test_id in test_entities:
            if test_id in router.mapper.entity_to_dmx:
                mapping = router.mapper.entity_to_dmx[test_id]
                if mapping['controller_ip'] != expected_ip:
                    print(f"   ❌ Entité {test_id}: IP {mapping['controller_ip']} != {expected_ip}")
                    range_ok = False
                    all_ranges_ok = False
            else:
                print(f"   ⚠️  Entité {test_id}: non mappée")
        
        if range_ok:
            print(f"   ✅ Plage {start_id}-{end_id} → {expected_ip}: OK")
        else:
            print(f"   ❌ Plage {start_id}-{end_id} → {expected_ip}: ERREUR")
    
    # Test 4: Test fonctionnel avec entités de chaque contrôleur
    print("✅ Test 4 - Test fonctionnel:")
    test_entities = [
        EntityUpdate(100, 255, 0, 0, 0),    # Contrôleur 1
        EntityUpdate(5100, 0, 255, 0, 0),   # Contrôleur 2
        EntityUpdate(10100, 0, 0, 255, 0),  # Contrôleur 3
        EntityUpdate(15100, 255, 255, 0, 0) # Contrôleur 4
    ]
    
    try:
        dmx_packets = router.mapper.map_entities_to_dmx(test_entities)
        print(f"   ✅ Mapping fonctionnel: {len(dmx_packets)} paquets DMX générés")
        
        # Vérifier que tous les contrôleurs sont représentés
        controller_ips = set()
        for packet in dmx_packets:
            controller_ips.add(packet.controller_ip)
        
        if len(controller_ips) == 4:
            print(f"   ✅ Tous les contrôleurs actifs: {sorted(controller_ips)}")
        else:
            print(f"   ⚠️  Seulement {len(controller_ips)} contrôleurs actifs: {sorted(controller_ips)}")
        
    except Exception as e:
        print(f"   ❌ Erreur mapping fonctionnel: {e}")
        all_ranges_ok = False
    
    # Résumé final
    print(f"\n🎯 === RÉSUMÉ DE VALIDATION ===")
    if all_ranges_ok and mapping_count > 0:
        print("✅ MAPPING VALIDE - Toutes les animations devraient fonctionner")
        return True
    else:
        print("❌ MAPPING INVALIDE - Corrections nécessaires")
        return False

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
        print("4. Pulsation globale - Tous contrôleurs")
        print("5. Balayage multi-contrôleurs (2 contrôleurs)")
        print("6. Balayage 3 contrôleurs")
        print("7. Test complet écran - Tous contrôleurs")
        print("8. Test messages eHuB manuel")
        print("v. Valider le mapping")
        print("q. Quitter la démo")
        self.router.receiver.start_listening(self.router.handle_update, self.router.handle_config)
        while self.running:
            choice = input("Choix (1-8/v/q) : ").strip()
            if choice in ["1", "2", "3", "4", "5", "6", "7"]:
                send_config_messages()
                time.sleep(0.5)  # Laisse le temps au thread de traiter le message CONFIG
                confirm = input("Messages CONFIG envoyés. Appuie sur Entrée pour lancer l'animation, ou 'q' pour annuler : ").strip().lower()
                if confirm == 'q':
                    continue
                # Initialiser l'écran (éteindre toutes les LEDs)
                self.initialize_screen()
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
                elif choice == "7":
                    self.full_screen_test_animation()
            elif choice == "8":
                self.manual_ehub_test()
            elif choice.lower() == "v":
                send_config_messages()
                time.sleep(0.5)
                is_valid = validate_mapping_strategy(self.router)
                if is_valid:
                    print("✅ Mapping validé avec succès - Toutes les animations devraient fonctionner")
                else:
                    print("❌ Problème détecté - Vérifiez la configuration")
            elif choice == "q":
                self.running = False
            else:
                print("Entrée invalide. Choisis 1, 2, 3, 4, 5, 6, 7, 8, v ou q.")
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
        """Pulsation douce de toutes les LEDs sur tous les contrôleurs."""
        print("[ANIMATION] Pulsation globale - Tous contrôleurs (6s)")
        
        # Plages d'entités par contrôleur
        controller_ranges = [
            (100, 4858),      # Contrôleur 1
            (5100, 9858),     # Contrôleur 2
            (10100, 14858),   # Contrôleur 3
            (15100, 19858)    # Contrôleur 4
        ]
        
        start_time = time.time()
        try:
            while time.time() - start_time < duration and self.running:
                t = time.time() - start_time
                pulse = math.sin(t * 2 * math.pi / 2)
                intensity = int((pulse + 1) * 127.5)
                
                entities = []
                for start_id, end_id in controller_ranges:
                    # Échantillonnage pour éviter trop d'entités (tous les 20 pixels)
                    for entity_id in range(start_id, min(start_id + 200, end_id), 20):
                        entities.append(EntityUpdate(entity_id, intensity, intensity, intensity, 0))
                
                self.router.handle_update(entities)
                if len(entities) > 0:
                    print(f"[LOG] Pulsation: {len(entities)} entités, intensité {intensity}")
                time.sleep(1/20)
        except Exception as e:
            print(f"[ERREUR] Animation pulsation : {e}")

    def multi_controller_sweep(self, duration=5.0):
        """Balayage progressif sur contrôleurs 1 et 2 avec vraies plages d'entités."""
        print("[ANIMATION] Balayage multi-contrôleurs (Contrôleurs 1-2, 5s)")
        
        # Vraies plages pour contrôleurs 1 et 2
        controller_ranges = [
            (100, 4858),      # Contrôleur 1
            (5100, 9858),     # Contrôleur 2
        ]
        
        start_time = time.time()
        try:
            while time.time() - start_time < duration and self.running:
                t = time.time() - start_time
                entities = []
                
                for ctrl_idx, (start_id, end_id) in enumerate(controller_ranges):
                    # Couleur différente par contrôleur
                    phase_offset = ctrl_idx * math.pi / 2
                    r = int((math.sin(t + phase_offset) + 1) * 127.5)
                    g = int((math.cos(t + phase_offset) + 1) * 127.5)
                    b = int((math.sin(t + phase_offset + 1) + 1) * 127.5)
                    
                    # Vague qui traverse le contrôleur
                    wave_pos = (t * 500) % (end_id - start_id)  # Vitesse de vague
                    
                    for i in range(0, min(300, end_id - start_id), 15):  # Échantillonnage
                        distance = abs(i - wave_pos)
                        if distance < 50:  # Rayon de la vague
                            intensity_factor = 1 - (distance / 50)
                            entity_id = start_id + i
                            entities.append(EntityUpdate(
                                entity_id, 
                                int(r * intensity_factor), 
                                int(g * intensity_factor), 
                                int(b * intensity_factor), 
                                0
                            ))
                
                self.router.handle_update(entities)
                if t < 2:  # Log seulement les 2 premières secondes
                    active_controllers = set()
                    for entity in entities[:3]:
                        mapping = self.router.mapper.entity_to_dmx.get(entity.id)
                        if mapping:
                            ctrl_num = self.get_controller_number(mapping['controller_ip'])
                            active_controllers.add(ctrl_num)
                    print(f"[LOG] t={t:.1f}s - {len(entities)} entités - Contrôleurs: {sorted(active_controllers)}")
                
                time.sleep(1/25)
        except Exception as e:
            print(f"[ERREUR] Animation multi-contrôleurs : {e}")

    def three_controller_sweep(self, duration=5.0):
        """Balayage progressif sur contrôleurs 1, 2, 3 avec vraies plages d'entités."""
        print("[ANIMATION] Balayage 3 contrôleurs (Contrôleurs 1-2-3, 5s)")
        
        # Vraies plages pour contrôleurs 1, 2, 3
        controller_ranges = [
            (100, 4858),      # Contrôleur 1
            (5100, 9858),     # Contrôleur 2
            (10100, 14858),   # Contrôleur 3
        ]
        
        start_time = time.time()
        try:
            while time.time() - start_time < duration and self.running:
                t = time.time() - start_time
                entities = []
                
                for ctrl_idx, (start_id, end_id) in enumerate(controller_ranges):
                    # Couleur et phase différente par contrôleur
                    phase_offset = ctrl_idx * math.pi * 2 / 3  # 120° entre chaque contrôleur
                    
                    # Couleurs RGB cycliques
                    if ctrl_idx == 0:  # Contrôleur 1 - Rouge dominant
                        r = int((math.sin(t + phase_offset) + 1) * 200)
                        g = int((math.sin(t + phase_offset + 1) + 1) * 50)
                        b = int((math.sin(t + phase_offset + 2) + 1) * 50)
                    elif ctrl_idx == 1:  # Contrôleur 2 - Vert dominant
                        r = int((math.sin(t + phase_offset) + 1) * 50)
                        g = int((math.sin(t + phase_offset + 1) + 1) * 200)
                        b = int((math.sin(t + phase_offset + 2) + 1) * 50)
                    else:  # Contrôleur 3 - Bleu dominant
                        r = int((math.sin(t + phase_offset) + 1) * 50)
                        g = int((math.sin(t + phase_offset + 1) + 1) * 50)
                        b = int((math.sin(t + phase_offset + 2) + 1) * 200)
                    
                    # Vague qui traverse le contrôleur
                    wave_pos = (t * 800) % (end_id - start_id)  # Vitesse de vague
                    
                    for i in range(0, min(400, end_id - start_id), 12):  # Échantillonnage
                        distance = abs(i - wave_pos)
                        if distance < 60:  # Rayon de la vague
                            intensity_factor = 1 - (distance / 60)
                            entity_id = start_id + i
                            entities.append(EntityUpdate(
                                entity_id, 
                                int(r * intensity_factor), 
                                int(g * intensity_factor), 
                                int(b * intensity_factor), 
                                0
                            ))
                
                self.router.handle_update(entities)
                if t < 2:  # Log seulement les 2 premières secondes
                    active_controllers = set()
                    for entity in entities[:3]:
                        mapping = self.router.mapper.entity_to_dmx.get(entity.id)
                        if mapping:
                            ctrl_num = self.get_controller_number(mapping['controller_ip'])
                            active_controllers.add(ctrl_num)
                    print(f"[LOG] t={t:.1f}s - {len(entities)} entités - Contrôleurs: {sorted(active_controllers)}")
                
                time.sleep(1/25)
        except Exception as e:
            print(f"[ERREUR] Animation 3 contrôleurs : {e}")

    def full_screen_test_animation(self, duration=15.0):
        """Animation complète testant tous les contrôleurs sur tout l'écran avec des vagues de couleur."""
        print("[ANIMATION] Test complet écran - Tous contrôleurs (15s)")
        print("Balayage progressif : Rouge→Vert→Bleu→Arc-en-ciel sur les 4 contrôleurs")
        
        # Plages d'entités par contrôleur (d'après la config réelle)
        controller_ranges = {
            1: (100, 4858),      # Contrôleur 1: 192.168.1.45
            2: (5100, 9858),     # Contrôleur 2: 192.168.1.46  
            3: (10100, 14858),   # Contrôleur 3: 192.168.1.47
            4: (15100, 19858)    # Contrôleur 4: 192.168.1.48
        }
        
        start_time = time.time()
        try:
            while time.time() - start_time < duration and self.running:
                t = time.time() - start_time
                entities = []
                
                # Phase 1 (0-3s): Balayage séquentiel par contrôleur
                if t < 3.0:
                    current_ctrl = int(t) + 1  # Contrôleur 1, 2, 3
                    if current_ctrl <= 4:
                        start_id, end_id = controller_ranges[current_ctrl]
                        # Vague rouge qui traverse le contrôleur
                        wave_pos = (t % 1.0) * (end_id - start_id)
                        for i in range(0, min(500, end_id - start_id), 10):  # Échantillonnage
                            entity_id = start_id + i
                            distance = abs(i - wave_pos)
                            intensity = max(0, int(255 * (1 - distance / 100)))
                            entities.append(EntityUpdate(entity_id, intensity, 0, 0, 0))
                
                # Phase 2 (3-6s): Balayage vert sur tous les contrôleurs
                elif t < 6.0:
                    phase_t = (t - 3.0) / 3.0
                    for ctrl_num, (start_id, end_id) in controller_ranges.items():
                        wave_pos = phase_t * (end_id - start_id)
                        for i in range(0, min(500, end_id - start_id), 10):
                            entity_id = start_id + i
                            distance = abs(i - wave_pos)
                            intensity = max(0, int(255 * (1 - distance / 150)))
                            entities.append(EntityUpdate(entity_id, 0, intensity, 0, 0))
                
                # Phase 3 (6-9s): Balayage bleu inverse
                elif t < 9.0:
                    phase_t = 1.0 - ((t - 6.0) / 3.0)  # Inverse
                    for ctrl_num, (start_id, end_id) in controller_ranges.items():
                        wave_pos = phase_t * (end_id - start_id)
                        for i in range(0, min(500, end_id - start_id), 10):
                            entity_id = start_id + i
                            distance = abs(i - wave_pos)
                            intensity = max(0, int(255 * (1 - distance / 150)))
                            entities.append(EntityUpdate(entity_id, 0, 0, intensity, 0))
                
                # Phase 4 (9-15s): Arc-en-ciel rotatif sur tous les contrôleurs
                else:
                    rainbow_t = (t - 9.0) * 0.5  # Rotation lente
                    for ctrl_num, (start_id, end_id) in controller_ranges.items():
                        # Couleur différente par contrôleur + rotation temporelle
                        base_hue = (ctrl_num - 1) * 0.25 + rainbow_t
                        for i in range(0, min(300, end_id - start_id), 15):
                            entity_id = start_id + i
                            pos = i / (end_id - start_id)
                            hue = (base_hue + pos * 0.5) % 1.0
                            r, g, b = self.hsv_to_rgb(hue, 1.0, 0.8)
                            entities.append(EntityUpdate(entity_id, r, g, b, 0))
                
                # Envoi des entités et log des contrôleurs actifs
                if entities:
                    self.router.handle_update(entities)
                    active_controllers = set()
                    for entity in entities[:5]:  # Log des 5 premières entités seulement
                        mapping = self.router.mapper.entity_to_dmx.get(entity.id)
                        if mapping:
                            ctrl_num = self.get_controller_number(mapping['controller_ip'])
                            active_controllers.add(ctrl_num)
                    
                    if t < 10:  # Log seulement les 10 premières secondes pour ne pas spammer
                        print(f"[LOG] t={t:.1f}s - {len(entities)} entités - Contrôleurs actifs: {sorted(active_controllers)}")
                
                time.sleep(1/30)  # 30 FPS
                
        except Exception as e:
            print(f"[ERREUR] Animation test complet : {e}")

    def initialize_screen(self):
        """Initialise l'écran en éteignant toutes les LEDs de tous les contrôleurs."""
        print("[INIT] Initialisation de l'écran - Extinction de toutes les LEDs...")
        
        # Plages d'entités de tous les contrôleurs
        all_controller_ranges = [
            (100, 4858),      # Contrôleur 1
            (5100, 9858),     # Contrôleur 2
            (10100, 14858),   # Contrôleur 3
            (15100, 19858)    # Contrôleur 4
        ]
        
        try:
            entities = []
            for start_id, end_id in all_controller_ranges:
                # Échantillonnage pour performance (tous les 50 pixels)
                for entity_id in range(start_id, min(start_id + 500, end_id), 50):
                    entities.append(EntityUpdate(entity_id, 0, 0, 0, 0))  # Noir
            
            if entities:
                self.router.handle_update(entities)
                print(f"[INIT] Écran initialisé - {len(entities)} entités éteintes")
            else:
                print("[INIT] Aucune entité à initialiser")
                
        except Exception as e:
            print(f"[ERREUR] Erreur initialisation écran : {e}")

    def manual_ehub_test(self):
        """Test manuel de messages eHuB avec validation CONFIG et boucle UPDATE."""
        print("\n🧪 === TEST MANUEL DE MESSAGES eHuB ===")
        print("Ce mode permet de tester vos propres messages eHuB tels qu'envoyés par les systèmes externes.")
        print("Formats acceptés: Base64, Hexadécimal, ou Binaire")
        
        # Étape 1: Test du message CONFIG
        print("\n1. TEST DU MESSAGE CONFIG")
        print("Collez votre message CONFIG eHuB:")
        print("Exemples de formats acceptés:")
        print("- Base64: ZUh1QgEAAQAGAB+LCAAyHC...")
        print("- Hexadécimal: 65487542010001000600...")
        print("- Binaire: eHuB\\x01\\x00\\x01\\x00...")
        
        while True:
            config_input = input("Message CONFIG: ").strip()
            if config_input.lower() == 'q':
                return
            
            config_data = self.parse_ehub_input(config_input)
            if config_data and self.validate_config_message_binary(config_data):
                print("✅ Message CONFIG valide et compatible avec l'écran")
                # Appliquer le CONFIG
                self.apply_config_message(config_data)
                break
            else:
                print("❌ Message CONFIG invalide ou incompatible")
                print("\n💡 Voici un exemple de message CONFIG compatible:")
                example_config = self.generate_example_config_readable()
                print(f"CONFIG exemple (Base64): {example_config}")
                
                retry = input("Voulez-vous réessayer? (o/n): ").strip().lower()
                if retry != 'o':
                    return
        
        # Étape 2: Test des messages UPDATE
        print("\n2. TEST DES MESSAGES UPDATE")
        print("Maintenant vous pouvez tester des messages UPDATE.")
        
        while True:
            print("\nOptions:")
            print("- Collez un message UPDATE (Base64, Hex, ou Binaire)")
            print("- Tapez 'exemple' pour voir des exemples")
            print("- Tapez 'q' pour revenir au menu principal")
            
            update_input = input("Message UPDATE: ").strip()
            if update_input.lower() == 'q':
                break
            elif update_input.lower() == 'exemple':
                self.show_update_examples()
                continue
            
            update_data = self.parse_ehub_input(update_input)
            if update_data and self.validate_update_message_binary(update_data):
                # Demander le nombre de répétitions
                try:
                    repeat_count = int(input("Nombre de répétitions (1-100): "))
                    if 1 <= repeat_count <= 100:
                        self.execute_update_message_binary(update_data, repeat_count)
                    else:
                        print("❌ Nombre de répétitions invalide (1-100)")
                except ValueError:
                    print("❌ Veuillez entrer un nombre valide")
            else:
                print("❌ Message UPDATE invalide")
                print("💡 Vérifiez que le message commence par 'eHuB' et est de type UPDATE")

    def parse_ehub_input(self, input_text):
        """Parse une entrée eHuB en différents formats (Base64, Hex, Binaire)."""
        try:
            input_text = input_text.strip()
            
            # Essayer Base64 en premier (format le plus courant)
            if not input_text.startswith('eHuB') and not input_text.startswith('65487542'):
                try:
                    import base64
                    data = base64.b64decode(input_text)
                    if data[:4] == b'eHuB':
                        print(f"[PARSE] Format Base64 détecté")
                        return data
                except:
                    pass
            
            # Essayer Hexadécimal
            if all(c in '0123456789abcdefABCDEF' for c in input_text):
                try:
                    data = bytes.fromhex(input_text)
                    if data[:4] == b'eHuB':
                        print(f"[PARSE] Format Hexadécimal détecté")
                        return data
                except:
                    pass
            
            # Essayer format binaire/string littéral
            if input_text.startswith('eHuB'):
                try:
                    # Traiter les échappements Python
                    data = input_text.encode('latin-1')
                    if data[:4] == b'eHuB':
                        print(f"[PARSE] Format Binaire détecté")
                        return data
                except:
                    pass
            
            # Essayer de décoder les échappements Python
            try:
                data = input_text.encode().decode('unicode_escape').encode('latin-1')
                if data[:4] == b'eHuB':
                    print(f"[PARSE] Format Binaire avec échappements détecté")
                    return data
            except:
                pass
            
            print(f"[ERREUR] Format non reconnu - doit commencer par 'eHuB'")
            return None
            
        except Exception as e:
            print(f"[ERREUR] Parsing entrée: {e}")
            return None

    def validate_config_message_binary(self, data):
        """Valide un message CONFIG eHuB à partir de données binaires."""
        try:
            # Vérifier la signature eHuB
            if data[:4] != b'eHuB':
                return False
                
            # Vérifier le type CONFIG (1)
            if data[4] != 1:
                return False
            
            # Parser le message avec la fonction existante
            from ehub.parser import parse_config_message
            ranges = parse_config_message(data)
            
            # Vérifier la compatibilité avec l'écran
            return self.check_config_compatibility(ranges)
            
        except Exception as e:
            print(f"[ERREUR] Validation CONFIG: {e}")
            return False

    def check_config_compatibility(self, ranges):
        """Vérifie si les plages CONFIG sont compatibles avec l'écran."""
        try:
            # Vérifier que les plages correspondent aux contrôleurs
            expected_ranges = [
                (100, 4858),      # Contrôleur 1
                (5100, 9858),     # Contrôleur 2
                (10100, 14858),   # Contrôleur 3
                (15100, 19858)    # Contrôleur 4
            ]
            
            found_ranges = []
            for r in ranges:
                found_ranges.append((r.entity_start, r.entity_end))
            
            # Vérifier qu'au moins une plage correspond à un contrôleur
            compatible = False
            for start, end in found_ranges:
                for exp_start, exp_end in expected_ranges:
                    if exp_start <= start <= exp_end and exp_start <= end <= exp_end:
                        compatible = True
                        break
                if compatible:
                    break
            
            if compatible:
                print(f"✅ CONFIG compatible: {len(ranges)} plages détectées")
                for r in ranges:
                    print(f"   - Plage: entités {r.entity_start}-{r.entity_end}")
                return True
            else:
                print(f"❌ CONFIG incompatible: plages ne correspondent pas aux contrôleurs")
                return False
                
        except Exception as e:
            print(f"[ERREUR] Vérification compatibilité: {e}")
            return False

    def apply_config_message(self, data):
        """Applique un message CONFIG au système."""
        try:
            from ehub.parser import parse_config_message
            ranges = parse_config_message(data)
            
            # Construire le dictionnaire pour le mapper
            entity_ranges_dict = {r.entity_start: r for r in ranges}
            
            # Appliquer le mapping
            self.router.mapper.build_mapping(entity_ranges_dict)
            
            print(f"✅ CONFIG appliqué: {len(ranges)} plages, {len(self.router.mapper.entity_to_dmx)} entités mappées")
            
        except Exception as e:
            print(f"[ERREUR] Application CONFIG: {e}")

    def generate_example_config_readable(self):
        """Génère un exemple de message CONFIG en format Base64 lisible."""
        try:
            # Utiliser la fonction existante pour générer un CONFIG valide
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
            ]
            
            payload = b''.join([struct.pack('<HHHH', *r) for r in ranges])
            compressed = gzip.compress(payload)
            header = b'eHuB\x01\x00' + struct.pack('<H', len(ranges)) + struct.pack('<H', len(compressed))
            message = header + compressed
            
            import base64
            return base64.b64encode(message).decode('ascii')
            
        except Exception as e:
            print(f"[ERREUR] Génération exemple CONFIG: {e}")
            return ""

    def validate_update_message_binary(self, data):
        """Valide un message UPDATE eHuB à partir de données binaires."""
        try:
            # Vérifier la signature eHuB
            if data[:4] != b'eHuB':
                return False
                
            # Vérifier le type UPDATE (2)
            if data[4] != 2:
                return False
            
            # Parser le message avec la fonction existante
            from ehub.parser import parse_update_message
            entities = parse_update_message(data)
            
            print(f"✅ Message UPDATE valide: {len(entities)} entités")
            return True
            
        except Exception as e:
            print(f"[ERREUR] Validation UPDATE: {e}")
            return False

    def execute_update_message_binary(self, data, repeat_count):
        """Exécute un message UPDATE le nombre de fois spécifié."""
        try:
            print(f"[EXEC] Exécution du message UPDATE {repeat_count} fois...")
            
            # Parser le message
            from ehub.parser import parse_update_message
            entities = parse_update_message(data)
            
            # Initialiser l'écran
            self.initialize_screen()
            time.sleep(0.5)
            
            # Exécuter le message en boucle
            for i in range(repeat_count):
                print(f"[EXEC] Exécution {i+1}/{repeat_count}")
                self.router.handle_update(entities)
                time.sleep(0.1)  # Pause entre les exécutions
            
            print(f"✅ Message exécuté {repeat_count} fois avec succès")
            
        except Exception as e:
            print(f"[ERREUR] Exécution UPDATE: {e}")

    def show_update_examples(self):
        """Affiche des exemples de messages UPDATE en différents formats."""
        print("\n💡 === EXEMPLES DE MESSAGES UPDATE ===")
        
        # Générer des exemples en Base64
        examples = self.generate_update_examples()
        
        print("Format Base64 (recommandé):")
        for name, b64_msg in examples.items():
            print(f"  {name}: {b64_msg}")
        
        print("\nCopiez-collez un de ces exemples pour tester!")

    def generate_update_examples(self):
        """Génère des exemples de messages UPDATE en Base64."""
        examples = {}
        
        try:
            import base64
            
            # Exemple 1: 4 LEDs rouges (une par contrôleur)
            entities = [
                (100, 255, 0, 0, 0),    # Rouge sur contrôleur 1
                (5100, 255, 0, 0, 0),   # Rouge sur contrôleur 2
                (10100, 255, 0, 0, 0),  # Rouge sur contrôleur 3
                (15100, 255, 0, 0, 0),  # Rouge sur contrôleur 4
            ]
            examples["4 LEDs rouges"] = self.create_update_message_b64(entities)
            
            # Exemple 2: Arc-en-ciel
            entities = [
                (100, 255, 0, 0, 0),    # Rouge
                (101, 255, 128, 0, 0),  # Orange
                (102, 255, 255, 0, 0),  # Jaune
                (103, 0, 255, 0, 0),    # Vert
                (104, 0, 0, 255, 0),    # Bleu
                (105, 128, 0, 255, 0),  # Violet
            ]
            examples["Arc-en-ciel"] = self.create_update_message_b64(entities)
            
            # Exemple 3: Blancs
            entities = [
                (100, 255, 255, 255, 0),
                (5100, 255, 255, 255, 0),
                (10100, 255, 255, 255, 0),
                (15100, 255, 255, 255, 0),
            ]
            examples["4 LEDs blanches"] = self.create_update_message_b64(entities)
            
        except Exception as e:
            print(f"[ERREUR] Génération exemples UPDATE: {e}")
        
        return examples

    def create_update_message_b64(self, entities):
        """Crée un message UPDATE en Base64 à partir d'une liste d'entités."""
        try:
            import base64
            
            # Construire le payload
            payload = b''
            for entity_id, r, g, b, w in entities:
                payload += struct.pack('<HBBBB', entity_id, r, g, b, w)
            
            # Compresser
            compressed = gzip.compress(payload)
            
            # Construire le header
            header = b'eHuB\x02\x00' + struct.pack('<H', len(entities)) + struct.pack('<H', len(compressed))
            message = header + compressed
            
            return base64.b64encode(message).decode('ascii')
            
        except Exception as e:
            print(f"[ERREUR] Création message UPDATE: {e}")
            return ""

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