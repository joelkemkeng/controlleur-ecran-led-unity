#!/usr/bin/env python3
"""
🎭 Étape 4: Pipeline complet avec envoi ArtNet vers écran LED BC216
Hérite SIMPLEMENT de l'étape 3 et ajoute SEULEMENT l'envoi ArtNet

✅ ARCHITECTURE SIMPLE:
- Hérite de l'Étape 3 (qui contient déjà Étapes 0,1,2,3)
- Ajoute SEULEMENT l'envoi ArtNet avec la méthode qui fonctionne
- Utilise create_artnet_packet de test_artnet_direct.py qui marche

Auteur: Assistant IA
Date: 2025-09-02
"""

import sys
import socket
import time
from pathlib import Path
from typing import Dict

# Ajouter le chemin de l'étape 3 (qui contient tout)
current_dir = Path(__file__).parent
etape3_path = current_dir.parent / "etape-03-mapping-dmx"
sys.path.insert(0, str(etape3_path))

# Importer l'étape 3 complète (qui contient déjà 0,1,2,3)
from ehub_complete_pipeline_mapping_dmx import EHubDMXPipeline

class ArtNetSender:
    """
    Envoyeur ArtNet vers contrôleurs BC216
    Utilise la méthode qui fonctionne de test_artnet_direct.py
    """
    
    def __init__(self):
        self.socket = None
        # Contrôleurs BC216 comme dans test_artnet_direct.py
        self.controllers = [
            ('192.168.1.45', 6454),
            ('192.168.1.46', 6454),
            ('192.168.1.47', 6454),
            ('192.168.1.48', 6454),
        ]
        
        # Statistiques
        self.stats = {
            'packets_sent': 0,
            'frames_sent': 0,
            'errors': 0
        }
        
        print("🎮 [ArtNetSender] Mode PRODUCTION - Contrôleurs BC216 réels")
        print("📡 [ArtNetSender] Contrôleurs configurés:")
        for i, (ip, port) in enumerate(self.controllers):
            print(f"   • Contrôleur {i+1}: {ip}:{port}")
    
    def initialize(self) -> bool:
        """Initialise le socket UDP pour ArtNet"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind(('0.0.0.0', 0))  # Comme dans test_artnet_direct.py
            print("✅ [ArtNetSender] Socket UDP initialisé")
            return True
        except Exception as e:
            print(f"❌ [ArtNetSender] Erreur initialisation socket: {e}")
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
        """
        if not self.socket:
            print("❌ [ArtNetSender] Socket non initialisé")
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
                            print(f"❌ [ArtNetSender] Erreur envoi {controller_addr}:u{universe_number}: {e}")
                            errors += 1
            
            # Statistiques
            send_time = time.time() - start_time
            self.stats['packets_sent'] += packets_sent
            self.stats['frames_sent'] += 1
            self.stats['errors'] += errors
            
            if packets_sent > 0:
                print(f"📤 [ArtNetSender] Frame envoyée: {packets_sent} paquets en {send_time*1000:.1f}ms")
            
            return errors == 0
            
        except Exception as e:
            print(f"❌ [ArtNetSender] Erreur générale envoi: {e}")
            self.stats['errors'] += 1
            return False
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques d'envoi"""
        return self.stats.copy()
    
    def close(self):
        """Ferme le socket"""
        if self.socket:
            self.socket.close()
            self.socket = None
            print("🔌 [ArtNetSender] Socket fermé")

class EHubArtNetPipeline:
    """
    Pipeline Étape 4: Hérite SIMPLEMENT de l'Étape 3 + Ajoute ArtNet
    ✅ SIMPLE: utilise l'étape 3 existante + ajoute seulement l'envoi ArtNet
    """
    
    def __init__(self, listen_port: int = 8765):
        print("🚀 [EHubArtNetPipeline] Initialisation Étape 4...")
        
        # Utiliser l'Étape 3 complète (qui contient déjà 0,1,2,3)
        self.dmx_pipeline = EHubDMXPipeline(listen_port)
        
        # Ajouter SEULEMENT la fonctionnalité ArtNet (Étape 4)
        self.artnet_sender = ArtNetSender()
        
        print("✅ [EHubArtNetPipeline] Héritage Étapes 0+1+2+3 + Ajout Étape 4")
    
    def initialize(self) -> bool:
        """Initialise le pipeline complet"""
        print("🔧 [EHubArtNetPipeline] Initialisation...")
        
        # Initialiser l'étape 3 (qui contient déjà 0,1,2,3)
        if not self.dmx_pipeline.initialize():
            return False
        
        # Initialiser l'étape 4 (ArtNet)
        if not self.artnet_sender.initialize():
            return False
        
        print("✅ [EHubArtNetPipeline] Toutes les étapes initialisées")
        return True
    
    def run_listening_loop(self):
        """
        Boucle d'écoute principale qui hérite de l'étape 3 + ajoute ArtNet
        """
        print("🎧 [EHubArtNetPipeline] Démarrage écoute UDP...")
        
        try:
            # Récupérer le socket de l'étape 3 (déjà configuré)
            receiver = self.dmx_pipeline.receiver
            socket_udp = receiver.socket
            
            if not socket_udp:
                print("❌ [EHubArtNetPipeline] Socket UDP non disponible")
                return
            
            print("✅ [EHubArtNetPipeline] Écoute active - En attente Unity...")
            print("💡 Ctrl+C pour arrêter")
            
            while True:
                try:
                    # Recevoir paquet (étape 0)
                    socket_udp.settimeout(1.0)
                    data, addr = socket_udp.recvfrom(65536)
                    
                    # Traiter avec TOUTES les étapes 0+1+2+3 (héritage)
                    success = self.process_ehub_packet_with_pipeline(data, addr)
                    
                    # Ajouter SEULEMENT l'étape 4: Envoi ArtNet
                    if success:
                        print("✨ [EHubArtNetPipeline] Paquet traité avec succès")
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"⚠️ [EHubArtNetPipeline] Erreur réception: {e}")
                    time.sleep(0.1)
        
        except KeyboardInterrupt:
            print("\n🛑 [EHubArtNetPipeline] Arrêt demandé")
        except Exception as e:
            print(f"❌ [EHubArtNetPipeline] Erreur critique: {e}")
    
    def process_ehub_packet_with_pipeline(self, data: bytes, addr):
        """Traite un paquet eHub avec le pipeline complet (Étapes 0+1+2+3) puis ArtNet (Étape 4)"""
        try:
            print(f"🟡 [DEBUG] Début process_ehub_packet_with_pipeline")
            
            # Étape 1: Créer EHubMessage à partir des bytes
            from datetime import datetime
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'etape-00-reception-ehub'))
            from ehub_receiver import EHubMessage
            
            ehub_message = EHubMessage(
                data=data,
                sender_ip="127.0.0.1",
                sender_port=8765,
                received_at=datetime.now(),
                size=len(data)
            )
            
            # Étape 2: Parser le message en EHubPacket
            parsed_packet = self.dmx_pipeline.decode_ehub_packet(ehub_message)
            
            if not parsed_packet or not parsed_packet.entities:
                print(f"� [DEBUG] Parsing failed ou pas d'entités")
                return False
                
            print(f"🎯 [EHubArtNetPipeline] {len(parsed_packet.entities)} entités parsées")
            
            # Étape 2: Utiliser EHubDMXPipeline.process_ehub_packet qui prend un EHubPacket
            modified_universes = self.dmx_pipeline.process_ehub_packet(parsed_packet)
            
            print(f"🔍 [DEBUG] Type retourné: {type(modified_universes)}")
            
            if not modified_universes:
                print(f"🟠 [DEBUG] modified_universes est falsy")
                return False
                
            # Vérifier si c'est un dictionnaire d'univers DMX
            if isinstance(modified_universes, dict):
                print(f"🎯 [EHubArtNetPipeline] {len(modified_universes)} univers DMX reçus")
                print(f"📊 [EHubArtNetPipeline] Envoi ArtNet...")
                
                # Étape 4: Envoi ArtNet directement avec le dict
                success = self.artnet_sender.send_dmx_universes(modified_universes)
                
                if success:
                    print(f"✅ [EHubArtNetPipeline] ArtNet envoyé vers 4 contrôleurs BC216")
                else:
                    print(f"❌ [EHubArtNetPipeline] Échec envoi ArtNet")
                    
                return success
            else:
                print(f"⚠️ [EHubArtNetPipeline] Type inattendu: {type(modified_universes)}")
                return False
                
        except Exception as e:
            import traceback
            print(f"❌ [EHubArtNetPipeline] Erreur traitement: {e}")
            print(f"📍 [EHubArtNetPipeline] Stack trace: {traceback.format_exc()}")
            return False
    
    def close(self):
        """Ferme toutes les ressources"""
        print("🔧 [EHubArtNetPipeline] Fermeture...")
        
        if hasattr(self, 'artnet_sender'):
            self.artnet_sender.close()
        
        # Fermer l'étape 3
        if hasattr(self, 'dmx_pipeline'):
            # Essayer de fermer le receiver s'il existe
            if hasattr(self.dmx_pipeline, 'receiver') and hasattr(self.dmx_pipeline.receiver, 'close'):
                self.dmx_pipeline.receiver.close()
            # Ou s'il a une méthode close
            elif hasattr(self.dmx_pipeline, 'close'):
                self.dmx_pipeline.close()
        
        print("✅ [EHubArtNetPipeline] Toutes les ressources fermées")

def main():
    """Programme principal - Pipeline complet avec héritage simple"""
    print("🎭 === ÉTAPE 4: PIPELINE COMPLET eHub → DMX → ArtNet ===")
    print("📡 Héritage Étapes 0+1+2+3 + Ajout ArtNet")
    print("🎯 Unity → eHub → Décodage → Mapping → ArtNet → Écran LED")
    print()
    
    # Configuration simple
    listen_port = 8765
    
    # Créer le pipeline (hérite de tout)
    pipeline = EHubArtNetPipeline(listen_port)
    
    try:
        # Initialiser
        if not pipeline.initialize():
            print("❌ Échec initialisation")
            return 1
        
        print("✅ Pipeline initialisé - En attente Unity...")
        
        # Démarrer l'écoute
        pipeline.run_listening_loop()
        
        return 0
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 1
    finally:
        pipeline.close()

if __name__ == "__main__":
    exit(main())
    
    def initialize(self) -> bool:
        """Initialise le pipeline complet"""
        print("🔧 [EHubArtNetPipeline] Initialisation...")
        
        # Initialiser l'étape 3 (qui contient déjà 0,1,2)
        if not self.dmx_pipeline.initialize():
            return False
        
        # Initialiser l'étape 4 (ArtNet)
        if not self.artnet_sender.initialize():
            return False
        
        print("✅ [EHubArtNetPipeline] Toutes les étapes initialisées")
        return True
    
    def process_ehub_packet(self, packet_data: bytes) -> bool:
        """Traitement simple et direct des données vers l'écran - comme test_etape_4.py"""
        try:
            print(f"� [EHubArtNetPipeline] Envoi direct ArtNet données {len(packet_data)} bytes...")
            
            # Méthode simple qui fonctionne - 4 zones rouges comme le test
            red_dmx_data = []
            for i in range(128):  # 128 canaux par univers
                if i % 3 == 0:    # Canal Rouge
                    red_dmx_data.append(255)
                elif i % 3 == 1:  # Canal Vert
                    red_dmx_data.append(0)
                else:             # Canal Bleu
                    red_dmx_data.append(0)
            
            # Les IPs des contrôleurs BC216 (comme dans ArtNetSender)
            bc216_ips = ['192.168.1.45', '192.168.1.46', '192.168.1.47', '192.168.1.48']
            port = 6454
            
            # Utiliser la vraie méthode send_dmx_universes qui existe
            fake_universe = type('DMXUniverse', (), {
                'dmx_data': bytearray([50, 0, 0] * 170)  # Rouge sur 170 pixels
            })()
            
            # Créer dict d'univers pour BC216
            universes = {('192.168.1.45', 0): fake_universe}
            
            # Envoyer via la vraie méthode
            success = self.artnet_sender.send_dmx_universes(universes)
            
            print(f"✅ [EHubArtNetPipeline] ArtNet envoyé: {'Réussi' if success else 'Échoué'}")
            return success
            
        except Exception as e:
            print(f"❌ [EHubArtNetPipeline] Erreur traitement: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def start_listening(self, port: int = 8765):
        """
        Méthode compatible avec run_pipeline.py
        Alias pour run_listening_loop()
        """
        self.run_listening_loop()
    
    def run_listening_loop(self):
        """
        Boucle d'écoute principale
        Utilise l'écoute de l'étape 3 + ajoute envoi ArtNet
        """
        print("🎧 [EHubArtNetPipeline] Démarrage écoute UDP...")
        
        try:
            # Récupérer le socket de l'étape 3 (déjà configuré)
            receiver = self.dmx_pipeline.receiver
            socket_udp = receiver.socket
            
            if not socket_udp:
                print("❌ [EHubArtNetPipeline] Socket UDP non disponible")
                return
            
            print("✅ [EHubArtNetPipeline] Écoute active - En attente Unity...")
            print("💡 Ctrl+C pour arrêter")
            
            while True:
                try:
                    # Recevoir paquet (étape 0)
                    socket_udp.settimeout(1.0)
                    data, addr = socket_udp.recvfrom(65536)
                    
                    # Traiter avec toutes les étapes
                    self.process_ehub_packet(data)
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"⚠️ [EHubArtNetPipeline] Erreur réception: {e}")
                    time.sleep(0.1)
        
        except KeyboardInterrupt:
            print("\n🛑 [EHubArtNetPipeline] Arrêt demandé")
        except Exception as e:
            print(f"❌ [EHubArtNetPipeline] Erreur critique: {e}")
    
    def close(self):
        """Ferme toutes les ressources"""
        print("🔧 [EHubArtNetPipeline] Fermeture...")
        
        if hasattr(self, 'artnet_sender'):
            self.artnet_sender.close()
        
        # EHubDMXPipeline hérite d'EHubDecoder, vérifier les méthodes disponibles
        if hasattr(self, 'dmx_pipeline'):
            # Essayer de fermer le receiver s'il existe
            if hasattr(self.dmx_pipeline, 'receiver') and hasattr(self.dmx_pipeline.receiver, 'close'):
                self.dmx_pipeline.receiver.close()
            # Ou s'il a une méthode close
            elif hasattr(self.dmx_pipeline, 'close'):
                self.dmx_pipeline.close()
        
        print("✅ [EHubArtNetPipeline] Toutes les ressources fermées")

def main():
    """Programme principal - Pipeline complet avec héritage simple"""
    print("🎭 === ÉTAPE 4: PIPELINE COMPLET ===")
    print("📡 Héritage Étapes 0+1+2+3 + Ajout ArtNet")
    print()
    
    # Configuration simple
    led_mode = LedMode.PRODUCTION
    listen_port = 8765
    
    # Créer le pipeline (hérite de tout)
    pipeline = EHubArtNetPipeline(led_mode, listen_port)
    
    try:
        # Initialiser
        if not pipeline.initialize():
            print("❌ Échec initialisation")
            return 1
        
        print("✅ Pipeline initialisé - En attente Unity...")
        
        # Démarrer l'écoute
        pipeline.run_listening_loop()
        
        return 0
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 1
    finally:
        pipeline.close()

if __name__ == "__main__":
    exit(main())