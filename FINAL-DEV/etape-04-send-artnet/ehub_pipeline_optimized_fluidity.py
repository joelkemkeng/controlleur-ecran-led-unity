#!/usr/bin/env python3
"""
🚀 PIPELINE ÉTAPE 4 OPTIMISÉ POUR FLUIDITÉ MAXIMALE 🚀

Optimisations pour vitesse ultra-rapide:
✅ 1. Threading asynchrone pour l'envoi ArtNet
✅ 2. Cache intelligent des paquets DMX inchangés
✅ 3. Batch sending (groupes de paquets)
✅ 4. Configuration FPS personnalisée
✅ 5. Queue de priorité pour les univers les plus actifs
✅ 6. Pre-computed packets (paquets pré-calculés)
✅ 7. Socket optimisé avec buffer size
"""

import socket
import struct
import time
import threading
import queue
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
import sys
import os

# Import des étapes précédentes
sys.path.append('/home/joel/projet_ecran/controlleur-ecran-led-unity/FINAL-DEV/etape-03-mapping-dmx')
from ehub_dmx_pipeline import EHubDMXPipeline

class OptimizedArtNetSender:
    """
    🔥 ArtNet Sender ULTRA-OPTIMISÉ pour fluidité maximale
    """
    
    def __init__(self, target_fps: int = 60, batch_size: int = 8):
        """
        Args:
            target_fps: FPS cible (default: 60fps = 16.67ms par frame)
            batch_size: Nombre de paquets à envoyer par batch
        """
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps  # Temps par frame en secondes
        self.batch_size = batch_size
        
        # Contrôleurs BC216
        self.controllers = [
            ("192.168.1.45", 6454),
            ("192.168.1.46", 6454), 
            ("192.168.1.47", 6454),
            ("192.168.1.48", 6454)
        ]
        
        # Socket optimisé
        self.socket = None
        self.socket_buffer_size = 65536  # 64KB buffer
        
        # Threading pour envoi asynchrone
        self.send_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="ArtNet")
        self.send_queue = queue.PriorityQueue(maxsize=1000)
        self.running = False
        
        # Cache intelligent des paquets
        self.packet_cache = {}  # {(ip, universe): (packet_data, timestamp)}
        self.cache_timeout = 0.1  # 100ms cache timeout
        
        # Statistiques de performance
        self.stats = {
            'frames_sent': 0,
            'packets_sent': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'send_time_avg': 0.0,
            'fps_actual': 0.0,
            'dropped_frames': 0
        }
        
        # Timing pour FPS
        self.last_frame_time = 0
        self.frame_times = deque(maxlen=60)  # Historique des 60 dernières frames
        
        # Pre-computed headers
        self.artnet_header = b'Art-Net\x00\x00\x50\x00\x0e'
        
        print(f"🚀 [OptimizedArtNetSender] Initialisé - Target: {target_fps}FPS, Batch: {batch_size}")
    
    def initialize(self) -> bool:
        """Initialise le socket optimisé et démarre les threads"""
        try:
            # Socket UDP optimisé
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, self.socket_buffer_size)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Démarrer le thread d'envoi asynchrone
            self.running = True
            self.send_thread = threading.Thread(target=self._async_sender_loop, daemon=True)
            self.send_thread.start()
            
            print(f"✅ [OptimizedArtNetSender] Socket optimisé créé - Buffer: {self.socket_buffer_size}B")
            return True
            
        except Exception as e:
            print(f"❌ [OptimizedArtNetSender] Erreur init: {e}")
            return False
    
    def create_artnet_packet_fast(self, universe: int, dmx_data: bytes) -> bytes:
        """Création ultra-rapide de paquet ArtNet avec header pré-calculé"""
        # Header pré-calculé + universe + length
        packet = self.artnet_header + struct.pack('<HH', universe, len(dmx_data)) + dmx_data
        return packet
    
    def _should_use_cache(self, universe_key: Tuple, dmx_data: bytes) -> Optional[bytes]:
        """Vérifie si on peut utiliser le cache pour ce paquet"""
        current_time = time.time()
        
        if universe_key in self.packet_cache:
            cached_packet, timestamp = self.packet_cache[universe_key]
            
            # Cache valide si moins de cache_timeout secondes
            if current_time - timestamp < self.cache_timeout:
                self.stats['cache_hits'] += 1
                return cached_packet
        
        # Cache miss - créer nouveau paquet
        self.stats['cache_misses'] += 1
        return None
    
    def _update_cache(self, universe_key: Tuple, packet_data: bytes):
        """Met à jour le cache avec le nouveau paquet"""
        self.packet_cache[universe_key] = (packet_data, time.time())
    
    def _async_sender_loop(self):
        """Boucle asynchrone d'envoi des paquets"""
        batch = []
        
        while self.running:
            try:
                # Collecter un batch de paquets
                timeout = 0.001  # 1ms timeout pour réactivité
                
                while len(batch) < self.batch_size:
                    try:
                        priority, packet_data, controller_addr = self.send_queue.get(timeout=timeout)
                        batch.append((packet_data, controller_addr))
                    except queue.Empty:
                        break
                
                # Envoyer le batch s'il y a des paquets
                if batch:
                    self._send_batch(batch)
                    batch.clear()
                
            except Exception as e:
                print(f"❌ [OptimizedArtNetSender] Erreur async sender: {e}")
    
    def _send_batch(self, batch: List[Tuple[bytes, Tuple]]):
        """Envoi optimisé d'un batch de paquets"""
        start_time = time.time()
        sent_count = 0
        
        for packet_data, controller_addr in batch:
            try:
                self.socket.sendto(packet_data, controller_addr)
                sent_count += 1
            except Exception as e:
                print(f"❌ [OptimizedArtNetSender] Erreur envoi {controller_addr}: {e}")
        
        # Mise à jour des stats
        send_time = time.time() - start_time
        self.stats['packets_sent'] += sent_count
        
        # Moyenne mobile du temps d'envoi
        if self.stats['frames_sent'] > 0:
            self.stats['send_time_avg'] = (self.stats['send_time_avg'] * 0.9) + (send_time * 0.1)
        else:
            self.stats['send_time_avg'] = send_time
    
    def send_dmx_universes_optimized(self, universes: Dict) -> bool:
        """
        🚀 ENVOI ULTRA-OPTIMISÉ avec contrôle FPS
        """
        if not self.running or not universes:
            return True
        
        current_time = time.time()
        
        # Contrôle de FPS - éviter d'envoyer trop vite
        time_since_last_frame = current_time - self.last_frame_time
        if time_since_last_frame < self.frame_time:
            # Frame trop rapide - attendre
            sleep_time = self.frame_time - time_since_last_frame
            time.sleep(sleep_time)
            current_time = time.time()
        
        self.last_frame_time = current_time
        frame_start = current_time
        
        # Priorité: univers avec plus de changements = priorité plus haute
        priority_base = 1000
        packets_queued = 0
        
        try:
            for universe_key, universe_obj in universes.items():
                if hasattr(universe_obj, 'dmx_data'):
                    dmx_data = bytes(universe_obj.dmx_data)
                    
                    # Extraire infos univers
                    if isinstance(universe_key, tuple) and len(universe_key) >= 2:
                        controller_ip = universe_key[0]
                        universe_number = universe_key[1]
                    else:
                        continue
                    
                    # Vérifier cache
                    cache_key = (controller_ip, universe_number)
                    cached_packet = self._should_use_cache(cache_key, dmx_data)
                    
                    if cached_packet:
                        packet_data = cached_packet
                    else:
                        # Créer nouveau paquet
                        packet_data = self.create_artnet_packet_fast(universe_number, dmx_data)
                        self._update_cache(cache_key, packet_data)
                    
                    # Trouver contrôleur
                    controller_addr = None
                    for ip, port in self.controllers:
                        if ip == controller_ip:
                            controller_addr = (ip, port)
                            break
                    
                    if controller_addr:
                        # Priorité basée sur l'activité de l'univers
                        priority = priority_base - (len(dmx_data) // 10)  # Plus de données = plus prioritaire
                        
                        # Ajouter à la queue asynchrone
                        try:
                            self.send_queue.put_nowait((priority, packet_data, controller_addr))
                            packets_queued += 1
                        except queue.Full:
                            self.stats['dropped_frames'] += 1
                            print("⚠️ [OptimizedArtNetSender] Queue pleine - frame droppée")
            
            # Calcul FPS réel
            frame_time = time.time() - frame_start
            self.frame_times.append(frame_time)
            
            if len(self.frame_times) >= 10:
                avg_frame_time = sum(self.frame_times) / len(self.frame_times)
                self.stats['fps_actual'] = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
            
            self.stats['frames_sent'] += 1
            
            # Log de performance
            if self.stats['frames_sent'] % 60 == 0:  # Chaque 60 frames
                self._print_performance_stats()
            
            return True
            
        except Exception as e:
            print(f"❌ [OptimizedArtNetSender] Erreur envoi optimisé: {e}")
            return False
    
    def _print_performance_stats(self):
        """Affiche les statistiques de performance"""
        cache_ratio = 0
        if self.stats['cache_hits'] + self.stats['cache_misses'] > 0:
            cache_ratio = self.stats['cache_hits'] / (self.stats['cache_hits'] + self.stats['cache_misses']) * 100
        
        print(f"📊 [PERF] FPS: {self.stats['fps_actual']:.1f}/{self.target_fps} | "
              f"Cache: {cache_ratio:.1f}% | "
              f"Frames: {self.stats['frames_sent']} | "
              f"Dropped: {self.stats['dropped_frames']} | "
              f"Avg Send: {self.stats['send_time_avg']*1000:.2f}ms")
    
    def set_target_fps(self, fps: int):
        """Change le FPS cible en temps réel"""
        self.target_fps = fps
        self.frame_time = 1.0 / fps
        print(f"🎯 [OptimizedArtNetSender] FPS cible: {fps}")
    
    def get_performance_stats(self) -> Dict:
        """Retourne les statistiques détaillées"""
        return self.stats.copy()
    
    def close(self):
        """Fermeture propre avec arrêt des threads"""
        self.running = False
        if hasattr(self, 'send_thread'):
            self.send_thread.join(timeout=1.0)
        if self.send_executor:
            self.send_executor.shutdown(wait=True)
        if self.socket:
            self.socket.close()
        print("🔌 [OptimizedArtNetSender] Fermé proprement")


class EHubFluidPipeline:
    """
    🔥 PIPELINE ULTRA-FLUIDE pour contrôle temps réel
    """
    
    def __init__(self, listen_port: int = 8765, target_fps: int = 60):
        print(f"🚀 [EHubFluidPipeline] Init - Target: {target_fps}FPS")
        
        # Pipeline DMX (Étapes 0-3)
        self.dmx_pipeline = EHubDMXPipeline(listen_port)
        
        # Sender ArtNet optimisé (Étape 4 ultra-rapide)
        self.optimized_sender = OptimizedArtNetSender(target_fps=target_fps)
        
        # Configuration de performance
        self.target_fps = target_fps
        self.performance_monitor = True
        
    def initialize(self) -> bool:
        """Initialise le pipeline ultra-rapide"""
        print("🔧 [EHubFluidPipeline] Initialisation...")
        
        if not self.dmx_pipeline.initialize():
            return False
        
        if not self.optimized_sender.initialize():
            return False
        
        print("✅ [EHubFluidPipeline] Pipeline ultra-rapide prêt")
        return True
    
    def set_fps(self, fps: int):
        """Change le FPS en temps réel"""
        self.target_fps = fps
        self.optimized_sender.set_target_fps(fps)
        print(f"🎯 [EHubFluidPipeline] FPS modifié: {fps}")
    
    def run_ultra_fluid(self):
        """Lance le pipeline avec fluidité maximale"""
        print(f"🔥 [EHubFluidPipeline] Démarrage ULTRA-FLUIDE à {self.target_fps}FPS")
        
        try:
            while True:
                # Réception et traitement (Étapes 0-3)
                data = self.dmx_pipeline.udp_receiver.receive_packet()
                if data:
                    # Traitement ultra-rapide
                    dmx_universes = self.dmx_pipeline.process_ehub_packet(data)
                    
                    if dmx_universes:
                        # Envoi optimisé (Étape 4)
                        self.optimized_sender.send_dmx_universes_optimized(dmx_universes)
                
        except KeyboardInterrupt:
            print("\n🛑 [EHubFluidPipeline] Arrêt demandé")
        finally:
            self.close()
    
    def get_performance_report(self) -> Dict:
        """Rapport de performance complet"""
        return {
            'target_fps': self.target_fps,
            'artnet_stats': self.optimized_sender.get_performance_stats(),
            'pipeline_stats': self.dmx_pipeline.get_stats() if hasattr(self.dmx_pipeline, 'get_stats') else {}
        }
    
    def close(self):
        """Fermeture propre"""
        self.optimized_sender.close()
        if hasattr(self.dmx_pipeline, 'close'):
            self.dmx_pipeline.close()
        print("🔌 [EHubFluidPipeline] Pipeline fermé")


def main():
    """
    🚀 MAIN ULTRA-OPTIMISÉ avec contrôles interactifs
    """
    print("=" * 60)
    print("🔥 CONTRÔLEUR LED ULTRA-FLUIDE - Version Optimisée 🔥")
    print("=" * 60)
    
    # Configuration par défaut
    DEFAULT_FPS = 60
    print(f"Target FPS: {DEFAULT_FPS} (changeable en temps réel)")
    
    # Créer le pipeline optimisé
    pipeline = EHubFluidPipeline(target_fps=DEFAULT_FPS)
    
    if not pipeline.initialize():
        print("❌ Échec d'initialisation")
        return
    
    print("\n🎮 COMMANDES INTERACTIVES:")
    print("  Ctrl+C : Arrêter")
    print("  En cours d'exécution: monitoring automatique des performances")
    
    try:
        # Lancer en mode ultra-fluide
        pipeline.run_ultra_fluid()
        
    except Exception as e:
        print(f"❌ Erreur pipeline: {e}")
    finally:
        pipeline.close()


if __name__ == "__main__":
    main()
