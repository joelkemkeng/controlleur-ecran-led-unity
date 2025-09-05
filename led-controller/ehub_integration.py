#!/usr/bin/env python3
"""
Module d'intégration eHub pour le logiciel actuel
Permet d'ajouter l'émission eHub sans modifier le code existant
"""

import time
import threading
import numpy as np
from typing import Optional
from core.ehub_sender import EHubSender

class EHubIntegrator:
    """
    Intégrateur eHub pour le logiciel LED existant
    Capture les frames du logiciel actuel et les envoie via eHub
    """
    
    def __init__(self, target_ip: str = "127.0.0.1", target_port: int = 8765):
        self.sender = EHubSender(target_ip, target_port)
        self.running = False
        self.thread = None
        self.last_frame = None
        self.frame_lock = threading.Lock()
        self.send_interval = 1.0 / 30  # 30 FPS par défaut
        self.stats = {
            "frames_sent": 0,
            "entities_sent": 0,
            "start_time": None
        }
    
    def start_integration(self):
        """Démarre l'intégration eHub"""
        if self.running:
            return
        
        self.running = True
        self.stats["start_time"] = time.time()
        self.thread = threading.Thread(target=self._send_loop, daemon=True)
        self.thread.start()
        print(f"🔗 Intégration eHub démarrée (cible: {self.sender.target_ip}:{self.sender.target_port})")
    
    def stop_integration(self):
        """Arrête l'intégration eHub"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        self.sender.close()
        
        # Afficher les statistiques finales
        elapsed = time.time() - self.stats["start_time"] if self.stats["start_time"] else 0
        fps = self.stats["frames_sent"] / elapsed if elapsed > 0 else 0
        print(f"📊 Intégration arrêtée: {self.stats['frames_sent']} frames envoyées ({fps:.1f} FPS)")
    
    def update_frame(self, frame: np.ndarray):
        """
        Met à jour la frame à envoyer
        
        Args:
            frame: Frame numpy (H, W, 3) avec valeurs RGB 0-255
        """
        with self.frame_lock:
            self.last_frame = frame.copy() if frame is not None else None
    
    def _send_loop(self):
        """Boucle d'envoi des frames"""
        last_send_time = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # Envoyer à la fréquence configurée
                if current_time - last_send_time >= self.send_interval:
                    with self.frame_lock:
                        if self.last_frame is not None:
                            entities = self._frame_to_entities(self.last_frame)
                            if entities:
                                self.sender.send_entities(entities)
                                self.stats["frames_sent"] += 1
                                self.stats["entities_sent"] += len(entities)
                                last_send_time = current_time
                
                # Petit délai pour éviter une utilisation CPU excessive
                time.sleep(0.001)
                
            except Exception as e:
                print(f"❌ Erreur dans boucle d'envoi eHub: {e}")
                time.sleep(0.1)
    
    def _frame_to_entities(self, frame: np.ndarray) -> list:
        """
        Convertit une frame en liste d'entités eHub
        
        Args:
            frame: Frame numpy (H, W, 3)
            
        Returns:
            Liste d'entités [(entity_id, r, g, b, w), ...]
        """
        entities = []
        height, width = frame.shape[:2]
        
        for y in range(height):
            for x in range(width):
                r, g, b = frame[y, x]
                
                # Ignorer les pixels noirs pour optimiser
                if r > 0 or g > 0 or b > 0:
                    # Convertir coordonnées en entity_id
                    entity_id = y * width + x + 1  # +1 car les IDs commencent à 1
                    entities.append((entity_id, int(r), int(g), int(b), 0))
        
        return entities
    
    def set_fps(self, fps: float):
        """Définit la fréquence d'envoi"""
        self.send_interval = 1.0 / fps if fps > 0 else 1.0 / 30
        print(f"🎯 FPS eHub: {fps}")

# Classe helper pour l'intégration simple
class SimpleEHubBridge:
    """
    Pont simple pour intégrer eHub au logiciel actuel
    Usage: remplacer les appels de rendu par des appels à cette classe
    """
    
    def __init__(self):
        self.integrator = None
        self.enabled = False
    
    def enable_ehub(self, target_ip: str = "127.0.0.1", target_port: int = 8765):
        """Active l'envoi eHub"""
        if not self.enabled:
            self.integrator = EHubIntegrator(target_ip, target_port)
            self.integrator.start_integration()
            self.enabled = True
            print("✅ Pont eHub activé")
    
    def disable_ehub(self):
        """Désactive l'envoi eHub"""
        if self.enabled and self.integrator:
            self.integrator.stop_integration()
            self.integrator = None
            self.enabled = False
            print("❌ Pont eHub désactivé")
    
    def send_frame(self, frame: np.ndarray):
        """Envoie une frame si eHub est activé"""
        if self.enabled and self.integrator:
            self.integrator.update_frame(frame)
    
    def send_game_state(self, game_objects: list):
        """
        Envoie l'état d'un jeu sous forme d'entités eHub
        
        Args:
            game_objects: Liste d'objets [(x, y, r, g, b), ...]
        """
        if not (self.enabled and self.integrator):
            return
        
        entities = []
        for obj in game_objects:
            x, y, r, g, b = obj[:5]
            entity_id = y * 128 + x + 1  # Supposer écran 128x128
            entities.append((entity_id, r, g, b, 0))
        
        if entities:
            self.integrator.sender.send_entities(entities)

# Instance globale pour faciliter l'intégration
ehub_bridge = SimpleEHubBridge()

# Fonctions helper pour une intégration rapide
def enable_ehub_output(target_ip: str = "127.0.0.1", target_port: int = 8765):
    """Active rapidement la sortie eHub"""
    ehub_bridge.enable_ehub(target_ip, target_port)

def disable_ehub_output():
    """Désactive rapidement la sortie eHub"""
    ehub_bridge.disable_ehub()

def send_frame_to_ehub(frame: np.ndarray):
    """Envoie rapidement une frame vers eHub"""
    ehub_bridge.send_frame(frame)

def send_pixels_to_ehub(pixels: list):
    """
    Envoie rapidement des pixels vers eHub
    
    Args:
        pixels: Liste de pixels [(x, y, r, g, b), ...]
    """
    ehub_bridge.send_game_state(pixels)

if __name__ == "__main__":
    # Test du pont eHub
    print("🧪 Test du pont eHub")
    
    # Créer une frame de test
    test_frame = np.zeros((10, 10, 3), dtype=np.uint8)
    test_frame[2:8, 2:8] = [255, 0, 0]  # Carré rouge
    
    # Activer le pont
    enable_ehub_output()
    
    try:
        # Envoyer quelques frames de test
        for i in range(10):
            print(f"Envoi frame {i+1}/10")
            send_frame_to_ehub(test_frame)
            time.sleep(0.5)
    finally:
        disable_ehub_output()
    
    print("✅ Test terminé")
