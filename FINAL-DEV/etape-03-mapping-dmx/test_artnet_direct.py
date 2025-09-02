#!/usr/bin/env python3
"""
🎭 Test ArtNet Direct - Envoi de données vers écran LED réel
Script de test pour vérifier la communication avec les contrôleurs BC216
Base sur le code Windows fonctionnel, adapté pour WSL Ubuntu
"""

import socket
import time
import sys
from enum import Enum
from typing import List, Tuple

class LedMode(Enum):
    SIMULATOR = "simulator"
    PRODUCTION = "production"

class ArtNetTester:
    def __init__(self, mode: LedMode = LedMode.PRODUCTION):
        """Initialise le testeur ArtNet"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', 0))
        self.mode = mode
        
        # Adresses des contrôleurs LED BC216
        if mode == LedMode.SIMULATOR:
            print("🔧 Mode SIMULATEUR activé")
            self.controllers = [
                ('127.0.0.1', 6454),
                ('127.0.0.1', 6454),
                ('127.0.0.1', 6454),
                ('127.0.0.1', 6454),
            ]
        else:
            print("🎮 Mode PRODUCTION activé - Contrôleurs BC216")
            self.controllers = [
                ('192.168.1.45', 6454),
                ('192.168.1.46', 6454),
                ('192.168.1.47', 6454),
                ('192.168.1.48', 6454),
            ]
        
        print(f"📡 Contrôleurs configurés:")
        for i, (ip, port) in enumerate(self.controllers):
            print(f"   • Contrôleur {i+1}: {ip}:{port}")
    
    def create_artnet_packet(self, universe: int, dmx_data: bytes) -> bytearray:
        """Crée un paquet ArtNet standard"""
        # Header ArtNet (18 bytes)
        packet = bytearray([
            ord('A'), ord('r'), ord('t'), ord('-'),
            ord('N'), ord('e'), ord('t'), 0,  # ID "Art-Net\0"
            0x00, 0x50,  # OpCode (OpOutput) - little endian
            0, 14,  # Protocol version - big endian
            0,  # Sequence
            0,  # Physical
            universe & 0xFF,
            (universe >> 8) & 0xFF,  # Universe - little endian
            0x02, 0x00,  # Length (512) - big endian
        ])
        
        # Données DMX (512 bytes)
        dmx_buffer = bytearray(512)
        if dmx_data:
            copy_len = min(len(dmx_data), 512)
            dmx_buffer[:copy_len] = dmx_data[:copy_len]
        
        packet.extend(dmx_buffer)
        return packet
    
    def send_test_frame(self, frame_data: bytes):
        """Envoie une frame test vers l'écran LED"""
        packets_sent = 0
        
        print(f"📤 Envoi frame ({len(frame_data)} bytes)...")
        
        # Envoi vers les 4 contrôleurs BC216
        for quarter in range(4):
            controller_addr = self.controllers[quarter]
            base_universe = quarter * 32  # 32 univers par contrôleur
            
            # 16 bandes par contrôleur, 2 univers par bande
            for band_in_quarter in range(16):
                for uni_in_band in range(2):
                    universe = base_universe + band_in_quarter * 2 + uni_in_band
                    
                    # Créer données DMX pour cet univers
                    dmx_data = self._create_dmx_for_universe(frame_data, quarter, band_in_quarter, uni_in_band)
                    
                    # Créer et envoyer paquet ArtNet
                    packet = self.create_artnet_packet(universe, dmx_data)
                    
                    try:
                        self.socket.sendto(packet, controller_addr)
                        packets_sent += 1
                    except Exception as e:
                        print(f"❌ Erreur envoi {controller_addr} u{universe}: {e}")
        
        print(f"✅ {packets_sent} paquets ArtNet envoyés")
        return packets_sent
    
    def _create_dmx_for_universe(self, frame_data: bytes, quarter: int, band: int, uni_in_band: int) -> bytes:
        """Crée les données DMX pour un univers spécifique"""
        dmx_data = bytearray(512)
        
        # Calcul des colonnes virtuelles
        physical_band = quarter * 16 + band
        col_up = physical_band * 2
        col_down = physical_band * 2 + 1
        
        # Vérifier limites
        if col_up >= 128 or col_down >= 128:
            return bytes(dmx_data)
        
        dmx_offset = 0
        
        if uni_in_band == 0:
            # Premier univers: 170 LEDs (510 canaux DMX)
            # Partie montante: 130 LEDs
            for led in range(130):
                if dmx_offset + 2 < 510:
                    y = max(0, 127 - (led * 128 // 130))
                    pixel_idx = (y * 128 + col_up) * 3
                    
                    if pixel_idx + 2 < len(frame_data):
                        dmx_data[dmx_offset] = frame_data[pixel_idx]      # R
                        dmx_data[dmx_offset + 1] = frame_data[pixel_idx + 1]  # G
                        dmx_data[dmx_offset + 2] = frame_data[pixel_idx + 2]  # B
                    dmx_offset += 3
            
            # Début partie descendante: 40 LEDs
            for led in range(40):
                if dmx_offset + 2 < 510:
                    y = min(127, led * 128 // 129)
                    pixel_idx = (y * 128 + col_down) * 3
                    
                    if pixel_idx + 2 < len(frame_data):
                        dmx_data[dmx_offset] = frame_data[pixel_idx]
                        dmx_data[dmx_offset + 1] = frame_data[pixel_idx + 1]
                        dmx_data[dmx_offset + 2] = frame_data[pixel_idx + 2]
                    dmx_offset += 3
        else:
            # Deuxième univers: 89 LEDs (267 canaux DMX)
            for led in range(40, 129):
                if dmx_offset + 2 < 267:
                    y = min(127, led * 128 // 129)
                    pixel_idx = (y * 128 + col_down) * 3
                    
                    if pixel_idx + 2 < len(frame_data):
                        dmx_data[dmx_offset] = frame_data[pixel_idx]
                        dmx_data[dmx_offset + 1] = frame_data[pixel_idx + 1]
                        dmx_data[dmx_offset + 2] = frame_data[pixel_idx + 2]
                    dmx_offset += 3
        
        return bytes(dmx_data)
    
    def test_solid_color(self, r: int, g: int, b: int, duration: float = 2.0):
        """Test couleur unie sur tout l'écran"""
        print(f"🎨 Test couleur unie: RGB({r},{g},{b}) pendant {duration}s")
        
        # Créer frame 128x128 RGB
        frame = bytearray(128 * 128 * 3)
        for i in range(0, len(frame), 3):
            frame[i] = r      # Rouge
            frame[i + 1] = g  # Vert
            frame[i + 2] = b  # Bleu
        
        start_time = time.time()
        packets_count = 0
        
        while time.time() - start_time < duration:
            packets_count += self.send_test_frame(frame)
            time.sleep(0.05)  # 20 FPS
        
        print(f"📊 Total: {packets_count} paquets en {duration}s")
    
    def test_gradient_horizontal(self, duration: float = 3.0):
        """Test dégradé horizontal rouge → vert → bleu"""
        print(f"🌈 Test dégradé horizontal pendant {duration}s")
        
        frame = bytearray(128 * 128 * 3)
        
        for y in range(128):
            for x in range(128):
                pixel_idx = (y * 128 + x) * 3
                
                # Dégradé horizontal
                if x < 43:  # Premier tiers: rouge
                    intensity = int((x / 42) * 255)
                    frame[pixel_idx] = intensity
                    frame[pixel_idx + 1] = 0
                    frame[pixel_idx + 2] = 0
                elif x < 86:  # Deuxième tiers: vert
                    intensity = int(((x - 43) / 42) * 255)
                    frame[pixel_idx] = 0
                    frame[pixel_idx + 1] = intensity
                    frame[pixel_idx + 2] = 0
                else:  # Dernier tiers: bleu
                    intensity = int(((x - 86) / 41) * 255)
                    frame[pixel_idx] = 0
                    frame[pixel_idx + 1] = 0
                    frame[pixel_idx + 2] = intensity
        
        start_time = time.time()
        while time.time() - start_time < duration:
            self.send_test_frame(frame)
            time.sleep(0.05)
    
    def test_moving_square(self, duration: float = 5.0):
        """Test carré qui se déplace"""
        print(f"📦 Test carré mobile pendant {duration}s")
        
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < duration:
            frame = bytearray(128 * 128 * 3)
            
            # Position du carré (animation circulaire)
            t = (time.time() - start_time) / duration * 2 * 3.14159
            center_x = int(64 + 40 * time.cos(t))
            center_y = int(64 + 40 * time.sin(t))
            
            # Dessiner carré 20x20
            for dy in range(-10, 11):
                for dx in range(-10, 11):
                    x = center_x + dx
                    y = center_y + dy
                    
                    if 0 <= x < 128 and 0 <= y < 128:
                        pixel_idx = (y * 128 + x) * 3
                        frame[pixel_idx] = 255      # Rouge
                        frame[pixel_idx + 1] = 255  # Vert  
                        frame[pixel_idx + 2] = 0    # Bleu = 0 → Jaune
            
            self.send_test_frame(frame)
            frame_count += 1
            time.sleep(0.033)  # ~30 FPS
        
        print(f"📊 {frame_count} frames envoyées")
    
    def test_sequence_complete(self):
        """Lance une séquence de tests complète"""
        print("🚀 === SÉQUENCE DE TESTS ARTNET COMPLÈTE ===")
        print()
        
        try:
            # Test 1: Noir (éteindre)
            print("🔴 Test 1: Écran noir")
            self.test_solid_color(0, 0, 0, 1.0)
            time.sleep(0.5)
            
            # Test 2: Rouge
            print("🔴 Test 2: Rouge pur")
            self.test_solid_color(255, 0, 0, 2.0)
            time.sleep(0.5)
            
            # Test 3: Vert
            print("🟢 Test 3: Vert pur")
            self.test_solid_color(0, 255, 0, 2.0)
            time.sleep(0.5)
            
            # Test 4: Bleu
            print("🔵 Test 4: Bleu pur")
            self.test_solid_color(0, 0, 255, 2.0)
            time.sleep(0.5)
            
            # Test 5: Blanc
            print("⚪ Test 5: Blanc pur")
            self.test_solid_color(255, 255, 255, 2.0)
            time.sleep(0.5)
            
            # Test 6: Dégradé
            print("🌈 Test 6: Dégradé horizontal")
            self.test_gradient_horizontal(3.0)
            time.sleep(0.5)
            
            # Test 7: Animation
            print("📦 Test 7: Carré mobile")
            self.test_moving_square(5.0)
            time.sleep(0.5)
            
            # Test 8: Éteindre
            print("⚫ Test 8: Extinction")
            self.test_solid_color(0, 0, 0, 1.0)
            
            print()
            print("🎉 Séquence de tests terminée !")
            
        except KeyboardInterrupt:
            print("\n🛑 Tests interrompus par l'utilisateur")
            self.test_solid_color(0, 0, 0, 0.5)  # Éteindre
        except Exception as e:
            print(f"\n❌ Erreur durant les tests: {e}")
            self.test_solid_color(0, 0, 0, 0.5)  # Éteindre
    
    def close(self):
        """Ferme le socket"""
        if self.socket:
            self.socket.close()

def main():
    """Programme principal"""
    print("🎭 === TESTEUR ARTNET POUR ÉCRAN LED ===")
    print("📡 Adaptation du code Windows pour WSL Ubuntu")
    print()
    
    # Créer testeur en mode production (BC216)
    tester = ArtNetTester(LedMode.PRODUCTION)
    
    try:
        # Lancer séquence complète
        tester.test_sequence_complete()
        
    finally:
        tester.close()
        print("🔌 Socket fermé")

if __name__ == "__main__":
    main()
