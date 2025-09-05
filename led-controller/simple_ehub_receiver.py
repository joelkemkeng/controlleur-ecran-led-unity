#!/usr/bin/env python3
"""
Récepteur eHub ultra-simple
Version minimaliste pour debug rapide
"""

import socket
import time
from datetime import datetime
from core.ehub import get_entities_list

def simple_monitor(port=8765):
    """Monitoring eHub ultra-simple"""
    print(f"🎧 Écoute eHub sur port {port}")
    print("Appuyez sur Ctrl+C pour arrêter\n")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", port))
    
    packet_count = 0
    
    try:
        while True:
            data, addr = sock.recvfrom(64*1024)
            packet_count += 1
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            try:
                entities = get_entities_list(data)
                print(f"[{timestamp}] Paquet #{packet_count}: {len(entities)} entités ({len(data)} bytes) de {addr[0]}")
                
                # Afficher les 3 premières entités
                for i, entity in enumerate(entities[:3]):
                    entity_id, r, g, b, w = entity
                    print(f"   #{entity_id}: R{r:3d} G{g:3d} B{b:3d}")
                
                if len(entities) > 3:
                    print(f"   ... et {len(entities)-3} autres")
                print()
                    
            except Exception as e:
                print(f"[{timestamp}] Erreur décodage paquet #{packet_count}: {e}")
                
    except KeyboardInterrupt:
        print(f"\n✅ Arrêté après {packet_count} paquets")
    finally:
        sock.close()

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    simple_monitor(port)
