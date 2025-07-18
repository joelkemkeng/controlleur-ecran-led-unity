#!/usr/bin/env python3
"""
generate_ehub_examples.py - Générateur d'exemples de messages eHuB pour les tests

Ce script génère des exemples de messages eHuB CONFIG et UPDATE
que vous pouvez utiliser dans l'option 8 de demo/animation_demo.py
"""

import struct
import gzip
import sys
import os

def generate_config_message():
    """Génère un message CONFIG eHuB d'exemple."""
    print("🔧 Génération du message CONFIG...")
    
    # Plages basées sur la vraie configuration de l'écran
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
    
    # Construire le message CONFIG
    payload = b''.join([struct.pack('<HHHH', *r) for r in ranges])
    compressed = gzip.compress(payload)
    header = b'eHuB\x01\x00' + struct.pack('<H', len(ranges)) + struct.pack('<H', len(compressed))
    message = header + compressed
    
    hex_message = message.hex()
    print(f"✅ Message CONFIG généré ({len(hex_message)} caractères)")
    print(f"   - {len(ranges)} plages définies")
    print(f"   - Taille compressée: {len(compressed)} bytes")
    
    return hex_message

def generate_update_message(pattern="rouge"):
    """Génère un message UPDATE eHuB d'exemple."""
    print(f"🎨 Génération du message UPDATE ({pattern})...")
    
    entities = []
    
    if pattern == "rouge":
        # Quelques LEDs rouges sur différents contrôleurs
        test_entities = [
            (100, 255, 0, 0, 0),    # Rouge sur contrôleur 1
            (5100, 255, 0, 0, 0),   # Rouge sur contrôleur 2
            (10100, 255, 0, 0, 0),  # Rouge sur contrôleur 3
            (15100, 255, 0, 0, 0),  # Rouge sur contrôleur 4
        ]
        entities.extend(test_entities)
        
    elif pattern == "arc-en-ciel":
        # Arc-en-ciel sur les premiers contrôleurs
        colors = [
            (255, 0, 0, 0),    # Rouge
            (255, 128, 0, 0),  # Orange
            (255, 255, 0, 0),  # Jaune
            (0, 255, 0, 0),    # Vert
            (0, 0, 255, 0),    # Bleu
            (128, 0, 255, 0),  # Violet
        ]
        
        for i, (r, g, b, w) in enumerate(colors):
            entities.append((100 + i, r, g, b, w))  # Contrôleur 1
            entities.append((5100 + i, r, g, b, w)) # Contrôleur 2
            
    elif pattern == "blanc":
        # Blanc sur tous les contrôleurs
        test_entities = [
            (100, 255, 255, 255, 0),
            (5100, 255, 255, 255, 0),
            (10100, 255, 255, 255, 0),
            (15100, 255, 255, 255, 0),
        ]
        entities.extend(test_entities)
    
    # Construire le payload
    payload = b''
    for entity_id, r, g, b, w in entities:
        payload += struct.pack('<HBBBB', entity_id, r, g, b, w)
    
    # Compresser
    compressed = gzip.compress(payload)
    
    # Construire le header
    header = b'eHuB\x02\x00' + struct.pack('<H', len(entities)) + struct.pack('<H', len(compressed))
    message = header + compressed
    
    hex_message = message.hex()
    print(f"✅ Message UPDATE généré ({len(hex_message)} caractères)")
    print(f"   - {len(entities)} entités définies")
    print(f"   - Taille compressée: {len(compressed)} bytes")
    
    return hex_message

def main():
    """Fonction principale - génère des exemples de messages eHuB."""
    print("🧪 === GÉNÉRATEUR D'EXEMPLES eHuB ===")
    print("Ce script génère des messages eHuB que vous pouvez utiliser")
    print("dans l'option 8 de demo/animation_demo.py")
    print()
    
    # Générer message CONFIG
    print("1. MESSAGE CONFIG")
    config_hex = generate_config_message()
    print(f"CONFIG: {config_hex[:100]}...")
    print()
    
    # Générer messages UPDATE
    print("2. MESSAGES UPDATE")
    
    patterns = ["rouge", "arc-en-ciel", "blanc"]
    update_messages = {}
    
    for pattern in patterns:
        update_hex = generate_update_message(pattern)
        update_messages[pattern] = update_hex
        print(f"UPDATE {pattern}: {update_hex[:100]}...")
        print()
    
    # Sauvegarder dans un fichier
    print("3. SAUVEGARDE")
    with open("ehub_examples.txt", "w") as f:
        f.write("=== EXEMPLES DE MESSAGES eHuB ===\n\n")
        
        f.write("CONFIG (Compatible avec l'écran complet):\n")
        f.write(f"{config_hex}\n\n")
        
        f.write("UPDATE Messages:\n")
        for pattern, hex_msg in update_messages.items():
            f.write(f"\n{pattern.upper()}:\n")
            f.write(f"{hex_msg}\n")
    
    print("✅ Exemples sauvegardés dans 'ehub_examples.txt'")
    print()
    
    # Instructions d'utilisation
    print("📋 INSTRUCTIONS D'UTILISATION:")
    print("1. Lancez: python demo/animation_demo.py")
    print("2. Choisissez l'option 8 (Test messages eHuB manuel)")
    print("3. Collez le message CONFIG ci-dessus")
    print("4. Collez un des messages UPDATE ci-dessus")
    print("5. Spécifiez le nombre de répétitions (ex: 5)")
    print()
    
    print("💡 CONSEILS:")
    print("- Le message CONFIG doit être validé avant les UPDATE")
    print("- Vous pouvez modifier les entités dans le code pour créer vos propres patterns")
    print("- Les messages sont générés selon le format eHuB officiel")
    print()
    
    print("🎯 Messages prêts à utiliser!")

if __name__ == "__main__":
    main()