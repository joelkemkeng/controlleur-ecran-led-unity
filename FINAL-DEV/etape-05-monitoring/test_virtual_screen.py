#!/usr/bin/env python3
"""
🧪 Test automatique de l'écran virtuel LED
Navigation automatique vers l'écran virtuel et génération de motif de test
"""

import sys
import os
import time
import threading

# Ajouter le chemin vers l'application
sys.path.append(os.path.dirname(__file__))

def test_virtual_screen():
    """🖥️ Test de l'écran virtuel avec navigation automatique"""
    print("🧪 [Test] Démarrage test écran virtuel...")
    
    # Import de l'application
    from main import main, create_app
    
    # Créer l'application
    app = create_app()
    
    def automated_test():
        """🤖 Test automatisé avec délais"""
        time.sleep(2)  # Attendre le démarrage
        
        print("🧭 [Test] Navigation vers écran virtuel...")
        # Simuler le clic sur écran virtuel
        app._on_nav_click("virtual_screen")
        
        time.sleep(3)  # Attendre le chargement
        
        print("🧪 [Test] Génération motif de test...")
        # Générer un motif de test si la page est chargée
        if hasattr(app, 'virtual_screen_page') and app.virtual_screen_page:
            app.virtual_screen_page._generate_test_pattern()
        
        time.sleep(5)  # Observer le motif
        
        print("📡 [Test] Test des données ArtNet simulées...")
        # Les données ArtNet devraient être générées automatiquement
        
        time.sleep(5)  # Observer les données
        
        print("✅ [Test] Test terminé - Fermeture...")
        app.quit()
    
    # Démarrer le test automatisé dans un thread
    test_thread = threading.Thread(target=automated_test, daemon=True)
    test_thread.start()
    
    # Démarrer l'application
    try:
        app.mainloop()
    except KeyboardInterrupt:
        print("🛑 [Test] Interruption clavier")
    
    print("🎯 [Test] Test écran virtuel terminé")

if __name__ == "__main__":
    test_virtual_screen()
