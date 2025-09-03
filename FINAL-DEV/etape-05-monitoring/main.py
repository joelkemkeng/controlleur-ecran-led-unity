#!/usr/bin/env python3
"""
🚀 eHub Monitor - Application de Monitoring Moderne
Point d'entrée principal de l'application

PHASE 1 - ÉTAPE 1.1 : Setup Framework CustomTkinter ✅
- Interface moderne avec CustomTkinter
- Système de thèmes sombre/clair
- Navigation sidebar professionnelle  
- Architecture modulaire extensible
"""

import sys
import os
from pathlib import Path

# Ajouter le chemin de l'application au PYTHONPATH
app_path = Path(__file__).parent / "app"
sys.path.insert(0, str(app_path))

# Imports de l'application
from ui.base_window import MainWindow
from utils.themes import get_theme_manager, ThemeMode
import customtkinter as ctk

def setup_application():
    """
    🔧 Configuration initiale de l'application
    """
    print("🚀 [Main] Initialisation eHub Monitor...")
    
    # Configuration CustomTkinter
    ctk.set_default_color_theme("blue")  # Couleur par défaut
    ctk.set_widget_scaling(1.0)  # Scaling par défaut
    ctk.set_window_scaling(1.0)
    
    # Thème par défaut
    get_theme_manager().set_theme(ThemeMode.DARK)
    
    print("✅ [Main] Configuration terminée")

def main():
    """
    🏠 Fonction principale de l'application
    """
    try:
        # Setup initial
        setup_application()
        
        # Création et lancement de l'application
        print("🏠 [Main] Création de la fenêtre principale...")
        app = MainWindow()
        
        print("🎉 [Main] Lancement de l'application eHub Monitor")
        print("=" * 50)
        print("🎨 Interface moderne avec CustomTkinter")
        print("🧭 Navigation sidebar avec 5 sections")
        print("🌙 Thèmes sombre/clair avec switch")
        print("🏗️ Architecture modulaire extensible") 
        print("=" * 50)
        print("🚀 Application prête ! Utilisez la sidebar pour naviguer")
        
        # Boucle principale
        app.mainloop()
        
    except Exception as e:
        print(f"❌ [Main] Erreur lors du lancement: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()