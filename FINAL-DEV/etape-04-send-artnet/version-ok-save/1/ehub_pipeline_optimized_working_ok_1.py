#!/usr/bin/env python3
"""
🚀 OPTIMISATION DE FLUIDITÉ - Version basée sur le pipeline qui marche 🚀

Optimisations appliquées au pipeline existant:
✅ 1. Threading asynchrone pour ArtNet
✅ 2. Cache intelligent des paquets
✅ 3. Contrôle FPS configurable
✅ 4. Batch sending optimisé
✅ 5. Statistiques de performance temps réel
"""

import sys
import socket
import time
import threading
import queue
from pathlib import Path
from typing import Dict, Tuple, List
from collections import deque
import struct

# Utiliser le même import que le pipeline qui marche
current_dir = Path(__file__).parent
etape3_path = current_dir.parent / "etape-03-mapping-dmx"
sys.path.insert(0, str(etape3_path))

# Importer l'étape 3 complète qui fonctionne
from ehub_complete_pipeline_mapping_dmx import EHubDMXPipeline

class OptimizedArtNetSender:
    """
    🔥 Version optimisée de l'ArtNetSender pour fluidité maximale
    """
    
    def __init__(self, target_fps: int = 60):
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        
        # Mêmes contrôleurs BC216 que la version qui marche
        self.controllers = [
            ("192.168.1.45", 6454),
            ("192.168.1.46", 6454), 
            ("192.168.1.47", 6454),
            ("192.168.1.48", 6454)
        ]
        
        # Socket avec buffer optimisé
        self.socket = None
        
        # Queue asynchrone pour l'envoi
        self.send_queue = queue.Queue(maxsize=1000)
        self.sender_thread = None
        self.running = False
        
        # Cache des derniers paquets pour éviter les envois identiques
        self.packet_cache = {}  # {(ip, universe): (dmx_data_hash, timestamp)}
        self.cache_timeout = 0.033  # 33ms (environ 30fps)
        
        # Statistiques temps réel
        self.stats = {
            'packets_sent': 0,
            'frames_sent': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'queue_size_avg': 0,
            'send_time_avg': 0.0,
            'fps_actual': 0.0,
            'errors': 0
        }
        
        # Mesure de performance
        self.last_frame_time = 0
        self.frame_times = deque(maxlen=60)  # Dernières 60 frames
        
        print(f"🚀 [OptimizedArtNetSender] Optimisé pour {target_fps}FPS")
    
    def initialize(self) -> bool:
        """Initialise le sender optimisé"""
        try:
            # Socket UDP avec buffer plus grand
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 131072)  # 128KB buffer
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Démarrer le thread d'envoi asynchrone
            self.running = True
            self.sender_thread = threading.Thread(target=self._async_sender, daemon=True)
            self.sender_thread.start()
            
            print("✅ [OptimizedArtNetSender] Initialisé avec thread asynchrone")
            return True
            
        except Exception as e:
            print(f"❌ [OptimizedArtNetSender] Erreur init: {e}")
            return False
    
    def create_artnet_packet(self, universe: int, dmx_data: bytes) -> bytes:
        """
        Même méthode de création de paquet que la version qui marche
        """
        # Header ArtNet standard
        header = b'Art-Net\x00'  # 8 bytes
        opcode = struct.pack('<H', 0x5000)  # ART_DMX opcode en little-endian
        protocol_version = struct.pack('>H', 14)  # Version 14 en big-endian
        sequence = b'\x00'  # Pas de séquençage
        physical = b'\x00'  # Port physique
        universe_bytes = struct.pack('<H', universe)  # Univers en little-endian
        length = struct.pack('>H', len(dmx_data))  # Longueur en big-endian
        
        packet = header + opcode + protocol_version + sequence + physical + universe_bytes + length + dmx_data
        return packet
    
    def _async_sender(self):
        """Thread d'envoi asynchrone avec batch processing"""
        batch = []
        max_batch_size = 16  # Traiter jusqu'à 16 paquets à la fois
        
        while self.running:
            try:
                # Collecter un batch de paquets
                batch_start = time.time()
                
                while len(batch) < max_batch_size:
                    try:
                        # Timeout court pour éviter la latence
                        packet_data, controller_addr = self.send_queue.get(timeout=0.001)
                        batch.append((packet_data, controller_addr))
                    except queue.Empty:
                        break
                
                # Envoyer le batch si on a des paquets
                if batch:
                    self._send_batch_optimized(batch)
                    batch.clear()
                
                # Micro-pause pour éviter 100% CPU
                if not batch:
                    time.sleep(0.0001)  # 0.1ms
                    
            except Exception as e:
                print(f"❌ [OptimizedArtNetSender] Erreur thread: {e}")
    
    def _send_batch_optimized(self, batch: List[Tuple]):
        """Envoi optimisé d'un batch de paquets"""
        start_time = time.time()
        sent_count = 0
        
        for packet_data, controller_addr in batch:
            try:
                self.socket.sendto(packet_data, controller_addr)
                sent_count += 1
            except Exception as e:
                self.stats['errors'] += 1
                print(f"❌ [OptimizedArtNetSender] Erreur envoi {controller_addr}: {e}")
        
        # Mise à jour statistiques
        send_time = time.time() - start_time
        self.stats['packets_sent'] += sent_count
        
        # Moyenne mobile du temps d'envoi
        alpha = 0.1  # Facteur de lissage
        self.stats['send_time_avg'] = (1 - alpha) * self.stats['send_time_avg'] + alpha * send_time
    
    def _should_skip_duplicate(self, universe_key: Tuple, dmx_data: bytes) -> bool:
        """Vérifie si on peut skip ce paquet (identique au précédent récent)"""
        current_time = time.time()
        data_hash = hash(dmx_data)
        
        if universe_key in self.packet_cache:
            cached_hash, timestamp = self.packet_cache[universe_key]
            
            # Si données identiques et récentes, skip
            if (cached_hash == data_hash and 
                current_time - timestamp < self.cache_timeout):
                self.stats['cache_hits'] += 1
                return True
        
        # Nouvelles données ou cache expiré
        self.packet_cache[universe_key] = (data_hash, current_time)
        self.stats['cache_misses'] += 1
        return False
    
    def create_artnet_packet(self, universe: int, dmx_data: bytes) -> bytearray:
        """
        Crée un paquet ArtNet standard
        COPIÉ EXACTEMENT de test_artnet_direct.py qui fonctionne
        """
        # Header ArtNet (18 bytes)
        packet = bytearray([
            ord('A'), ord('r'), ord('t'), ord('-'),
            ord('N'), ord('e'), ord('t'), 0,  # ID "Art-Net\0"
            0x00, 0x50,  # OpCode (OpOutput) - little endian
            0, 14,  # Protocol version - big endian
            0,  # Sequence
            0,  # Physical
            universe & 0xFF,
            (universe >> 8) & 0xFF,  # Universe - little endian
            0x02, 0x00,  # Length (512) - big endian
        ])
        
        # Données DMX (512 bytes)
        dmx_buffer = bytearray(512)
        if dmx_data:
            copy_len = min(len(dmx_data), 512)
            dmx_buffer[:copy_len] = dmx_data[:copy_len]
        
        packet.extend(dmx_buffer)
        return packet

    def send_dmx_universes(self, universes: Dict) -> bool:
        """
        Envoie les univers DMX de l'étape 3 vers les contrôleurs BC216 
        (Méthode compatible avec le pipeline qui fonctionne)
        """
        if not self.socket:
            print("❌ [OptimizedArtNetSender] Socket non initialisé")
            return False
        
        if not universes:
            return True
        
        try:
            start_time = time.time()
            packets_sent = 0
            errors = 0
            
            # Parcourir tous les univers modifiés de l'étape 3
            for universe_key, universe_obj in universes.items():
                if hasattr(universe_obj, 'dmx_data'):
                    dmx_data = bytes(universe_obj.dmx_data)
                    
                    # Extraire le numéro d'univers depuis la clé
                    if isinstance(universe_key, tuple) and len(universe_key) >= 2:
                        universe_number = universe_key[1]  # (ip, universe)
                        controller_ip = universe_key[0]    # IP du contrôleur
                    else:
                        continue
                    
                    # Trouver le contrôleur correspondant
                    controller_addr = None
                    for ip, port in self.controllers:
                        if ip == controller_ip:
                            controller_addr = (ip, port)
                            break
                    
                    if controller_addr:
                        # Créer le paquet ArtNet avec la méthode qui fonctionne
                        artnet_packet = self.create_artnet_packet(universe_number, dmx_data)
                        
                        # Envoyer vers le contrôleur
                        try:
                            self.socket.sendto(artnet_packet, controller_addr)
                            packets_sent += 1
                        except Exception as e:
                            print(f"❌ [OptimizedArtNetSender] Erreur envoi {controller_addr}:u{universe_number}: {e}")
                            errors += 1
            
            # Statistiques
            send_time = time.time() - start_time
            self.stats['packets_sent'] += packets_sent
            self.stats['frames_sent'] += 1
            self.stats['errors'] += errors
            
            if packets_sent > 0:
                print(f"📤 [OptimizedArtNetSender] Frame envoyée: {packets_sent} paquets en {send_time*1000:.1f}ms")
            
            return errors == 0
            
        except Exception as e:
            print(f"❌ [OptimizedArtNetSender] Erreur générale envoi: {e}")
            self.stats['errors'] += 1
            return False

    def send_dmx_universes_optimized(self, universes: Dict) -> bool:
        """
        🚀 Envoi optimisé avec contrôle FPS et cache intelligent
        """
        if not self.running or not universes:
            return True
        
        current_time = time.time()
        
        # Contrôle de FPS - éviter d'envoyer trop rapidement
        time_since_last_frame = current_time - self.last_frame_time
        if time_since_last_frame < self.frame_time:
            # Attendre pour respecter le FPS cible
            sleep_time = self.frame_time - time_since_last_frame
            time.sleep(sleep_time)
            current_time = time.time()
        
        self.last_frame_time = current_time
        frame_start = current_time
        
        packets_queued = 0
        
        try:
            # Traiter chaque univers modifié
            for universe_key, universe_obj in universes.items():
                if hasattr(universe_obj, 'dmx_data'):
                    dmx_data = bytes(universe_obj.dmx_data)
                    
                    # Extraire les infos de l'univers
                    if isinstance(universe_key, tuple) and len(universe_key) >= 2:
                        controller_ip = universe_key[0]
                        universe_number = universe_key[1]
                    else:
                        continue
                    
                    # Vérifier si on peut skip (cache)
                    if self._should_skip_duplicate(universe_key, dmx_data):
                        continue
                    
                    # Trouver l'adresse du contrôleur
                    controller_addr = None
                    for ip, port in self.controllers:
                        if ip == controller_ip:
                            controller_addr = (ip, port)
                            break
                    
                    if controller_addr:
                        # Créer le paquet ArtNet
                        packet_data = self.create_artnet_packet(universe_number, dmx_data)
                        
                        # Ajouter à la queue asynchrone
                        try:
                            self.send_queue.put_nowait((packet_data, controller_addr))
                            packets_queued += 1
                        except queue.Full:
                            print("⚠️ [OptimizedArtNetSender] Queue pleine - frame perdue")
            
            # Calcul du FPS réel
            frame_time = time.time() - frame_start
            self.frame_times.append(frame_time)
            
            if len(self.frame_times) >= 10:
                avg_frame_time = sum(self.frame_times) / len(self.frame_times)
                if avg_frame_time > 0:
                    self.stats['fps_actual'] = 1.0 / avg_frame_time
            
            # Stats de la queue
            self.stats['queue_size_avg'] = self.send_queue.qsize()
            self.stats['frames_sent'] += 1
            
            # Log périodique des performances
            if self.stats['frames_sent'] % 60 == 0:  # Chaque seconde à 60fps
                self._log_performance()
            
            return True
            
        except Exception as e:
            print(f"❌ [OptimizedArtNetSender] Erreur envoi optimisé: {e}")
            self.stats['errors'] += 1
            return False
    
    def _log_performance(self):
        """Log des performances temps réel"""
        cache_ratio = 0
        total_cache = self.stats['cache_hits'] + self.stats['cache_misses']
        if total_cache > 0:
            cache_ratio = self.stats['cache_hits'] / total_cache * 100
        
        print(f"🔥 [OPTIMIZED] FPS: {self.stats['fps_actual']:.1f}/{self.target_fps} | "
              f"Latence: {self.stats['send_time_avg']*1000:.2f}ms | "
              f"Cache: {cache_ratio:.1f}% | "
              f"Queue: {self.stats['queue_size_avg']} | "
              f"Frames: {self.stats['frames_sent']} | "
              f"Errors: {self.stats['errors']}")
    
    def set_target_fps(self, fps: int):
        """Change le FPS cible en temps réel"""
        self.target_fps = fps
        self.frame_time = 1.0 / fps
        print(f"🎯 [OptimizedArtNetSender] Nouveau FPS: {fps}")
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques de performance"""
        return self.stats.copy()
    
    def close(self):
        """Fermeture propre avec arrêt du thread"""
        self.running = False
        if self.sender_thread and self.sender_thread.is_alive():
            self.sender_thread.join(timeout=1.0)
        if self.socket:
            self.socket.close()
            self.socket = None
        print("🔌 [OptimizedArtNetSender] Fermé proprement")


class EHubOptimizedPipeline:
    """
    🔥 Pipeline optimisé basé sur la version qui marche
    """
    
    def __init__(self, listen_port: int = 8765, target_fps: int = 60):
        print(f"🔥 [EHubOptimizedPipeline] Init optimisé - {target_fps}FPS")
        
        # Utiliser le pipeline DMX qui marche (Étapes 0-3)
        self.dmx_pipeline = EHubDMXPipeline(listen_port)
        
        # Remplacer l'ArtNet sender par la version optimisée
        self.optimized_sender = OptimizedArtNetSender(target_fps)
        
        self.target_fps = target_fps
    
    def initialize(self) -> bool:
        """Initialise le pipeline optimisé"""
        print("🔧 [EHubOptimizedPipeline] Initialisation...")
        
        # Initialiser le pipeline DMX existant
        if not self.dmx_pipeline.initialize():
            return False
        
        # Initialiser le sender optimisé
        if not self.optimized_sender.initialize():
            return False
        
        print("✅ [EHubOptimizedPipeline] Pipeline optimisé prêt")
        return True
    
    def process_ehub_packet_optimized(self, data: bytes) -> bool:
        """Traitement optimisé d'un paquet eHub"""
        try:
            # 1. Créer un message EHubMessage pour le décodeur
            from datetime import datetime
            from ehub_receiver import EHubMessage
            message = EHubMessage(
                data=data,
                sender_ip="172.26.208.1",
                sender_port=61311,
                received_at=datetime.now(),
                size=len(data)
            )
            
            # 2. Décoder avec le pipeline DMX  
            packet = self.dmx_pipeline.decode_ehub_packet(message)
            if not packet:
                return False
                
            print(f"🎯 [EHubOptimizedPipeline] {len(packet.entities)} entités parsées")
                
            # 3. **UTILISER LA MÊME MÉTHODE QUE LE PIPELINE QUI FONCTIONNE**
            # Utiliser EHubDMXPipeline.process_ehub_packet qui prend un EHubPacket
            modified_universes = self.dmx_pipeline.process_ehub_packet(packet)
            
            if not modified_universes:
                return False
                
            # Vérifier si c'est un dictionnaire d'univers DMX
            if isinstance(modified_universes, dict):
                print(f"🎯 [EHubOptimizedPipeline] {len(modified_universes)} univers DMX reçus")
                print(f"📊 [EHubOptimizedPipeline] Envoi ArtNet...")
                
                # 4. **UTILISER LA VRAIE MÉTHODE D'ENVOI QUI FONCTIONNE**
                success = self.optimized_sender.send_dmx_universes(modified_universes)
                
                if success:
                    print(f"✅ [EHubOptimizedPipeline] ArtNet envoyé vers 4 contrôleurs BC216")
                else:
                    print(f"❌ [EHubOptimizedPipeline] Échec envoi ArtNet")
                    
                return success
            else:
                print(f"⚠️ [EHubOptimizedPipeline] Type inattendu: {type(modified_universes)}")
                return False
            
        except Exception as e:
            print(f"❌ [EHubOptimizedPipeline] Erreur traitement: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_optimized(self):
        """Exécute le pipeline en mode optimisé"""
        print(f"🔥 [EHubOptimizedPipeline] DÉMARRAGE OPTIMISÉ à {self.target_fps}FPS")
        print("  Optimisations: Threading asynchrone, Cache intelligent, Contrôle FPS précis")
        print("  Ctrl+C pour arrêter")
        
        try:
            while True:
                # Réception de données Unity - utilise la méthode correcte
                message = self.dmx_pipeline.receiver.receive_message(timeout=1.0)
                if message:
                    # Traitement optimisé complet
                    self.process_ehub_packet_optimized(message.data)
                
        except KeyboardInterrupt:
            print("\n🛑 [EHubOptimizedPipeline] Arrêt demandé")
        finally:
            self.close()
    
    def set_fps(self, fps: int):
        """Change le FPS en temps réel"""
        self.target_fps = fps
        self.optimized_sender.set_target_fps(fps)
        print(f"🎯 [EHubOptimizedPipeline] FPS modifié: {fps}")
    
    def get_performance_report(self) -> Dict:
        """Rapport de performance complet"""
        return {
            'target_fps': self.target_fps,
            'sender_stats': self.optimized_sender.get_stats(),
            'pipeline_status': 'optimized'
        }
    
    def close(self):
        """Fermeture propre"""
        self.optimized_sender.close()
        if hasattr(self.dmx_pipeline, 'close'):
            self.dmx_pipeline.close()
        print("🔌 [EHubOptimizedPipeline] Pipeline fermé")


def main():
    """
    🔥 Main avec contrôle FPS interactif
    """
    print("=" * 60)
    print("🔥 CONTRÔLEUR LED OPTIMISÉ - Version Fluidité Maximale 🔥")
    print("=" * 60)
    
    print("\n🎯 Sélection du FPS cible:")
    print("1. 30 FPS  (économique)")
    print("2. 60 FPS  (fluide)")
    print("3. 90 FPS  (très fluide)")
    print("4. 120 FPS (ultra fluide)")
    print("5. FPS personnalisé")
    
    choice = input("\nVotre choix (1-5): ").strip()
    
    fps_options = {'1': 30, '2': 60, '3': 90, '4': 120}
    
    if choice in fps_options:
        target_fps = fps_options[choice]
    elif choice == '5':
        try:
            target_fps = int(input("Entrez le FPS désiré (10-240): "))
            target_fps = max(10, min(240, target_fps))  # Limiter entre 10 et 240
        except ValueError:
            target_fps = 60
    else:
        target_fps = 60
    
    print(f"\n🎯 FPS sélectionné: {target_fps}")
    
    # Créer le pipeline optimisé
    pipeline = EHubOptimizedPipeline(target_fps=target_fps)
    
    if not pipeline.initialize():
        print("❌ Échec d'initialisation du pipeline optimisé")
        return
    
    print(f"\n🔥 PIPELINE OPTIMISÉ ACTIF")
    print(f"  • FPS cible: {target_fps}")
    print(f"  • Threading asynchrone: ✅")
    print(f"  • Cache intelligent: ✅")
    print(f"  • Contrôle FPS précis: ✅")
    print(f"  • Buffer optimisé: ✅")
    
    try:
        # Lancer en mode optimisé
        pipeline.run_optimized()
        
    except Exception as e:
        print(f"❌ Erreur pipeline: {e}")
    finally:
        pipeline.close()


if __name__ == "__main__":
    main()
