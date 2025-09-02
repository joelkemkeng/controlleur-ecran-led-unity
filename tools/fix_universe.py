#!/usr/bin/env python3
"""
Script pour modifier l'univers dans les données eHub
"""

import ast

def fix_universe_in_data(data, new_universe):
    """Modifie l'univers dans les données eHub"""
    if len(data) < 8:
        return data
    
    # Conversion en bytearray pour modification
    data_array = bytearray(data)
    
    # Modification de l'univers (bytes 6-7, little endian)
    data_array[6:8] = new_universe.to_bytes(2, byteorder='little')
    
    return bytes(data_array)

def main():
    target_universe = 1  # Univers cible
    
    try:
        with open('data_send.txt', 'r') as f:
            lines = f.readlines()
        
        new_lines = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('CONFIG:') or line.startswith('UPDATE:'):
                prefix = line.split(':', 1)[0]
                data_str = line.split(':', 1)[1]
                
                try:
                    data_bytes = ast.literal_eval(data_str)
                    fixed_data = fix_universe_in_data(data_bytes, target_universe)
                    new_lines.append(f"{prefix}:{fixed_data}\n")
                    print(f"Modifié {prefix} pour univers {target_universe}")
                    
                except Exception as e:
                    print(f"Erreur modification {prefix}: {e}")
                    new_lines.append(line + '\n')
            else:
                new_lines.append(line + '\n')
        
        # Sauvegarde le fichier modifié
        with open('data_send_universe1.txt', 'w') as f:
            f.writelines(new_lines)
            
        print(f"\nFichier sauvegardé: data_send_universe1.txt")
        print(f"Toutes les données sont maintenant sur l'univers {target_universe}")
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    main()