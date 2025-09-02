#!/usr/bin/env python3
"""
🎮 Simulateur Unity pour test pipeline Étape 3
Envoie des messages eHuB vers le pipeline complet
"""

import socket
import time
import gzip
import struct
import sys

def create_test_ehub_message():
    """
    Crée un message eHuB de test avec entités LED
    """
    # Entités test (format: entity_id [2 bytes], r, g, b, w [1 byte chacun])
    entities_data = b''
    
    # Entité 100: LED rouge
    entities_data += struct.pack('<H', 100)  # entity_id (little-endian)
    entities_data += bytes([255, 0, 0, 0])   # R=255, G=0, B=0, W=0
    
    # Entité 101: LED verte  
    entities_data += struct.pack('<H', 101)
    entities_data += bytes([0, 255, 0, 0])   # R=0, G=255, B=0, W=0
    
    # Entité 4000: LED bleue (contrôleur 2)
    entities_data += struct.pack('<H', 4000)
    entities_data += bytes([0, 0, 255, 0])   # R=0, G=0, B=255, W=0
    
    # Entité 8000: LED jaune (contrôleur 3)
    entities_data += struct.pack('<H', 8000) 
    entities_data += bytes([255, 255, 0, 0]) # R=255, G=255, B=0, W=0
    
    # Entité 12000: LED magenta (contrôleur 4)
    entities_data += struct.pack('<H', 12000)
    entities_data += bytes([255, 0, 255, 0]) # R=255, G=0, B=255, W=0
    
    # Compresser les données
    compressed_data = gzip.compress(entities_data)
    
    # Construire header eHuB (10 bytes)
    header = b'eHuB'                                    # Signature (4 bytes)
    header += struct.pack('B', 2)                       # packet_type: 2=update (1 byte)
    header += struct.pack('B', 1)                       # universe (1 byte)
    header += struct.pack('<H', 5)                      # entity_count (2 bytes, little-endian) 
    header += struct.pack('<H', len(compressed_data))   # payload_size (2 bytes, little-endian)
    
    # Message complet
    message = header + compressed_data
    
    print(f"📦 Message eHuB créé:")
    print(f"   🏷️  Signature: {header[0:4]}")
    print(f"   📝 Type: {header[4]} (update)")
    print(f"   🌍 Univers: {header[5]}")
    print(f"   🔢 Entités: {struct.unpack('<H', header[6:8])[0]}")
    print(f"   📦 Payload: {len(compressed_data)} bytes")
    print(f"   📏 Total: {len(message)} bytes")
    print(f"   🎨 Entités test: 100(rouge), 101(vert), 4000(bleu), 8000(jaune), 12000(magenta)")
    
    return message

def send_to_pipeline(message, target_ip='172.26.223.135', target_port=8765):
    """
    Envoie le message vers le pipeline eHub
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        print(f"📤 Envoi vers {target_ip}:{target_port}")
        sock.sendto(message, (target_ip, target_port))
        sock.close()
        
        print(f"✅ Message envoyé ({len(message)} bytes)")
        return True
        
    except Exception as e:
        print(f"❌ Erreur envoi: {e}")
        return False

def main():
    """
    Lance le simulateur Unity
    """
    print("🎮 === SIMULATEUR UNITY - TEST ÉTAPE 3 ===")
    print()
    
    # Créer message test
    print("🔧 Création du message eHuB de test...")
    message = create_test_ehub_message()
    print()
    
    # Envoyer vers le pipeline
    print("📡 Envoi vers le pipeline eHub→ArtNet...")
    success = send_to_pipeline(message)
    
    if success:
        print()
        print("🎉 Test réussi !")
        print("💡 Vérifiez les logs du pipeline pour voir:")
        print("   📨 Réception du message eHuB") 
        print("   🔬 Décodage des 5 entités")
        print("   🎭 Génération des paquets ArtNet")
        print("   📤 Envoi vers les contrôleurs BC216")
        print()
        print("🎨 Entités envoyées:")
        print("   • Entité 100: Rouge → 192.168.1.45:u0")
        print("   • Entité 101: Vert → 192.168.1.45:u0") 
        print("   • Entité 4000: Bleu → 192.168.1.46:u*")
        print("   • Entité 8000: Jaune → 192.168.1.47:u*")
        print("   • Entité 12000: Magenta → 192.168.1.48:u*")
    else:
        print("❌ Échec du test")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
