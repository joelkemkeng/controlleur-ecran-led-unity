#!/usr/bin/env python3
"""
Analyse du mapping spatial pour debug
"""
import numpy as np

def calculate_led_position(entity_id, width=128, height=128):
    """
    Calcule la position spatiale réelle d'une LED sur l'écran
    """
    if 100 <= entity_id <= 16577:  # Range principal observé
        # Normaliser l'entity_id dans une grille logique
        normalized_id = entity_id - 100
        
        # Disposition séquentielle: ligne par ligne
        pixels_per_line = width  # 128 pixels par ligne
        
        line = normalized_id // pixels_per_line
        col = normalized_id % pixels_per_line
        
        # Assurer qu'on reste dans les limites
        y = min(line, height - 1)
        x = min(col, width - 1)
        
        return x, y
    else:
        # Pour les IDs hors range, distribution uniforme
        x = (entity_id * 7) % width
        y = (entity_id * 11) % height
        return x, y

def analyze_mapping():
    """Analyse la distribution spatiale"""
    
    # Test avec les entity_ids observées dans les logs
    test_entities = [1, 100, 101, 102, 259, 400, 2051, 4044, 6196, 8189, 10341, 12334, 14327, 16479]
    
    print("🔍 Analyse du mapping spatial:")
    print("=" * 50)
    
    for entity_id in test_entities:
        x, y = calculate_led_position(entity_id)
        print(f"Entity {entity_id:5d} → Position ({x:3d}, {y:3d})")
    
    # Créer une mini visualisation ASCII
    print("\n📊 Visualisation ASCII des positions (réduites 32x32):")
    
    # Grille réduite pour affichage
    grid_size = 32
    scale_x = 128 // grid_size  # 4
    scale_y = 128 // grid_size  # 4
    
    grid = [['.' for _ in range(grid_size)] for _ in range(grid_size)]
    
    # Placer les entités sur la grille réduite
    for entity_id in test_entities:
        x, y = calculate_led_position(entity_id)
        # Réduire les coordonnées
        grid_x = min(x // scale_x, grid_size - 1)
        grid_y = min(y // scale_y, grid_size - 1)
        
        # Marquer la position avec un symbole selon l'ID
        if entity_id == 1:
            grid[grid_y][grid_x] = '★'  # Entité spéciale
        elif entity_id < 1000:
            grid[grid_y][grid_x] = '●'  # Début
        elif entity_id < 10000:
            grid[grid_y][grid_x] = '◆'  # Milieu
        else:
            grid[grid_y][grid_x] = '▲'  # Fin
    
    # Afficher la grille
    for row in grid:
        print(''.join(row))
    
    print("\nLégende: ★=Entity1, ●=<1K, ◆=1K-10K, ▲=>10K, .=vide")

def analyze_entity_ranges():
    """Analyse les ranges d'entités pour comprendre la structure"""
    
    # Ranges observées dans les logs
    ranges = [
        (100, 269, "192.168.1.45:u0"),      # 170 LEDs
        (270, 358, "192.168.1.45:u1"),      # 89 LEDs  
        (400, 569, "192.168.1.45:u2"),      # 170 LEDs
        (2051, 2055, "Exemple observé"),
        (4044, 4048, "Exemple observé"),
        (6196, 6200, "Exemple observé"),
        (8189, 8193, "Exemple observé"),
        (10341, 10345, "Exemple observé"),
        (12334, 12338, "Exemple observé"),
        (14327, 14331, "Exemple observé"),
        (16479, 16483, "Exemple observé"),
    ]
    
    print("\n🗺️ Analyse des ranges d'entités:")
    print("=" * 60)
    
    for start, end, info in ranges:
        count = end - start + 1
        # Calculer positions pour visualiser la distribution
        start_x, start_y = calculate_led_position(start)
        end_x, end_y = calculate_led_position(end)
        
        print(f"Range {start:5d}-{end:5d} ({count:3d} LEDs) → ({start_x:3d},{start_y:3d}) à ({end_x:3d},{end_y:3d}) | {info}")

if __name__ == "__main__":
    analyze_mapping()
    analyze_entity_ranges()
