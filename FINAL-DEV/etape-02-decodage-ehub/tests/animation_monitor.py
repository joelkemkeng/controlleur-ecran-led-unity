#!/usr/bin/env python3
"""
🎬 MONITEUR ANIMATION eHUB - Mode Continu
Observe SEULEMENT les changements de valeurs RGBW en temps réel
"""

import sys
import os
import time
from collections import defaultdict

# Ajouter les chemins
sys.path.append('/home/joel/projet_ecran/controlleur-ecran-led-unity/FINAL-DEV/etape-02-decodage-ehub')

from ehub_complete_pipeline_decoder import EHubDecoder

class AnimationMonitor:
    """
    Moniteur d'animation focalisé sur les changements RGBW
    """
    
    def __init__(self, port=8765, max_entities=10):
        self.port = port
        self.max_entities = max_entities
        self.entity_history = defaultdict(lambda: {"r": None, "g": None, "b": None, "w": None})
        self.monitored_entities = set()
        self.packets_received = 0
        self.start_time = time.time()
        self.last_stats_time = time.time()
        
    def run(self):
        """
        Lance le monitoring continu
        """
        print("🎬 === MONITEUR ANIMATION eHUB ===")
        print()
        print("🚀 Initialisation décodeur...")
        
        decoder = EHubDecoder(port=self.port, verbose=False)  # Mode silencieux
        
        if not decoder.initialize():
            print("❌ Échec initialisation")
            return False
        
        print("✅ Décodeur initialisé")
        print()
        print("🎯 MODE ANIMATION CONTINUE")
        print("💡 Lancez Unity et démarrez une animation")
        print("🔍 Seuls les changements de valeurs RGBW s'afficheront")
        print("🛑 Appuyez Ctrl+C pour arrêter")
        print("=" * 60)
        print()
        
        try:
            while True:
                message = decoder.receiver.receive_message(timeout=0.5)
                
                if message:
                    self.packets_received += 1
                    
                    # Décodage silencieux du paquet
                    packet = self._decode_silently(decoder, message)
                    
                    if packet and packet.entities:
                        self._monitor_changes(packet.entities)
                        
                    # Stats périodiques
                    self._show_periodic_stats()
                        
                else:
                    # Timeout
                    self._show_waiting_message()
        
        except KeyboardInterrupt:
            print("\n🛑 Arrêt demandé par utilisateur")
        
        finally:
            decoder.stop()
        
        self._show_final_stats()
        return self.packets_received > 0
    
    def _decode_silently(self, decoder, message):
        """
        Décode un paquet sans affichage
        """
        try:
            # Extraction header silencieuse
            header_data = message.data[:10]
            
            if len(header_data) < 10:
                return None
                
            import struct
            signature = header_data[:4]
            if signature != b'eHuB':
                return None
                
            packet_type, universe, entity_count, payload_size = struct.unpack('>BBHH', header_data[4:10])
            
            # Extraction et décompression payload
            payload_data = message.data[10:10+payload_size]
            
            if len(payload_data) != payload_size:
                return None
                
            import gzip
            decompressed_data = gzip.decompress(payload_data)
            
            # Parsing entités silencieux
            entities = []
            entity_size = 6  # 2 bytes ID + 4 bytes RGBW
            
            for i in range(0, len(decompressed_data), entity_size):
                if i + entity_size <= len(decompressed_data):
                    entity_data = decompressed_data[i:i+entity_size]
                    entity_id, r, g, b, w = struct.unpack('>HBBBB', entity_data)
                    
                    # Créer un objet entité simple
                    entity = type('Entity', (), {
                        'entity_id': entity_id,
                        'red': r,
                        'green': g, 
                        'blue': b,
                        'white': w
                    })()
                    
                    entities.append(entity)
            
            # Créer un objet paquet simple
            packet = type('Packet', (), {
                'packet_type': packet_type,
                'universe': universe,
                'entities': entities
            })()
            
            return packet
            
        except Exception:
            return None
    
    def _monitor_changes(self, entities):
        """
        Surveille les changements dans les entités
        """
        # Ajouter nouvelles entités à surveiller
        for entity in entities:
            if len(self.monitored_entities) < self.max_entities:
                self.monitored_entities.add(entity.entity_id)
        
        # Analyser changements pour entités surveillées
        changes_detected = False
        
        for entity in entities:
            if entity.entity_id in self.monitored_entities:
                eid = entity.entity_id
                prev = self.entity_history[eid]
                
                # Vérifier changements
                changed = False
                if prev["r"] != entity.red:
                    changed = True
                elif prev["g"] != entity.green:
                    changed = True
                elif prev["b"] != entity.blue:
                    changed = True
                elif prev["w"] != entity.white:
                    changed = True
                
                if changed or prev["r"] is None:
                    changes_detected = True
                    self._show_entity_change(entity, prev)
                    
                    # Mettre à jour l'historique
                    self.entity_history[eid]["r"] = entity.red
                    self.entity_history[eid]["g"] = entity.green
                    self.entity_history[eid]["b"] = entity.blue
                    self.entity_history[eid]["w"] = entity.white
    
    def _show_entity_change(self, entity, prev):
        """
        Affiche un changement d'entité
        """
        eid = entity.entity_id
        
        if prev["r"] is not None:
            # Changement détecté
            print(f"🔄 Entité {eid:5}: ", end="")
            
            # Rouge
            if prev["r"] != entity.red:
                print(f"R:{prev['r']:3}→{entity.red:3} ", end="")
            else:
                print(f"R:{entity.red:3}     ", end="")
            
            # Vert
            if prev["g"] != entity.green:
                print(f"G:{prev['g']:3}→{entity.green:3} ", end="")
            else:
                print(f"G:{entity.green:3}     ", end="")
            
            # Bleu
            if prev["b"] != entity.blue:
                print(f"B:{prev['b']:3}→{entity.blue:3} ", end="")
            else:
                print(f"B:{entity.blue:3}     ", end="")
            
            # Blanc
            if prev["w"] != entity.white:
                print(f"W:{prev['w']:3}→{entity.white:3}")
            else:
                print(f"W:{entity.white:3}")
        
        else:
            # Première valeur détectée
            print(f"🆕 Entité {eid:5}: R:{entity.red:3} G:{entity.green:3} B:{entity.blue:3} W:{entity.white:3}")
    
    def _show_periodic_stats(self):
        """
        Affiche les stats périodiquement
        """
        current_time = time.time()
        if current_time - self.last_stats_time >= 5.0:  # Toutes les 5 secondes
            elapsed = current_time - self.start_time
            pps = self.packets_received / elapsed if elapsed > 0 else 0
            
            print(f"📊 {self.packets_received} paquets reçus | {pps:.1f} pps | {len(self.monitored_entities)} entités surveillées")
            self.last_stats_time = current_time
    
    def _show_waiting_message(self):
        """
        Affiche un message d'attente
        """
        current_time = time.time()
        if current_time - self.last_stats_time >= 8.0:
            print("⏳ En attente de données Unity... (vérifiez la connexion)")
            self.last_stats_time = current_time
    
    def _show_final_stats(self):
        """
        Affiche les statistiques finales
        """
        elapsed = time.time() - self.start_time
        pps = self.packets_received / elapsed if elapsed > 0 else 0
        
        print("\n" + "=" * 60)
        print(f"📊 RÉSUMÉ FINAL:")
        print(f"⏱️  Durée: {elapsed:.1f} secondes")
        print(f"📦 Paquets reçus: {self.packets_received}")
        print(f"📊 Débit moyen: {pps:.1f} paquets/seconde")
        print(f"🎯 Entités surveillées: {len(self.monitored_entities)}")
        
        if self.monitored_entities:
            print(f"🔢 IDs surveillés: {sorted(list(self.monitored_entities))}")

if __name__ == "__main__":
    print("🎬 MONITEUR ANIMATION eHUB EN TEMPS RÉEL")
    print("=" * 60)
    print()
    
    print("🎯 Mode: Analyse continue des changements RGBW uniquement")
    print("🔇 Décodage silencieux pour performance optimale")
    print("🔍 Affichage: Seulement les entités qui changent")
    print()
    
    try:
        monitor = AnimationMonitor(port=8765, max_entities=15)
        monitor.run()
    
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé")
    
    print("\n✅ Monitoring terminé")
