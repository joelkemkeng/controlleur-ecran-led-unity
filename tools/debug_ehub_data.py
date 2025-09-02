#!/usr/bin/env python3
"""
Script pour analyser les données eHub et voir l'univers
"""

import ast

def analyze_ehub_header(data):
    """Analyse le header eHub pour extraire les infos de base"""
    if len(data) < 10:
        return None
    
    # Vérification signature eHuB
    if data[:4] != b'eHuB':
        return None
    
    # Parsing du header
    message_type = data[4]
    sequence = data[5]
    universe = int.from_bytes(data[6:8], byteorder='little')
    length = int.from_bytes(data[8:10], byteorder='little')
    
    return {
        'signature': data[:4].decode(),
        'type': message_type,
        'sequence': sequence,
        'universe': universe,
        'length': length
    }

def main():
    # Charge les données depuis le fichier
    try:
        with open('data_send.txt', 'r') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('CONFIG:') or line.startswith('UPDATE:'):
                prefix = line.split(':', 1)[0]
                data_str = line.split(':', 1)[1]
                
                try:
                    data_bytes = ast.literal_eval(data_str)
                    header = analyze_ehub_header(data_bytes)
                    
                    if header:
                        print(f"Paquet {i+1} ({prefix}):")
                        print(f"  - Type: {header['type']} ({'CONFIG' if header['type'] == 1 else 'UPDATE' if header['type'] == 2 else 'UNKNOWN'})")
                        print(f"  - Univers: {header['universe']}")
                        print(f"  - Séquence: {header['sequence']}")
                        print(f"  - Longueur: {header['length']}")
                        print(f"  - Taille totale: {len(data_bytes)} bytes")
                        print()
                    else:
                        print(f"Paquet {i+1} ({prefix}): Header invalide")
                        
                except Exception as e:
                    print(f"Erreur parsing paquet {i+1}: {e}")
                    
    except FileNotFoundError:
        print("Fichier data_send.txt non trouvé")
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    main()