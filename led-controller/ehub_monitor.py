#!/usr/bin/env python3
"""
Module de monitoring eHub simple
Récepteur eHub avec affichage des données en temps réel
"""

import socket
import time
import sys
from datetime import datetime
from typing import List
from core.ehub import get_entities_list

class EHubMonitor:
    """Moniteur eHub avec affichage en temps réel"""
    
    def __init__(self, listen_ip: str = "127.0.0.1", listen_port: int = 8765):
        self.listen_ip = listen_ip
        self.listen_port = listen_port
        self.socket = None
        self.running = False
        self.stats = {
            "packets_received": 0,
            "entities_total": 0,
            "errors": 0,
            "start_time": None,
            "last_packet_time": 0,
            "packets_per_second": 0,
            "entities_per_second": 0
        }
        self.packet_times = []
        
    def start_monitoring(self):
        """Démarre le monitoring eHub"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind((self.listen_ip, self.listen_port))
            self.socket.settimeout(1.0)  # Timeout pour permettre l'arrêt propre
            
            self.running = True
            self.stats["start_time"] = time.time()
            
            self.print_header()
            
            while self.running:
                try:
                    data, addr = self.socket.recvfrom(64 * 1024)
                    self.process_packet(data, addr)
                    
                except socket.timeout:
                    # Mettre à jour les stats périodiquement même sans paquet
                    self.update_stats()
                    continue
                except Exception as e:
                    self.stats["errors"] += 1
                    print(f"\n❌ Erreur réception: {e}")
                    
        except Exception as e:
            print(f"💥 Erreur critique: {e}")
        finally:
            self.cleanup()
    
    def print_header(self):
        """Affiche l'en-tête du monitoring"""
        print("=" * 80)
        print("🎧 MONITEUR eHub ACTIF")
        print(f"📡 Écoute: {self.listen_ip}:{self.listen_port}")
        print(f"🕐 Démarré: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 80)
        print("⌨️  Appuyez sur Ctrl+C pour arrêter")
        print("-" * 80)
    
    def process_packet(self, data: bytes, addr: tuple):
        """Traite un paquet eHub reçu"""
        try:
            current_time = time.time()
            self.stats["packets_received"] += 1
            self.stats["last_packet_time"] = current_time
            self.packet_times.append(current_time)
            
            # Garder seulement les 100 derniers temps de paquets
            if len(self.packet_times) > 100:
                self.packet_times = self.packet_times[-100:]
            
            # Décoder le paquet
            entities_list = get_entities_list(data)
            self.stats["entities_total"] += len(entities_list)
            
            # Affichage en temps réel
            timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
            
            print(f"\n📦 [{timestamp}] Paquet #{self.stats['packets_received']}")
            print(f"   👤 Expéditeur: {addr[0]}:{addr[1]}")
            print(f"   📏 Taille: {len(data)} bytes")
            print(f"   🔢 Entités: {len(entities_list)}")
            
            # Afficher quelques entités colorées
            if entities_list:
                print("   🎨 Entités reçues:")
                for i, entity in enumerate(entities_list[:10]):  # Limiter à 10
                    entity_id, r, g, b, w = entity
                    color_bar = self.get_color_bar(r, g, b)
                    print(f"      #{entity_id:4d}: {color_bar} R:{r:3d} G:{g:3d} B:{b:3d}", end="")
                    if w > 0:
                        print(f" W:{w:3d}", end="")
                    print()
                
                if len(entities_list) > 10:
                    print(f"      ... et {len(entities_list) - 10} autres entités")
            
            # Mettre à jour et afficher les stats
            self.update_stats()
            self.print_live_stats()
            
        except Exception as e:
            self.stats["errors"] += 1
            print(f"❌ Erreur traitement paquet: {e}")
    
    def get_color_bar(self, r: int, g: int, b: int) -> str:
        """Créé une barre de couleur visuelle"""
        # Créer une représentation colorée simple
        if r > 200 and g < 50 and b < 50:
            return "🟥"  # Rouge
        elif g > 200 and r < 50 and b < 50:
            return "🟩"  # Vert
        elif b > 200 and r < 50 and g < 50:
            return "🟦"  # Bleu
        elif r > 150 and g > 150 and b < 50:
            return "🟨"  # Jaune
        elif r > 150 and b > 150 and g < 50:
            return "🟪"  # Magenta
        elif g > 150 and b > 150 and r < 50:
            return "🟦"  # Cyan-ish
        elif r > 100 and g > 100 and b > 100:
            return "⬜"  # Blanc-ish
        else:
            return "⬛"  # Noir/sombre
    
    def update_stats(self):
        """Met à jour les statistiques"""
        current_time = time.time()
        elapsed = current_time - self.stats["start_time"] if self.stats["start_time"] else 0
        
        # Calculer les débits
        if elapsed > 0:
            self.stats["packets_per_second"] = self.stats["packets_received"] / elapsed
            self.stats["entities_per_second"] = self.stats["entities_total"] / elapsed
        
        # FPS basé sur les dernières secondes
        recent_packets = [t for t in self.packet_times if current_time - t <= 1.0]
        self.stats["fps"] = len(recent_packets)
    
    def print_live_stats(self):
        """Affiche les statistiques en temps réel"""
        elapsed = time.time() - self.stats["start_time"] if self.stats["start_time"] else 0
        
        print(f"   📊 Stats: {self.stats['packets_received']} pkt | {self.stats['entities_total']} ent | "
              f"{self.stats['fps']} FPS | {elapsed:.1f}s")
        
        # Stats complètes tous les 10 paquets
        if self.stats["packets_received"] % 10 == 0:
            print("\n" + "="*60)
            print("📊 STATISTIQUES DÉTAILLÉES")
            print(f"   ⏱️  Durée: {elapsed:.1f}s")
            print(f"   📦 Paquets: {self.stats['packets_received']}")
            print(f"   🔢 Entités: {self.stats['entities_total']}")
            print(f"   ❌ Erreurs: {self.stats['errors']}")
            print(f"   📈 Débit paquets: {self.stats['packets_per_second']:.1f} pkt/s")
            print(f"   📈 Débit entités: {self.stats['entities_per_second']:.1f} ent/s")
            print(f"   🎯 FPS actuel: {self.stats['fps']}")
            print("="*60)
    
    def stop(self):
        """Arrête le monitoring"""
        self.running = False
        print("\n🛑 Arrêt du monitoring demandé...")
    
    def cleanup(self):
        """Nettoie les ressources"""
        if self.socket:
            self.socket.close()
        
        print("\n" + "="*80)
        print("📋 RAPPORT FINAL")
        elapsed = time.time() - self.stats["start_time"] if self.stats["start_time"] else 0
        print(f"⏱️  Durée totale: {elapsed:.1f}s")
        print(f"📦 Paquets reçus: {self.stats['packets_received']}")
        print(f"🔢 Entités totales: {self.stats['entities_total']}")
        print(f"❌ Erreurs: {self.stats['errors']}")
        if elapsed > 0:
            print(f"📈 Débit moyen: {self.stats['packets_received']/elapsed:.1f} pkt/s")
            print(f"📈 Entités/s moyen: {self.stats['entities_total']/elapsed:.1f} ent/s")
        print("="*80)
        print("👋 Moniteur eHub arrêté")

def main():
    """Fonction principale"""
    print("🚀 Moniteur eHub - Réception et affichage en temps réel")
    
    # Paramètres par défaut
    listen_ip = "127.0.0.1"
    listen_port = 8765
    
    # Parser les arguments de ligne de commande
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help"]:
            print("\nUsage:")
            print(f"  python {sys.argv[0]} [port] [ip]")
            print(f"  python {sys.argv[0]} 9999              # Écouter sur port 9999")
            print(f"  python {sys.argv[0]} 8765 192.168.1.1  # Écouter sur IP spécifique")
            print("\nDéfaut: 127.0.0.1:8765")
            return
        
        try:
            listen_port = int(sys.argv[1])
        except ValueError:
            print(f"❌ Port invalide: {sys.argv[1]}")
            return
    
    if len(sys.argv) > 2:
        listen_ip = sys.argv[2]
    
    monitor = EHubMonitor(listen_ip, listen_port)
    
    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\n⌨️  Interruption clavier détectée")
        monitor.stop()
    except Exception as e:
        print(f"\n💥 Erreur inattendue: {e}")

if __name__ == "__main__":
    main()
