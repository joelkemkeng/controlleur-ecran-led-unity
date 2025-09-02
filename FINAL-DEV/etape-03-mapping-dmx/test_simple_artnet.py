#!/usr/bin/env python3
"""
🎮 Test ArtNet Simple - Tests rapides pour vérifier l'écran
"""

import socket
import time
import sys

def send_solid_color(r, g, b, duration=2.0):
    """Envoie une couleur unie vers l'écran LED"""
    print(f"🎨 Envoi couleur RGB({r},{g},{b}) pendant {duration}s...")
    
    # Socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Contrôleurs BC216
    controllers = [
        ('192.168.1.45', 6454),
        ('192.168.1.46', 6454), 
        ('192.168.1.47', 6454),
        ('192.168.1.48', 6454),
    ]
    
    # Frame 128x128 RGB
    frame = bytearray(128 * 128 * 3)
    for i in range(0, len(frame), 3):
        frame[i] = r      # Rouge
        frame[i + 1] = g  # Vert  
        frame[i + 2] = b  # Bleu
    
    start_time = time.time()
    packets_sent = 0
    
    while time.time() - start_time < duration:
        # Envoyer vers tous les contrôleurs
        for ctrl_idx, (ip, port) in enumerate(controllers):
            base_universe = ctrl_idx * 32
            
            # 32 univers par contrôleur
            for universe_offset in range(32):
                universe = base_universe + universe_offset
                
                # Header ArtNet
                packet = bytearray([
                    ord('A'), ord('r'), ord('t'), ord('-'),
                    ord('N'), ord('e'), ord('t'), 0,  # "Art-Net\0"
                    0x00, 0x50,  # OpCode
                    0, 14,       # Version
                    0, 0,        # Sequence, Physical
                    universe & 0xFF, (universe >> 8) & 0xFF,  # Universe
                    0x02, 0x00,  # Length (512)
                ])
                
                # Données DMX (512 bytes)
                dmx_data = bytearray(512)
                
                # Remplir avec la couleur (170 LEDs × 3 canaux = 510 canaux)
                for led in range(170):
                    if led * 3 + 2 < 512:
                        dmx_data[led * 3] = r      # R
                        dmx_data[led * 3 + 1] = g  # G
                        dmx_data[led * 3 + 2] = b  # B
                
                packet.extend(dmx_data)
                
                # Envoyer
                try:
                    sock.sendto(packet, (ip, port))
                    packets_sent += 1
                except Exception as e:
                    print(f"❌ Erreur {ip}: {e}")
        
        time.sleep(0.05)  # 20 FPS
    
    sock.close()
    print(f"✅ {packets_sent} paquets envoyés")

def main():
    """Tests rapides"""
    print("🚀 === TESTS ARTNET RAPIDES ===")
    
    try:
        # Test basiques
        send_solid_color(0, 0, 0, 1.0)      # Noir
        time.sleep(0.5)
        send_solid_color(255, 0, 0, 2.0)    # Rouge
        time.sleep(0.5)
        send_solid_color(0, 255, 0, 2.0)    # Vert
        time.sleep(0.5)
        send_solid_color(0, 0, 255, 2.0)    # Bleu
        time.sleep(0.5)
        send_solid_color(255, 255, 255, 2.0) # Blanc
        time.sleep(0.5)
        send_solid_color(0, 0, 0, 1.0)      # Éteindre
        
        print("🎉 Tests terminés !")
        
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé")
        send_solid_color(0, 0, 0, 0.5)  # Éteindre

if __name__ == "__main__":
    main()
