#!/usr/bin/env python3
"""
🚀 VERSION SIMPLE OPTIMISÉE POUR FLUIDITÉ 🚀

Optimisations simples mais efficaces:
✅ 1. Envoi asynchrone avec threading
✅ 2. Cache des paquets identiques  
✅ 3. Contrôle FPS précis
✅ 4. Batch sending
✅ 5. Statistiques temps réel
"""

import socket
import struct
import time
import threading
import queue
from typing import Dict, List, Tuple, Optional, Any
from collections import deque
import sys
import os

# Import du pipeline existant
sys.path.append('/home/joel/projet_ecran/controlleur-ecran-led-unity/FINAL-DEV/etape-03-mapping-dmx')
sys.path.append('/home/joel/projet_ecran/controlleur-ecran-led-unity')

# Import des classes existantes
from FINAL_DEV.etape_03_mapping_dmx.ehub_dmx_pipeline import EHubDMXPipeline

class FastArtNetSender:
    """
    🔥 Sender ArtNet optimisé pour vitesse
    """
    
    def __init__(self, target_fps: int = 60):
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        
        # Contrôleurs BC216
        self.controllers = [
            ("192.168.1.45", 6454),
            ("192.168.1.46", 6454), 
            ("192.168.1.47", 6454),
            ("192.168.1.48", 6454)
        ]
        
        # Socket optimisé
        self.socket = None
        
        # Threading pour envoi asynchrone
        self.send_queue = queue.Queue(maxsize=500)
        self.sender_thread = None
        self.running = False
        
        # Cache simple des derniers paquets
        self.packet_cache = {}  # {(ip, universe): (data, timestamp)}
        self.cache_duration = 0.05  # 50ms cache
        
        # Statistiques
        self.stats = {
            'frames_sent': 0,
            'packets_sent': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'fps_actual': 0.0,
            'avg_send_time': 0.0
        }
        
        # Timing
        self.last_frame_time = 0
        self.frame_times = deque(maxlen=30)
        
        print(f"🚀 [FastArtNetSender] Init - Target: {target_fps}FPS")
    
    def initialize(self) -> bool:
        """Initialise le sender rapide"""
        try:
            # Socket UDP optimisé
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)  # 64KB buffer
            
            # Démarrer thread d'envoi
            self.running = True
            self.sender_thread = threading.Thread(target=self._sender_loop, daemon=True)
            self.sender_thread.start()
            
            print("✅ [FastArtNetSender] Initialisé avec thread asynchrone")
            return True
            
        except Exception as e:
            print(f"❌ [FastArtNetSender] Erreur init: {e}")
            return False
    
    def create_artnet_packet(self, universe: int, dmx_data: bytes) -> bytes:
        """Création rapide de paquet ArtNet"""
        header = b'Art-Net\x00\x00\x50\x00\x0e'
        packet = header + struct.pack('<HH', universe, len(dmx_data)) + dmx_data
        return packet
    
    def _sender_loop(self):
        """Boucle d'envoi asynchrone"""
        batch = []
        batch_size = 8
        
        while self.running:
            try:
                # Collecter batch
                timeout = 0.002  # 2ms timeout
                
                while len(batch) < batch_size:
                    try:
                        item = self.send_queue.get(timeout=timeout)
                        batch.append(item)
                    except queue.Empty:
                        break
                
                # Envoyer le batch
                if batch:
                    self._send_batch_fast(batch)
                    batch.clear()
                    
            except Exception as e:
                print(f"❌ [FastArtNetSender] Erreur sender loop: {e}")
    
    def _send_batch_fast(self, batch):
        """Envoi rapide d'un batch"""
        for packet_data, controller_addr in batch:
            try:
                self.socket.sendto(packet_data, controller_addr)
                self.stats['packets_sent'] += 1
            except Exception as e:
                print(f"❌ [FastArtNetSender] Erreur envoi: {e}")
    
    def send_dmx_universes_fast(self, universes: Dict) -> bool:
        """
        🔥 Envoi rapide avec contrôle FPS et cache
        """
        if not self.running or not universes:
            return True
        
        current_time = time.time()
        
        # Contrôle FPS
        time_since_last = current_time - self.last_frame_time
        if time_since_last < self.frame_time:
            sleep_time = self.frame_time - time_since_last
            time.sleep(sleep_time)
            current_time = time.time()
        
        self.last_frame_time = current_time
        frame_start = current_time
        
        packets_queued = 0
        
        try:
            for universe_key, universe_obj in universes.items():
                if hasattr(universe_obj, 'dmx_data'):
                    dmx_data = bytes(universe_obj.dmx_data)
                    
                    # Extraire infos
                    if isinstance(universe_key, tuple) and len(universe_key) >= 2:
                        controller_ip = universe_key[0]
                        universe_number = universe_key[1]
                    else:
                        continue
                    
                    # Vérifier cache
                    cache_key = (controller_ip, universe_number)
                    use_cache = False
                    
                    if cache_key in self.packet_cache:
                        cached_data, timestamp = self.packet_cache[cache_key]
                        if current_time - timestamp < self.cache_duration and cached_data == dmx_data:
                            use_cache = True
                            self.stats['cache_hits'] += 1
                    
                    if not use_cache:
                        self.stats['cache_misses'] += 1
                        
                        # Créer nouveau paquet
                        packet_data = self.create_artnet_packet(universe_number, dmx_data)
                        
                        # Mettre en cache
                        self.packet_cache[cache_key] = (dmx_data, current_time)
                        
                        # Trouver contrôleur
                        controller_addr = None
                        for ip, port in self.controllers:
                            if ip == controller_ip:
                                controller_addr = (ip, port)
                                break
                        
                        if controller_addr:
                            # Ajouter à la queue asynchrone
                            try:
                                self.send_queue.put_nowait((packet_data, controller_addr))
                                packets_queued += 1
                            except queue.Full:
                                print("⚠️ [FastArtNetSender] Queue pleine")
            
            # Calcul FPS réel
            frame_time = time.time() - frame_start
            self.frame_times.append(frame_time)
            
            if len(self.frame_times) >= 10:
                avg_frame_time = sum(self.frame_times) / len(self.frame_times)
                self.stats['fps_actual'] = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
                self.stats['avg_send_time'] = avg_frame_time * 1000  # en ms
            
            self.stats['frames_sent'] += 1
            
            # Log périodique
            if self.stats['frames_sent'] % 60 == 0:
                self._print_stats()
            
            return True
            
        except Exception as e:
            print(f"❌ [FastArtNetSender] Erreur envoi: {e}")
            return False
    
    def _print_stats(self):
        """Affiche les stats de performance"""
        cache_ratio = 0
        if self.stats['cache_hits'] + self.stats['cache_misses'] > 0:
            cache_ratio = self.stats['cache_hits'] / (self.stats['cache_hits'] + self.stats['cache_misses']) * 100
        
        print(f"🔥 [FAST] FPS: {self.stats['fps_actual']:.1f}/{self.target_fps} | "
              f"Latence: {self.stats['avg_send_time']:.2f}ms | "
              f"Cache: {cache_ratio:.1f}% | "
              f"Frames: {self.stats['frames_sent']} | "
              f"Packets: {self.stats['packets_sent']}")
    
    def set_fps(self, fps: int):
        """Change le FPS target"""
        self.target_fps = fps
        self.frame_time = 1.0 / fps
        print(f"🎯 [FastArtNetSender] FPS: {fps}")
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques"""
        return self.stats.copy()
    
    def close(self):
        """Fermeture propre"""
        self.running = False
        if self.sender_thread:
            self.sender_thread.join(timeout=1.0)
        if self.socket:
            self.socket.close()
        print("🔌 [FastArtNetSender] Fermé")


class EHubFastPipeline:
    """
    🔥 Pipeline rapide et simple
    """
    
    def __init__(self, target_fps: int = 60):
        print(f"🔥 [EHubFastPipeline] Init - {target_fps}FPS")
        
        # Pipeline DMX existant
        self.dmx_pipeline = EHubDMXPipeline(8765)
        
        # Sender rapide
        self.fast_sender = FastArtNetSender(target_fps)
        
        self.target_fps = target_fps
    
    def initialize(self) -> bool:
        """Initialise le pipeline rapide"""
        if not self.dmx_pipeline.initialize():
            return False
        
        if not self.fast_sender.initialize():
            return False
        
        print("✅ [EHubFastPipeline] Pipeline rapide prêt")
        return True
    
    def run_fast(self):
        """Exécution rapide"""
        print(f"🔥 [EHubFastPipeline] DÉMARRAGE RAPIDE à {self.target_fps}FPS")
        
        try:
            while True:
                # Réception
                data = self.dmx_pipeline.udp_receiver.receive_packet()
                if data:
                    # Processing
                    dmx_universes = self.dmx_pipeline.process_ehub_packet(data)
                    
                    if dmx_universes:
                        # Envoi rapide
                        self.fast_sender.send_dmx_universes_fast(dmx_universes)
                
        except KeyboardInterrupt:
            print("\n🛑 [EHubFastPipeline] Arrêt demandé")
        finally:
            self.close()
    
    def set_fps(self, fps: int):
        """Change FPS"""
        self.target_fps = fps
        self.fast_sender.set_fps(fps)
    
    def get_performance_stats(self) -> Dict:
        """Stats de performance"""
        return {
            'target_fps': self.target_fps,
            'sender_stats': self.fast_sender.get_stats()
        }
    
    def close(self):
        """Fermeture"""
        self.fast_sender.close()
        print("🔌 [EHubFastPipeline] Fermé")


def main():
    """
    🔥 Main rapide avec contrôles FPS
    """
    print("=" * 50)
    print("🔥 CONTRÔLEUR LED RAPIDE - Version Optimisée 🔥")
    print("=" * 50)
    
    print("\nChoix du FPS:")
    print("1. 30 FPS (stable)")
    print("2. 60 FPS (fluide)")
    print("3. 90 FPS (très fluide)")
    print("4. 120 FPS (ultra fluide)")
    
    choice = input("Choix (1-4) ou FPS personnalisé: ").strip()
    
    fps_map = {'1': 30, '2': 60, '3': 90, '4': 120}
    
    if choice in fps_map:
        target_fps = fps_map[choice]
    elif choice.isdigit():
        target_fps = int(choice)
    else:
        target_fps = 60  # défaut
    
    print(f"\n🎯 FPS sélectionné: {target_fps}")
    
    # Créer pipeline
    pipeline = EHubFastPipeline(target_fps)
    
    if not pipeline.initialize():
        print("❌ Échec initialisation")
        return
    
    print(f"\n🔥 PIPELINE RAPIDE DÉMARRÉ")
    print("  Optimisations: Threading asynchrone, Cache, Contrôle FPS")
    print("  Ctrl+C pour arrêter")
    
    try:
        pipeline.run_fast()
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        pipeline.close()


if __name__ == "__main__":
    main()
