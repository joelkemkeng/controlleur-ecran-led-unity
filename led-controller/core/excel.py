import openpyxl
from typing import Dict, Tuple

def get_pixel_mapping(file_path: str) -> Dict[int, Tuple[int, int]]:
    """
    Extrait le mapping des pixels depuis un fichier Excel.
    La feuille de calcul doit contenir les colonnes 'ID', 'X', 'Y'.
    Retourne un dictionnaire: { led_id: (x, y) }
    """
    if not file_path:
        return {}
        
    try:
        workbook = openpyxl.load_workbook(file_path)
        # On suppose que le mapping est dans la première feuille
        sheet = workbook.active
        mapping = {}
        
        # On suppose un en-tête et que le format est: ID, X, Y
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if len(row) >= 3:
                try:
                    # Assurer une conversion propre en entier
                    led_id = int(float(row[0]))
                    x = int(float(row[1]))
                    y = int(float(row[2]))
                    mapping[led_id] = (x, y)
                except (ValueError, TypeError, IndexError):
                    # Ignorer les lignes mal formatées ou vides
                    continue
                    
        return mapping
    except FileNotFoundError:
        print(f"Erreur: Le fichier {file_path} n'a pas été trouvé.")
        return {}
    except Exception as e:
        print(f"Une erreur est survenue lors de la lecture du fichier Excel: {e}")
        return {}

