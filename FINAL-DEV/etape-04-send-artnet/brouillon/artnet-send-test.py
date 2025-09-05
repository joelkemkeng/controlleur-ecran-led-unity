import socket
from enum import Enum
from typing import List, Optional


class LedMode(Enum):
    SIMULATOR = "simulator"
    PRODUCTION = "production"


class LedController:
    def __init__(self, mode: LedMode = LedMode.SIMULATOR):
        """Initialize LED controller with specified mode."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', 0))
        self.mode = mode
        
        # Adresses des contrôleurs LED
        if mode == LedMode.SIMULATOR:
            self.controllers = [
                ('127.0.0.1', 6454),
                ('127.0.0.1', 6454),
                ('127.0.0.1', 6454),
                ('127.0.0.1', 6454),
            ]
        else:  # Production
            self.controllers = [
                ('192.168.1.45', 6454),
                ('192.168.1.46', 6454),
                ('192.168.1.47', 6454),
                ('192.168.1.48', 6454),
            ]
    
    @classmethod
    def new(cls):
        """Create new LED controller with default simulator mode."""
        return cls(LedMode.SIMULATOR)
    
    @classmethod
    def new_with_mode(cls, mode: LedMode):
        """Create new LED controller with specified mode."""
        return cls(mode)
    
    def send_frame(self, frame: bytes):
        """Send frame data to LED controllers."""
        # Calculer la luminosité moyenne pour vérifier si on envoie bien des données
        if len(frame) > 0:
            avg_brightness = sum(frame) / len(frame)
            if avg_brightness > 1.0:
                print(f"📡 Sending frame - avg brightness: {avg_brightness:.1f}")
        
        if self.mode == LedMode.SIMULATOR:
            self._send_frame_simulator(frame)
        else:
            self._send_frame_production(frame)
    
    def _send_frame_simulator(self, frame: bytes):
        """Send frame to simulator (256 universes, 2 per column, 128 columns)."""
        universe = 0
        
        # Pour chaque colonne de l'écran LED
        for col in range(128):
            # Chaque colonne utilise 2 univers (128 pixels / 170 pixels par univers)
            for uni_in_col in range(2):
                artnet_packet = bytearray([
                    ord('A'), ord('r'), ord('t'), ord('-'),
                    ord('N'), ord('e'), ord('t'), 0,  # ID
                    0x00, 0x50,  # OpCode (OpOutput)
                    0, 14,  # Protocol version
                    0,  # Sequence
                    0,  # Physical
                    universe & 0xFF,
                    (universe >> 8) & 0xFF,  # Universe
                    0x02, 0x00,  # Length (512)
                ])
                
                dmx_data = bytearray(512)
                
                # Mapping serpentin : colonnes paires montent, colonnes impaires descendent
                if col % 2 == 0:
                    # Colonnes paires : du bas vers le haut
                    start_pixel = uni_in_col * 64
                    end_pixel = min((uni_in_col + 1) * 64, 128)
                    
                    for pixel in range(start_pixel, end_pixel):
                        led_idx = pixel - start_pixel
                        y = 127 - pixel  # Inverser pour monter
                        pixel_idx = (y * 128 + col) * 3
                        
                        if pixel_idx + 2 < len(frame) and led_idx * 3 + 2 < 512:
                            dmx_data[led_idx * 3] = frame[pixel_idx]  # R
                            dmx_data[led_idx * 3 + 1] = frame[pixel_idx + 1]  # G
                            dmx_data[led_idx * 3 + 2] = frame[pixel_idx + 2]  # B
                else:
                    # Colonnes impaires : du haut vers le bas
                    start_pixel = uni_in_col * 64
                    end_pixel = min((uni_in_col + 1) * 64, 128)
                    
                    for pixel in range(start_pixel, end_pixel):
                        led_idx = pixel - start_pixel
                        y = pixel  # Normal pour descendre
                        pixel_idx = (y * 128 + col) * 3
                        
                        if pixel_idx + 2 < len(frame) and led_idx * 3 + 2 < 512:
                            dmx_data[led_idx * 3] = frame[pixel_idx]  # R
                            dmx_data[led_idx * 3 + 1] = frame[pixel_idx + 1]  # G
                            dmx_data[led_idx * 3 + 2] = frame[pixel_idx + 2]  # B
                
                artnet_packet.extend(dmx_data)
                
                # Envoyer le paquet
                try:
                    self.socket.sendto(artnet_packet, ('127.0.0.1', 6454))
                except Exception:
                    pass  # Ignorer les erreurs d'envoi
                
                universe += 1
    
    def _send_frame_production(self, frame: bytes):
        """Send frame to production LED screen."""
        # L'écran physique a 64 bandes de 259 LEDs chacune
        # Chaque bande monte puis redescend, formant 2 colonnes
        # Donc 64 bandes = 128 colonnes au total
        # Organisées en 4 contrôleurs de 16 bandes chacun
        
        packets_sent = 0
        
        for quarter in range(4):
            controller_addr = self.controllers[quarter]
            base_universe = quarter * 32
            
            # Chaque quartier a 16 bandes physiques
            for band_in_quarter in range(16):
                physical_band = quarter * 16 + band_in_quarter
                
                # Colonnes correspondantes dans l'écran virtuel
                col_up = physical_band * 2  # Colonne montante
                col_down = physical_band * 2 + 1  # Colonne descendante
                
                # Chaque bande physique utilise 2 univers (259 LEDs / 170 par univers)
                for uni_in_band in range(2):
                    universe = base_universe + band_in_quarter * 2 + uni_in_band
                    artnet_packet = self._create_artnet_header(universe)
                    dmx_data = bytearray(512)
                    
                    # Mapper les pixels de l'écran vers les LEDs physiques
                    self._map_pixels_to_band(dmx_data, frame, col_up, col_down, uni_in_band)
                    
                    artnet_packet.extend(dmx_data)
                    try:
                        self.socket.sendto(artnet_packet, controller_addr)
                        packets_sent += 1
                    except Exception as e:
                        print(f"❌ Error sending to {controller_addr}: {e}")
        
        if packets_sent > 0 and packets_sent % 64 == 0:
            print(f"✅ Sent {packets_sent} ArtNet packets")
    
    def _create_artnet_header(self, universe: int) -> bytearray:
        """Create ArtNet packet header."""
        return bytearray([
            ord('A'), ord('r'), ord('t'), ord('-'),
            ord('N'), ord('e'), ord('t'), 0,  # ID
            0x00, 0x50,  # OpCode (OpOutput)
            0, 14,  # Protocol version
            0,  # Sequence
            0,  # Physical
            universe & 0xFF,
            (universe >> 8) & 0xFF,  # Universe
            0x02, 0x00,  # Length (512)
        ])
    
    def _map_pixels_to_band(self, dmx_data: bytearray, frame: bytes, 
                            col_up: int, col_down: int, uni_in_band: int):
        """Map pixels from frame to physical LED band."""
        # Une bande physique de 259 LEDs fait un U inversé :
        # - Monte sur 130 LEDs (col_up)
        # - Redescend sur 129 LEDs (col_down)
        
        # Vérifier que les colonnes sont dans les limites
        if col_up >= 128 or col_down >= 128:
            print(f"⚠️  Column out of bounds: col_up={col_up}, col_down={col_down}")
            return
        
        if uni_in_band == 0:
            # Premier univers: LEDs 0-169 (170 LEDs)
            dmx_offset = 0
            
            # Partie montante : LEDs 0-129 (130 LEDs)
            for led in range(130):
                if dmx_offset + 2 < 510:  # 170 * 3 = 510
                    # La LED physique 0 est en bas, on monte vers le haut
                    y = 127 - (led * 128 // 130)  # Répartir 130 LEDs sur 128 pixels
                    y = min(y, 127)  # S'assurer qu'on ne dépasse pas
                    
                    pixel_idx = (y * 128 + col_up) * 3
                    if pixel_idx + 2 < len(frame):
                        dmx_data[dmx_offset] = frame[pixel_idx]
                        dmx_data[dmx_offset + 1] = frame[pixel_idx + 1]
                        dmx_data[dmx_offset + 2] = frame[pixel_idx + 2]
                    dmx_offset += 3
            
            # Début de la partie descendante : LEDs 130-169 (40 LEDs)
            for led in range(40):
                if dmx_offset + 2 < 510:
                    # On redescend depuis le haut
                    y = led * 128 // 129  # Répartir 129 LEDs sur 128 pixels
                    y = min(y, 127)
                    
                    pixel_idx = (y * 128 + col_down) * 3
                    if pixel_idx + 2 < len(frame):
                        dmx_data[dmx_offset] = frame[pixel_idx]
                        dmx_data[dmx_offset + 1] = frame[pixel_idx + 1]
                        dmx_data[dmx_offset + 2] = frame[pixel_idx + 2]
                    dmx_offset += 3
        else:
            # Deuxième univers: LEDs 170-258 (89 LEDs)
            dmx_offset = 0
            
            # Suite de la partie descendante : LEDs 170-258 (89 LEDs)
            for led in range(40, 129):
                if dmx_offset + 2 < 267:  # 89 * 3 = 267
                    y = led * 128 // 129
                    y = min(y, 127)
                    
                    pixel_idx = (y * 128 + col_down) * 3
                    if pixel_idx + 2 < len(frame):
                        dmx_data[dmx_offset] = frame[pixel_idx]
                        dmx_data[dmx_offset + 1] = frame[pixel_idx + 1]
                        dmx_data[dmx_offset + 2] = frame[pixel_idx + 2]
                    dmx_offset += 3


# Exemple d'utilisation
if __name__ == "__main__":
    # Créer un contrôleur en mode simulateur
    controller = LedController.new()
    
    # Ou en mode production
    # controller = LedController.new_with_mode(LedMode.PRODUCTION)
    
    # Créer une frame de test (128x128 pixels RGB)
    frame = bytearray(128 * 128 * 3)
    
    # Remplir avec des données de test (par exemple, tout en rouge)
    for i in range(0, len(frame), 3):
        frame[i] = 255  # R
        frame[i + 1] = 0  # G
        frame[i + 2] = 0  # B
    
    # Envoyer la frame
    controller.send_frame(frame)