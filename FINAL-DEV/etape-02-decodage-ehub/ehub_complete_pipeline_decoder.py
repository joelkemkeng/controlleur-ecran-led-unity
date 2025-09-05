#!/usr/bin/env python3
"""
🔬 ÉTAPE 2 : Décodage Messages eHub
Module de décodage des messages eHub reçus de Unity
Intègre: Réception UDP + Config Écran + Décodage eHub
"""

import gzip
import struct
from dataclasses import dataclass
from typing import List, Optional, Dict
import sys
import os

# Ajouter les chemins pour intégrer les étapes précédentes (Windows compatible)
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(os.path.join(project_root, 'etape-00-reception-ehub'))
sys.path.append(os.path.join(project_root, 'config-ecran'))

from ehub_receiver import EHubReceiver, EHubMessage
from screen_loader import ScreenConfigLoader, LEDMapping

@dataclass
class EHubEntity:
    """
    Représente une entité eHub décodée (une LED)
    """
    entity_id: int      # ID entité (ex: 100)
    red: int           # Rouge 0-255
    green: int         # Vert 0-255
    blue: int          # Bleu 0-255
    white: int         # Blanc 0-255

@dataclass
class EHubPacket:
    """
    Représente un paquet eHub décodé selon spécification officielle
    """
    signature: str          # "eHuB"
    packet_type: int       # Type: 2=update, 1=config
    entity_count: int      # Nombre d'entités déclarées
    universe: int          # Univers eHuB adressé
    entities: List[EHubEntity]  # Liste des entités décodées

class EHubDecoder:
    """
    Décodeur de messages eHub
    Intègre réception UDP, config écran et décodage
    """
    
    def __init__(self, port: int = 8765):
        self.port = port
        self.receiver: Optional[EHubReceiver] = None
        self.screen_config: Optional[ScreenConfigLoader] = None
        self.total_packets = 0
        self.total_entities = 0
        self.decode_errors = 0
        
        print(f"🔬 [EHubDecoder] Initialisation décodeur eHub")
        print(f"📡 [EHubDecoder] Port: {port}")
    
    def initialize(self) -> bool:
        """
        Initialise le récepteur et la configuration écran
        Retourne True si succès, False sinon
        """
        print(f"🚀 [EHubDecoder] Initialisation complète...")
        
        # 1. Initialiser le récepteur UDP
        print(f"📡 [EHubDecoder] Étape 1: Initialisation récepteur UDP...")
        self.receiver = EHubReceiver(port=self.port)
        if not self.receiver.start_listening():
            print(f"❌ [EHubDecoder] Échec initialisation récepteur")
            return False
        print(f"✅ [EHubDecoder] Récepteur UDP opérationnel")
        
        # 2. Charger la configuration écran
        print(f"🗺️  [EHubDecoder] Étape 2: Chargement configuration écran...")
        self.screen_config = ScreenConfigLoader()
        if not self.screen_config.load_config():
            print(f"❌ [EHubDecoder] Échec chargement configuration écran")
            return False
        print(f"✅ [EHubDecoder] Configuration écran chargée ({len(self.screen_config.mappings)} mappings)")
        
        print(f"🎉 [EHubDecoder] Initialisation complète réussie!")
        return True
    
    def decode_ehub_header(self, data: bytes) -> Optional[Dict]:
        """
        Décode le header eHub selon la spécification officielle
        Format: "eHuB" + type(1) + universe(1) + entity_count(2) + payload_size(2) = 10 bytes
        """
        try:
            if len(data) < 10:
                print(f"⚠️  [EHubDecoder] Données trop courtes pour header: {len(data)} bytes")
                return None
            
            # Vérification signature
            signature = data[0:4].decode('ascii', errors='ignore')
            if signature != "eHuB":
                print(f"⚠️  [EHubDecoder] Signature invalide: {signature}")
                return None
            
            # Décodage header selon spécification officielle
            packet_type = data[4]        # 2=update, 1=config
            universe = data[5]           # Numéro univers eHuB
            entity_count = struct.unpack('<H', data[6:8])[0]    # Nombre d'entités
            payload_size = struct.unpack('<H', data[8:10])[0]   # Taille payload compressé
            
            header = {
                'signature': signature,
                'packet_type': packet_type,
                'universe': universe,
                'entity_count': entity_count,
                'payload_size': payload_size,
                'header_size': 10
            }
            
            print(f"📋 [EHubDecoder] Header décodé: {signature} type={packet_type} u={universe} entities={entity_count} payload={payload_size}")
            return header
            
        except Exception as e:
            print(f"❌ [EHubDecoder] Erreur décodage header: {e}")
            return None
    
    def decompress_payload(self, compressed_data: bytes) -> Optional[bytes]:
        """
        Décompresse le payload GZip
        """
        try:
            print(f"🗜️  [EHubDecoder] Décompression payload ({len(compressed_data)} bytes)...")
            
            decompressed = gzip.decompress(compressed_data)
            
            print(f"✅ [EHubDecoder] Décompression réussie: {len(compressed_data)} → {len(decompressed)} bytes")
            return decompressed
            
        except Exception as e:
            print(f"❌ [EHubDecoder] Erreur décompression: {e}")
            return None
    
    def parse_entities(self, decompressed_data: bytes) -> List[EHubEntity]:
        """
        Parse les entités selon la spécification officielle eHuB
        Format: [entity_id(2) + r(1) + g(1) + b(1) + w(1)] = 6 bytes par entité
        """
        entities = []
        
        try:
            print(f"🔍 [EHubDecoder] Parsing entités depuis {len(decompressed_data)} bytes...")
            
            # Chaque entité = 6 bytes selon spécification (ID=2 + RGBW=4)
            entity_size = 6
            entity_count = len(decompressed_data) // entity_size
            
            print(f"📊 [EHubDecoder] Nombre d'entités théorique: {entity_count}")
            
            for i in range(entity_count):
                offset = i * entity_size
                
                if offset + entity_size > len(decompressed_data):
                    break
                
                # Extraction des bytes
                entity_bytes = decompressed_data[offset:offset + entity_size]
                
                # Décodage selon spécification officielle (2 bytes ID + 4 bytes RGBW)
                entity_id = struct.unpack('<H', entity_bytes[0:2])[0]  # unsigned short
                red = entity_bytes[2]    # R
                green = entity_bytes[3]  # V (Vert)
                blue = entity_bytes[4]   # B
                white = entity_bytes[5]  # W
                
                entity = EHubEntity(
                    entity_id=entity_id,
                    red=red,
                    green=green,
                    blue=blue,
                    white=white
                )
                
                entities.append(entity)
                
                # Debug pour les premières entités
                if i < 5:
                    print(f"   🔸 Entité {entity_id}: R={red} G={green} B={blue} W={white}")
            
            print(f"✅ [EHubDecoder] {len(entities)} entités parsées")
            return entities
            
        except Exception as e:
            print(f"❌ [EHubDecoder] Erreur parsing entités: {e}")
            return []
    
    def decode_ehub_packet(self, message: EHubMessage) -> Optional[EHubPacket]:
        """
        Décode un message eHub complet
        """
        print(f"🔬 [EHubDecoder] Décodage message eHub ({len(message.data)} bytes)...")
        
        # 1. Décodage header
        header = self.decode_ehub_header(message.data)
        if not header:
            self.decode_errors += 1
            return None
        
        # 2. Extraction payload compressé
        payload_start = header['header_size']
        compressed_payload = message.data[payload_start:]
        
        print(f"📦 [EHubDecoder] Payload compressé: {len(compressed_payload)} bytes")
        
        # 3. Décompression
        decompressed_data = self.decompress_payload(compressed_payload)
        if not decompressed_data:
            self.decode_errors += 1
            return None
        
        # 4. Parsing entités
        entities = self.parse_entities(decompressed_data)
        
        # 5. Création paquet final
        packet = EHubPacket(
            signature=header['signature'],
            packet_type=header['packet_type'],
            entity_count=header['entity_count'],
            universe=header['universe'],
            entities=entities
        )
        
        # Stats
        self.total_packets += 1
        self.total_entities += len(entities)
        
        print(f"✅ [EHubDecoder] Paquet décodé: {len(entities)} entités")
        return packet
    
    def get_led_mapping(self, entity_id: int) -> Optional[LEDMapping]:
        """
        Obtient le mapping LED pour une entité
        """
        if not self.screen_config:
            return None
        
        return self.screen_config.get_mapping_for_entity(entity_id)
    
    def process_packet(self, packet: EHubPacket):
        """
        Traite un paquet décodé (mapping vers DMX)
        """
        print(f"🔄 [EHubDecoder] Traitement paquet avec {len(packet.entities)} entités...")
        
        mapped_count = 0
        unmapped_count = 0
        
        for entity in packet.entities[:5]:  # Limite pour debug
            mapping = self.get_led_mapping(entity.entity_id)
            
            if mapping:
                mapped_count += 1
                print(f"   🗺️  Entité {entity.entity_id}: RGB({entity.red},{entity.green},{entity.blue}) → {mapping.controller_ip}:u{mapping.universe}:ch{mapping.channel}")
            else:
                unmapped_count += 1
                if unmapped_count <= 3:  # Limite les messages d'erreur
                    print(f"   ⚠️  Entité {entity.entity_id}: Pas de mapping trouvé")
        
        total_mapped = sum(1 for entity in packet.entities if self.get_led_mapping(entity.entity_id))
        total_unmapped = len(packet.entities) - total_mapped
        
        print(f"📊 [EHubDecoder] Résultat: {total_mapped} mappées, {total_unmapped} non mappées")
    
    def listen_and_decode(self, packet_limit: Optional[int] = None):
        """
        Écoute continue et décodage des messages
        """
        if not self.receiver:
            print(f"❌ [EHubDecoder] Récepteur non initialisé")
            return
        
        print(f"🔄 [EHubDecoder] Démarrage écoute et décodage...")
        print(f"💡 [EHubDecoder] Appuyez Ctrl+C pour arrêter")
        
        packets_processed = 0
        
        try:
            while True:
                # Réception message
                message = self.receiver.receive_message(timeout=1.0)
                
                if message:
                    # Décodage
                    packet = self.decode_ehub_packet(message)
                    
                    if packet:
                        # Traitement
                        self.process_packet(packet)
                        packets_processed += 1
                        
                        # Stats périodiques
                        if packets_processed % 10 == 0:
                            self.print_stats()
                        
                        # Limite optionnelle
                        if packet_limit and packets_processed >= packet_limit:
                            print(f"🏁 [EHubDecoder] Limite de {packet_limit} paquets atteinte")
                            break
                
        except KeyboardInterrupt:
            print(f"\n🛑 [EHubDecoder] Arrêt demandé par utilisateur")
        except Exception as e:
            print(f"❌ [EHubDecoder] Erreur inattendue: {e}")
        finally:
            self.stop()
    
    def print_stats(self):
        """
        Affiche les statistiques de décodage
        """
        avg_entities = self.total_entities / self.total_packets if self.total_packets > 0 else 0
        error_rate = (self.decode_errors / (self.total_packets + self.decode_errors)) * 100 if (self.total_packets + self.decode_errors) > 0 else 0
        
        print(f"📊 [EHubDecoder] === STATISTIQUES ===")
        print(f"📊 [EHubDecoder] Paquets décodés: {self.total_packets}")
        print(f"📊 [EHubDecoder] Entités totales: {self.total_entities}")
        print(f"📊 [EHubDecoder] Moyenne entités/paquet: {avg_entities:.1f}")
        print(f"📊 [EHubDecoder] Erreurs décodage: {self.decode_errors} ({error_rate:.1f}%)")
        print(f"📊 [EHubDecoder] ====================")
    
    def stop(self):
        """
        Arrête le décodeur proprement
        """
        print(f"🔌 [EHubDecoder] Arrêt du décodeur...")
        
        if self.receiver:
            self.receiver.stop()
        
        # Stats finales
        self.print_stats()

# Test si exécuté directement
if __name__ == "__main__":
    print("🚀 [PIPELINE] Pipeline complet eHub - Réception ➜ Décodage ➜ Analyse")
    print("📡 Mode continu - Appuyez Ctrl+C pour arrêter")
    print("=" * 60)
    
    # Création décodeur
    decoder = EHubDecoder(port=8765)
    
    # Initialisation
    if decoder.initialize():
        print("✅ [PIPELINE] Pipeline initialisé avec succès")
        print("🎯 En attente des données Unity...")
        print("🔍 Les paquets décodés s'afficheront ci-dessous")
        print("-" * 60)
        
        try:
            # Écoute et décodage en continu (sans limite)
            decoder.listen_and_decode()  # Pas de packet_limit = mode continu
        except KeyboardInterrupt:
            print("\n🛑 Arrêt demandé par l'utilisateur...")
        finally:
            decoder.stop()
    else:
        print("❌ [PIPELINE] Échec initialisation pipeline")
