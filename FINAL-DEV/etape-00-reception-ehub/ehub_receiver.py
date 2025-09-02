#!/usr/bin/env python3
"""
🌐 ÉTAPE 0 : Réception Messages eHub
Module de réception UDP des messages eHub depuis Unity
Version améliorée avec debug et gestion d'erreurs robuste
"""

import socket
import subprocess
import time
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class EHubMessage:
    """
    Représente un message eHub reçu
    """
    data: bytes
    sender_ip: str
    sender_port: int
    received_at: datetime
    size: int

class EHubReceiver:
    """
    Récepteur UDP pour messages eHub depuis Unity
    Simple, robuste et bien documenté
    """
    
    def __init__(self, port: int = 8765, bind_ip: str = "0.0.0.0"):
        self.port = port
        self.bind_ip = bind_ip
        self.socket: Optional[socket.socket] = None
        self.is_running = False
        self.message_count = 0
        self.total_bytes = 0
        
        print(f"🌐 [EHubReceiver] Initialisation récepteur eHub")
        print(f"📡 [EHubReceiver] Port: {port}, IP: {bind_ip}")
    
    def get_wsl_ip(self) -> str:
        """
        Récupère l'IP WSL pour info utilisateur
        """
        try:
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
            wsl_ip = result.stdout.strip().split()[0]
            print(f"🔍 [EHubReceiver] IP WSL détectée: {wsl_ip}")
            return wsl_ip
        except Exception as e:
            print(f"⚠️  [EHubReceiver] Impossible de détecter IP WSL: {e}")
            return "IP_NON_DETECTEE"
    
    def start_listening(self) -> bool:
        """
        Démarre l'écoute UDP
        Retourne True si succès, False sinon
        """
        try:
            print(f"🚀 [EHubReceiver] Démarrage du récepteur...")
            
            # Création socket UDP
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Permet réutilisation adresse (évite erreur "Address already in use")
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind sur l'adresse et port
            self.socket.bind((self.bind_ip, self.port))
            
            print(f"✅ [EHubReceiver] Socket créé et bindé avec succès")
            print(f"👂 [EHubReceiver] Écoute sur {self.bind_ip}:{self.port}")
            
            # Affichage info pour Unity
            wsl_ip = self.get_wsl_ip()
            print(f"📋 [EHubReceiver] ===== CONFIGURATION UNITY =====")
            print(f"📋 [EHubReceiver] IP cible Unity: {wsl_ip}")
            print(f"📋 [EHubReceiver] Port cible Unity: {self.port}")
            print(f"📋 [EHubReceiver] ===============================")
            
            self.is_running = True
            return True
            
        except OSError as e:
            if e.errno == 98:  # Address already in use
                print(f"❌ [EHubReceiver] ERREUR: Port {self.port} déjà utilisé")
                print(f"💡 [EHubReceiver] Solution: Arrêtez l'autre processus ou changez de port")
                return False
            else:
                print(f"❌ [EHubReceiver] ERREUR socket: {e}")
                return False
        except Exception as e:
            print(f"❌ [EHubReceiver] ERREUR inattendue: {e}")
            return False
    
    def receive_message(self, timeout: float = 1.0) -> Optional[EHubMessage]:
        """
        Reçoit un message eHub avec timeout
        Retourne EHubMessage si reçu, None si timeout
        """
        if not self.socket or not self.is_running:
            return None
        
        try:
            # Timeout pour éviter blocage infini
            self.socket.settimeout(timeout)
            
            # Réception données
            data, addr = self.socket.recvfrom(64 * 1024)  # Buffer 64KB
            
            # Statistiques
            self.message_count += 1
            self.total_bytes += len(data)
            
            # Création objet message
            message = EHubMessage(
                data=data,
                sender_ip=addr[0],
                sender_port=addr[1],
                received_at=datetime.now(),
                size=len(data)
            )
            
            # Debug info
            print(f"📨 [EHubReceiver] Message #{self.message_count}")
            print(f"   📍 Source: {message.sender_ip}:{message.sender_port}")
            print(f"   📏 Taille: {message.size} bytes")
            print(f"   🕐 Reçu: {message.received_at.strftime('%H:%M:%S.%f')[:-3]}")
            
            # Aperçu données (premiers 50 bytes)
            data_preview = message.data[:50]
            print(f"   🔍 Données: {data_preview}{'...' if len(message.data) > 50 else ''}")
            
            return message
            
        except socket.timeout:
            # Timeout normal, pas d'erreur
            return None
        except Exception as e:
            print(f"⚠️  [EHubReceiver] Erreur réception: {e}")
            return None
    
    def listen_continuous(self, callback=None):
        """
        Écoute continue avec callback optionnel
        """
        print(f"🔄 [EHubReceiver] Démarrage écoute continue...")
        print(f"💡 [EHubReceiver] Appuyez Ctrl+C pour arrêter")
        
        try:
            while self.is_running:
                message = self.receive_message(timeout=1.0)
                
                if message:
                    # Callback personnalisé si fourni
                    if callback:
                        try:
                            callback(message)
                        except Exception as e:
                            print(f"⚠️  [EHubReceiver] Erreur callback: {e}")
                    
                    # Affichage stats périodique
                    if self.message_count % 10 == 0:
                        self.print_stats()
                
        except KeyboardInterrupt:
            print(f"\n🛑 [EHubReceiver] Arrêt demandé par utilisateur")
        except Exception as e:
            print(f"❌ [EHubReceiver] Erreur écoute: {e}")
        finally:
            self.stop()
    
    def print_stats(self):
        """
        Affiche les statistiques de réception
        """
        avg_size = self.total_bytes / self.message_count if self.message_count > 0 else 0
        print(f"📊 [EHubReceiver] Stats: {self.message_count} messages, {self.total_bytes} bytes total, {avg_size:.1f} bytes/msg")
    
    def stop(self):
        """
        Arrête le récepteur proprement
        """
        print(f"🔌 [EHubReceiver] Arrêt du récepteur...")
        
        self.is_running = False
        
        if self.socket:
            try:
                self.socket.close()
                print(f"✅ [EHubReceiver] Socket fermé")
            except Exception as e:
                print(f"⚠️  [EHubReceiver] Erreur fermeture socket: {e}")
        
        # Stats finales
        if self.message_count > 0:
            print(f"📊 [EHubReceiver] === STATISTIQUES FINALES ===")
            print(f"📊 [EHubReceiver] Messages reçus: {self.message_count}")
            print(f"📊 [EHubReceiver] Bytes totaux: {self.total_bytes}")
            print(f"📊 [EHubReceiver] Taille moyenne: {self.total_bytes/self.message_count:.1f} bytes")
            print(f"📊 [EHubReceiver] =============================")
        else:
            print(f"📊 [EHubReceiver] Aucun message reçu")

# Fonction callback d'exemple
def simple_message_handler(message: EHubMessage):
    """
    Exemple de traitement simple d'un message eHub
    """
    print(f"🔄 [Handler] Traitement message de {message.sender_ip}")
    
    # Ici on pourrait ajouter:
    # - Décodage du header eHub
    # - Décompression GZip
    # - Extraction des entités
    # - Mapping vers DMX
    # - Envoi ArtNet

# Test si exécuté directement
if __name__ == "__main__":
    print("🧪 [TEST] Test du récepteur eHub")
    
    # Création récepteur
    receiver = EHubReceiver(port=8765)
    
    # Démarrage
    if receiver.start_listening():
        print("✅ [TEST] Récepteur démarré avec succès")
        
        # Écoute continue avec handler simple
        receiver.listen_continuous(callback=simple_message_handler)
    else:
        print("❌ [TEST] Échec démarrage récepteur")
