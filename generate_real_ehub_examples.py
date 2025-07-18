#!/usr/bin/env python3
"""
generate_real_ehub_examples.py - Générateur d'exemples de messages eHuB réels

Ce script génère des exemples de messages eHuB tels qu'ils sont envoyés par les systèmes externes
(Unity, applications, etc.) en formats Base64, binaire et hexadécimal.
"""

import struct
import gzip
import base64
import sys
import os

def generate_real_config_message():
    """Génère un message CONFIG eHuB réel."""
    print("🔧 Génération du message CONFIG réel...")
    
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
    
    print(f"✅ Message CONFIG généré")
    print(f"   - {len(ranges)} plages définies")
    print(f"   - Taille totale: {len(message)} bytes")
    print(f"   - Taille compressée: {len(compressed)} bytes")
    
    return message

def generate_real_update_message(pattern="test"):
    """Génère un message UPDATE eHuB réel."""
    print(f"🎨 Génération du message UPDATE réel ({pattern})...")
    
    entities = []
    
    if pattern == "test":
        # Test simple: 4 LEDs rouges, une par contrôleur
        entities = [
            (100, 255, 0, 0, 0),    # Rouge sur contrôleur 1
            (5100, 255, 0, 0, 0),   # Rouge sur contrôleur 2
            (10100, 255, 0, 0, 0),  # Rouge sur contrôleur 3
            (15100, 255, 0, 0, 0),  # Rouge sur contrôleur 4
        ]
        
    elif pattern == "rainbow":
        # Arc-en-ciel sur le premier contrôleur
        entities = [
            (100, 255, 0, 0, 0),    # Rouge
            (101, 255, 128, 0, 0),  # Orange
            (102, 255, 255, 0, 0),  # Jaune
            (103, 0, 255, 0, 0),    # Vert
            (104, 0, 0, 255, 0),    # Bleu
            (105, 128, 0, 255, 0),  # Violet
        ]
        
    elif pattern == "white":
        # Blanc sur tous les contrôleurs
        entities = [
            (100, 255, 255, 255, 0),
            (5100, 255, 255, 255, 0),
            (10100, 255, 255, 255, 0),
            (15100, 255, 255, 255, 0),
        ]
        
    elif pattern == "gradient":
        # Dégradé de rouge sur le premier contrôleur
        entities = []
        for i in range(10):
            intensity = 255 - (i * 25)
            entities.append((100 + i, intensity, 0, 0, 0))
    
    # Construire le payload
    payload = b''
    for entity_id, r, g, b, w in entities:
        payload += struct.pack('<HBBBB', entity_id, r, g, b, w)
    
    # Compresser
    compressed = gzip.compress(payload)
    
    # Construire le header
    header = b'eHuB\x02\x00' + struct.pack('<H', len(entities)) + struct.pack('<H', len(compressed))
    message = header + compressed
    
    print(f"✅ Message UPDATE généré")
    print(f"   - {len(entities)} entités définies")
    print(f"   - Taille totale: {len(message)} bytes")
    print(f"   - Taille compressée: {len(compressed)} bytes")
    
    return message

def format_message_examples(message, msg_type):
    """Formate un message dans tous les formats possibles."""
    examples = {}
    
    # Format Base64 (le plus courant pour les applications)
    examples["Base64"] = base64.b64encode(message).decode('ascii')
    
    # Format Hexadécimal
    examples["Hexadécimal"] = message.hex()
    
    # Format Binaire (pour debug)
    examples["Binaire"] = repr(message)
    
    # Format lisible pour inspection
    examples["Lisible"] = f"eHuB + {len(message)-4} bytes de données"
    
    return examples

def main():
    """Fonction principale - génère des exemples de messages eHuB réels."""
    print("🧪 === GÉNÉRATEUR D'EXEMPLES eHuB RÉELS ===")
    print("Ce script génère des messages eHuB tels qu'envoyés par les systèmes externes")
    print("(Unity, applications, etc.) en formats Base64, binaire et hexadécimal.")
    print()
    
    # Générer message CONFIG
    print("1. MESSAGE CONFIG RÉEL")
    config_message = generate_real_config_message()
    config_examples = format_message_examples(config_message, "CONFIG")
    print()
    
    # Générer messages UPDATE
    print("2. MESSAGES UPDATE RÉELS")
    update_patterns = ["test", "rainbow", "white", "gradient"]
    update_examples = {}
    
    for pattern in update_patterns:
        update_message = generate_real_update_message(pattern)
        update_examples[pattern] = format_message_examples(update_message, "UPDATE")
        print()
    
    # Sauvegarder dans un fichier
    print("3. SAUVEGARDE DES EXEMPLES")
    with open("real_ehub_examples.txt", "w") as f:
        f.write("=== EXEMPLES DE MESSAGES eHuB RÉELS ===\n")
        f.write("Ces messages sont au format utilisé par les systèmes externes (Unity, etc.)\n\n")
        
        f.write("🔧 MESSAGE CONFIG (Compatible avec l'écran complet):\n")
        f.write("Format Base64 (recommandé pour copier-coller):\n")
        f.write(f"{config_examples['Base64']}\n\n")
        
        f.write("Format Hexadécimal:\n")
        f.write(f"{config_examples['Hexadécimal']}\n\n")
        
        f.write("🎨 MESSAGES UPDATE:\n\n")
        for pattern, examples in update_examples.items():
            f.write(f"--- {pattern.upper()} ---\n")
            f.write("Format Base64:\n")
            f.write(f"{examples['Base64']}\n\n")
            f.write("Format Hexadécimal:\n")
            f.write(f"{examples['Hexadécimal']}\n\n")
    
    print("✅ Exemples sauvegardés dans 'real_ehub_examples.txt'")
    print()
    
    # Afficher les exemples Base64 pour usage immédiat
    print("📋 EXEMPLES PRÊTS À UTILISER (Format Base64):")
    print()
    print("CONFIG (copiez-collez dans l'option 8):")
    print(config_examples['Base64'])
    print()
    
    print("UPDATE Examples (copiez-collez dans l'option 8):")
    for pattern, examples in update_examples.items():
        print(f"{pattern}: {examples['Base64']}")
    print()
    
    # Instructions d'utilisation
    print("📋 INSTRUCTIONS D'UTILISATION:")
    print("1. Lancez: python demo/animation_demo.py")
    print("2. Choisissez l'option 8 (Test messages eHuB manuel)")
    print("3. Collez le message CONFIG Base64 ci-dessus")
    print("4. Collez un des messages UPDATE Base64 ci-dessus")
    print("5. Spécifiez le nombre de répétitions (ex: 3)")
    print()
    
    print("💡 FORMATS SUPPORTÉS:")
    print("- Base64: Format le plus courant, utilisé par Unity et autres applications")
    print("- Hexadécimal: Format pour debugging et analyse")
    print("- Binaire: Format raw pour développeurs")
    print()
    
    print("🎯 Messages eHuB réels prêts à tester!")

if __name__ == "__main__":
    main()