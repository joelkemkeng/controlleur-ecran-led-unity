"""
🔧 Pipeline Monitor - Wrapper pour intégrer les étapes 0-4 existantes
Gère le monitoring en temps réel du pipeline eHub → ArtNet
"""

import sys
import os
import threading
import time
import queue
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

# Ajouter les chemins vers les étapes existantes
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root / "etape-00-reception-ehub"))
sys.path.append(str(project_root / "config-ecran"))
sys.path.append(str(project_root / "etape-02-decodage-ehub"))
sys.path.append(str(project_root / "etape-03-mapping-dmx"))
sys.path.append(str(project_root / "etape-04-send-artnet"))

@dataclass
class MonitoringData:
    """Structure des données de monitoring"""
    timestamp: float
    throughput: float
    latency: float
    error_rate: float
    active_entities: int
    status: str

@dataclass
class PipelineData:
    """📊 Structure de données pour métriques pipeline"""
    timestamp: float
    packets_received: int
    latency_ms: float
    entities_processed: int
    controllers_active: int
    errors_count: int
    pipeline_status: str
    bytes_per_second: int = 0

class PipelineMonitor:
    """
    🔧 Wrapper de monitoring pour le pipeline eHub complet
    Intègre toutes les étapes 0-4 avec monitoring en temps réel
    """
    
    def __init__(self):
        """Initialise le wrapper de monitoring pipeline"""
        try:
            print("🔧 [PipelineMonitor] Initialisation pipeline...")
            
            # Import conditionnel des modules pipeline
            try:
                # Tentative d'import des vraies dépendances
                sys.path.append('/home/joel/projet_ecran/controlleur-ecran-led-unity')
                from network.receiver import EhubReceiver
                from ehub.parser import EhubParser  
                from mapping.entity_mapper import EntityMapper
                from artnet.sender import ArtNetSender
                
                # ✅ Mode production avec vraies dépendances
                self.simulation_mode = False
                self.receiver = EhubReceiver()
                self.parser = EhubParser()
                self.mapper = EntityMapper()
                self.artnet = ArtNetSender()
                print("✅ [PipelineMonitor] Mode production - vraies dépendances")
                
            except ImportError as e:
                # 🧪 Mode simulation si dépendances manquantes
                print(f"⚠️ [PipelineMonitor] Modules pipeline indisponibles: {e}")
                print("🧪 [PipelineMonitor] Basculement en mode simulation")
                self.simulation_mode = True
                self._init_simulation_mode()
            
            # Variables de monitoring
            self.monitoring_active = False
            self.is_running = False  # Ajout de l'attribut manquant
            self.last_statistics = None
            self.data_callback = None
            self.artnet_callback = None  # Callback pour données ArtNet
            self.monitor_thread = None
            self._stop_event = threading.Event()
            
            print("✅ [PipelineMonitor] Initialisé")
            
        except Exception as e:
            print(f"❌ [PipelineMonitor] Erreur initialisation: {e}")
            # Forcer le mode simulation en cas d'erreur
            self.simulation_mode = True
            self.is_running = False
            self.artnet_callback = None
            self._init_simulation_mode()
    
    def _init_simulation_mode(self):
        """🧪 Initialise le mode simulation pour démonstration"""
        self.receiver = None
        self.parser = None
        self.mapper = None
        self.artnet = None
        
        # Variables additionnelles pour compatibilité
        self.ehub_pipeline = None
        self.start_time = None
        self.data_queue = queue.Queue()  # Ajout de l'attribut manquant
        self.current_data = None         # Ajout de l'attribut manquant
        
        # Données simulées
        self.sim_packet_count = 0
        self.sim_start_time = time.time()
        print("🧪 [PipelineMonitor] Mode simulation initialisé")
    
    def _start_simulation_thread(self):
        """🧪 Démarre le thread de simulation de données"""
        self.monitor_thread = threading.Thread(
            target=self._simulation_loop,
            daemon=True,
            name="SimulationMonitor"
        )
        self.monitor_thread.start()
        print("🧪 [PipelineMonitor] Thread de simulation démarré")
    
    def _simulation_loop(self):
        """🧪 Boucle de simulation pour générer des données de test"""
        import random
        import math
        
        while self.is_running:
            try:
                current_time = time.time()
                elapsed = current_time - self.sim_start_time
                
                # Simuler des données variables
                base_packets = 50 + 30 * math.sin(elapsed / 10)  # Oscillation
                packets_received = int(base_packets + random.uniform(-10, 10))
                
                latency_ms = 5 + 2 * math.sin(elapsed / 5) + random.uniform(-1, 1)
                entities_processed = packets_received * 8  # 8 entités par paquet
                controllers_active = 4  # BC216 fixe
                errors_count = random.randint(0, 2) if random.random() < 0.1 else 0
                
                # Créer les données simulées
                sim_data = PipelineData(
                    timestamp=current_time,
                    packets_received=packets_received,
                    latency_ms=latency_ms,
                    entities_processed=entities_processed,
                    controllers_active=controllers_active,
                    errors_count=errors_count,
                    pipeline_status="running",
                    bytes_per_second=packets_received * 512
                )
                
                # Envoyer via callback si disponible
                if self.data_callback:
                    self.data_callback(sim_data)
                
                # Stocker dans la queue pour récupération
                if not self.data_queue.full():
                    self.data_queue.put(sim_data)
                
                # Stocker comme données actuelles
                self.current_data = sim_data
                
                # 📡 Générer des données ArtNet simulées pour l'écran virtuel
                self._generate_simulated_artnet_data(current_time, elapsed)
                
                self.sim_packet_count += packets_received
                time.sleep(1)  # Mise à jour chaque seconde
                
            except Exception as e:
                print(f"❌ [Simulation] Erreur: {e}")
                time.sleep(1)
    
    def _generate_simulated_artnet_data(self, current_time: float, elapsed: float):
        """📡 Génère des données ArtNet simulées pour l'écran virtuel"""
        import random
        import math
        
        try:
            # Générer des données pour les 4 univers (4 BC216)
            for universe in range(4):
                channel_data = []
                
                # Générer 512 canaux de données (128 pixels * 4 canaux RGBW)
                for pixel in range(128):  # 128 pixels par univers
                    # Créer des effets visuels selon l'univers
                    if universe == 0:  # Quadrant haut-gauche - effet ondulé rouge
                        r = int(128 + 127 * math.sin(elapsed + pixel * 0.1))
                        g = int(50 + 50 * math.sin(elapsed * 0.5))
                        b = int(20)
                        w = int(30 + 20 * math.sin(elapsed * 0.3))
                    elif universe == 1:  # Quadrant haut-droite - effet spirale verte
                        r = int(20)
                        g = int(128 + 127 * math.sin(elapsed * 0.8 + pixel * 0.2))
                        b = int(50 + 50 * math.cos(elapsed))
                        w = int(40)
                    elif universe == 2:  # Quadrant bas-gauche - effet bleu pulsant
                        r = int(30 + 30 * math.sin(elapsed * 0.6))
                        g = int(40)
                        b = int(128 + 127 * math.sin(elapsed * 1.2))
                        w = int(50 + 30 * math.cos(elapsed * 0.4))
                    else:  # Quadrant bas-droite - effet multicolore
                        r = int(80 + 75 * math.sin(elapsed + pixel * 0.05))
                        g = int(80 + 75 * math.cos(elapsed * 1.1 + pixel * 0.05))
                        b = int(80 + 75 * math.sin(elapsed * 0.7 + pixel * 0.1))
                        w = int(60 + 40 * math.sin(elapsed * 0.9))
                    
                    # Ajouter un peu de bruit aléatoire
                    r = max(0, min(255, r + random.randint(-10, 10)))
                    g = max(0, min(255, g + random.randint(-10, 10))) 
                    b = max(0, min(255, b + random.randint(-10, 10)))
                    w = max(0, min(255, w + random.randint(-5, 5)))
                    
                    # Ajouter les 4 canaux RGBW
                    channel_data.extend([r, g, b, w])
                
                # Compléter à 512 canaux si nécessaire
                while len(channel_data) < 512:
                    channel_data.append(0)
                
                # Envoyer les données à l'écran virtuel via callback
                if hasattr(self, 'artnet_callback') and self.artnet_callback:
                    self.artnet_callback(universe, channel_data)
                    
        except Exception as e:
            print(f"❌ [Simulation] Erreur génération ArtNet: {e}")
    
    def set_artnet_callback(self, callback):
        """📡 Définit le callback pour les données ArtNet"""
        self.artnet_callback = callback
        print("📡 [PipelineMonitor] Callback ArtNet configuré")
    
    def stop_monitoring(self):
        """⏹ Arrête le monitoring"""
        if not self.is_running:
            print("⚠️ [PipelineMonitor] Monitoring pas en cours")
            return
        
        print("⏹ [PipelineMonitor] Arrêt du monitoring...")
        self.is_running = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            if self.simulation_mode:
                print("🧪 [PipelineMonitor] Arrêt simulation")
            else:
                self._stop_event.set()
            self.monitor_thread.join(timeout=2)
        
        print("✅ [PipelineMonitor] Monitoring arrêté")
    
    def initialize_pipeline(self) -> bool:
        """
        🚀 Initialise le pipeline complet (étapes 0-4)
        """
        try:
            print("🔧 [PipelineMonitor] Initialisation pipeline...")
            
            # Import des modules existants
            self._import_pipeline_modules()
            
            # Initialiser la configuration écran
            if not self._initialize_screen_config():
                return False
            
            # Initialiser le pipeline ArtNet complet
            if not self._initialize_artnet_pipeline():
                return False
            
            print("✅ [PipelineMonitor] Pipeline initialisé avec succès")
            self.current_data.pipeline_status = "Initialisé"
            return True
            
        except Exception as e:
            print(f"❌ [PipelineMonitor] Erreur initialisation: {e}")
            self.current_data.pipeline_status = f"Erreur: {str(e)}"
            return False
    
    def _import_pipeline_modules(self):
        """Import des modules du pipeline existant"""
        try:
            # Import étape 0 - Réception eHub
            global EHubReceiver, EHubMessage
            from ehub_receiver import EHubReceiver, EHubMessage
            
            # Import config écran
            global ScreenConfigLoader
            from screen_loader import ScreenConfigLoader
            
            # Import étape 2 - Décodage
            global EHubDecoder
            from ehub_complete_pipeline_decoder import EHubDecoder
            
            # Import étape 4 - ArtNet complet (contient étapes 3+4)
            global EHubArtNetPipeline
            from ehub_complete_pipeline_send_artnet import EHubArtNetPipeline
            
            print("✅ [PipelineMonitor] Modules importés")
            
        except ImportError as e:
            print(f"❌ [PipelineMonitor] Erreur import modules: {e}")
            raise
    
    def _initialize_screen_config(self) -> bool:
        """Initialise la configuration écran"""
        try:
            self.screen_config = ScreenConfigLoader()
            if not self.screen_config.load_config():
                print("❌ [PipelineMonitor] Échec chargement config écran")
                return False
            
            print(f"✅ [PipelineMonitor] Config écran: {len(self.screen_config.mappings)} mappings")
            return True
            
        except Exception as e:
            print(f"❌ [PipelineMonitor] Erreur config écran: {e}")
            return False
    
    def _initialize_artnet_pipeline(self) -> bool:
        """Initialise le pipeline ArtNet complet"""
        try:
            self.ehub_pipeline = EHubArtNetPipeline(listen_port=self.port)
            
            if not self.ehub_pipeline.initialize():
                print("❌ [PipelineMonitor] Échec initialisation pipeline ArtNet")
                return False
            
            print("✅ [PipelineMonitor] Pipeline ArtNet initialisé")
            return True
            
        except Exception as e:
            print(f"❌ [PipelineMonitor] Erreur pipeline ArtNet: {e}")
            return False
    
    def start_monitoring(self) -> bool:
        """
        ▶ Démarre le monitoring temps réel
        """
        if self.is_running:
            print("⚠️ [PipelineMonitor] Monitoring déjà en cours")
            return False
        
        # 🧪 Mode simulation si pipeline indisponible
        if self.simulation_mode:
            print("🧪 [PipelineMonitor] Démarrage en mode simulation")
            self.is_running = True
            self.start_time = datetime.now()
            self._start_simulation_thread()
            return True
        
        if not self.ehub_pipeline:
            if not self.initialize_pipeline():
                return False
        
        try:
            self.is_running = True
            self.start_time = datetime.now()
            
            # Démarrer le thread de monitoring
            self.monitor_thread = threading.Thread(
                target=self._monitoring_loop, 
                daemon=True,
                name="PipelineMonitor"
            )
            self.monitor_thread.start()
            
            print("▶ [PipelineMonitor] Monitoring démarré")
            self.current_data.pipeline_status = "En cours"
            return True
            
        except Exception as e:
            print(f"❌ [PipelineMonitor] Erreur démarrage: {e}")
            self.is_running = False
            return False
    
    def stop_monitoring(self):
        """
        ⏸ Arrête le monitoring
        """
        if not self.is_running:
            return
        
        print("⏸ [PipelineMonitor] Arrêt du monitoring...")
        self.is_running = False
        
        # Arrêter le pipeline
        if self.ehub_pipeline:
            self.ehub_pipeline.stop()
        
        # Attendre l'arrêt du thread
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
        
        self.current_data.pipeline_status = "Arrêté"
        print("⏹ [PipelineMonitor] Monitoring arrêté")
    
    def _monitoring_loop(self):
        """
        🔄 Boucle principale de monitoring non-bloquante
        """
        print("🔄 [PipelineMonitor] Boucle de monitoring démarrée")
        
        last_update_time = time.time()
        packets_last_second = 0
        bytes_last_second = 0
        
        # Variables pour le monitoring passif
        last_stats_check = time.time()
        
        while self.is_running:
            try:
                current_time = time.time()
                
                # Traiter les commandes de l'UI
                self._process_ui_commands()
                
                # Mode monitoring passif : surveiller les stats du pipeline
                if current_time - last_stats_check >= 0.5:  # Vérifier toutes les 500ms
                    pipeline_stats = self._get_pipeline_statistics()
                    if pipeline_stats:
                        packets_last_second += pipeline_stats.get('new_packets', 0)
                        bytes_last_second += pipeline_stats.get('new_bytes', 0)
                    last_stats_check = current_time
                
                # Calculer métriques chaque seconde
                if current_time - last_update_time >= 1.0:
                    self._update_monitoring_metrics(
                        current_time - last_update_time,
                        packets_last_second,
                        bytes_last_second
                    )
                    
                    # Envoyer les données à l'UI
                    self._send_data_to_ui()
                    
                    # Reset compteurs
                    packets_last_second = 0
                    bytes_last_second = 0
                    last_update_time = current_time
                
                # Pause courte pour éviter 100% CPU
                time.sleep(0.1)  # 100ms - monitoring relaxé
                
            except Exception as e:
                print(f"❌ [PipelineMonitor] Erreur monitoring: {e}")
                self.total_errors += 1
                time.sleep(0.5)  # Pause plus longue en cas d'erreur
    
    def _get_pipeline_statistics(self) -> Optional[Dict[str, Any]]:
        """Récupère les statistiques du pipeline de manière non-invasive"""
        try:
            # Si le pipeline a des stats intégrées, les utiliser
            if hasattr(self.ehub_pipeline, 'get_statistics'):
                return self.ehub_pipeline.get_statistics()
            
            # Sinon, estimation basée sur l'activité observée
            return {
                'new_packets': 1 if self.is_running else 0,  # Simulation
                'new_bytes': 2048 if self.is_running else 0,  # Simulation
                'total_entities': self.total_entities
            }
            
        except Exception:
            return None
    
    def _receive_ehub_message(self) -> Optional[Any]:
        """Reçoit un message eHub via le pipeline"""
        try:
            if self.ehub_pipeline and hasattr(self.ehub_pipeline, 'ehub_receiver'):
                # Utiliser la structure correcte du pipeline ArtNet
                message_data = self.ehub_pipeline.ehub_receiver.receive_message(timeout=0.1)
                if message_data:
                    return message_data
            return None
        except Exception as e:
            # Log seulement les vraies erreurs, pas les timeouts
            if "timeout" not in str(e).lower():
                print(f"⚠️ [PipelineMonitor] Erreur réception: {e}")
            return None
    
    def _process_ehub_message(self, message) -> bool:
        """Traite un message eHub via le pipeline"""
        try:
            start_time = time.time()
            
            # Traiter le message via le pipeline complet
            if hasattr(self.ehub_pipeline, 'run_single_iteration'):
                # Utiliser la méthode d'itération unique si disponible
                result = self.ehub_pipeline.run_single_iteration()
            else:
                # Fallback sur le traitement manuel
                result = self._manual_process_message(message)
            
            if result:
                # Calculer la latence
                latency_ms = (time.time() - start_time) * 1000
                self.current_data.latency_ms = latency_ms
                
                # Incrémenter les entités (estimation basée sur le type de message)
                estimated_entities = self._estimate_entities_from_message(message)
                self.total_entities += estimated_entities
                
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ [PipelineMonitor] Erreur traitement message: {e}")
            return False
    
    def _manual_process_message(self, message) -> bool:
        """Traitement manuel d'un message si pas d'itération unique"""
        try:
            # Simuler le traitement pour le monitoring
            # En réalité, le pipeline fonctionne déjà en arrière-plan
            return True
        except Exception:
            return False
    
    def _estimate_entities_from_message(self, message) -> int:
        """Estime le nombre d'entités dans un message"""
        try:
            if hasattr(message, 'data') and message.data:
                # Estimation basée sur la taille du message
                # Messages typiques : ~2KB pour 86 entités, ~2.7KB pour 1706 entités  
                size_kb = len(message.data) / 1024
                if size_kb < 1.0:
                    return int(size_kb * 86)  # Petits messages
                else:
                    return int(size_kb * 600)  # Messages plus gros
            return 0
        except Exception:
            return 0
    
    def _update_monitoring_metrics(self, time_delta: float, packets: int, bytes_count: int):
        """Met à jour les métriques de monitoring"""
        # Taux de paquets et bytes par seconde
        self.current_data.packets_received = int(packets / time_delta)
        self.current_data.bytes_per_second = bytes_count / time_delta
        
        # Contrôleurs actifs (simulation basée sur la config)
        if self.screen_config:
            self.current_data.controllers_active = len(self.screen_config.controllers)
        
        # Entités traitées
        self.current_data.entities_processed = self.total_entities
        
        # Erreurs
        self.current_data.errors_count = self.total_errors
        
        # Timestamp
        self.current_data.timestamp = datetime.now()
        
        # Status
        if self.is_running:
            self.current_data.pipeline_status = "Actif"
    
    def _send_data_to_ui(self):
        """Envoie les données de monitoring à l'UI"""
        try:
            self.data_queue.put_nowait(self.current_data)
        except queue.Full:
            # Queue pleine, supprimer l'ancien
            try:
                self.data_queue.get_nowait()
                self.data_queue.put_nowait(self.current_data)
            except queue.Empty:
                pass
    
    def _process_ui_commands(self):
        """Traite les commandes reçues de l'UI"""
        try:
            while True:
                command = self.command_queue.get_nowait()
                self._handle_ui_command(command)
        except queue.Empty:
            pass
    
    def _handle_ui_command(self, command: Dict[str, Any]):
        """Gère une commande de l'UI"""
        action = command.get("action")
        
        if action == "reset_stats":
            self._reset_statistics()
        elif action == "pause":
            # Pause temporaire (sera implémentée plus tard)
            pass
        elif action == "test_pipeline":
            self._test_pipeline()
        
        print(f"🎛️ [PipelineMonitor] Commande traitée: {action}")
    
    def _reset_statistics(self):
        """Reset les statistiques"""
        self.total_packets = 0
        self.total_entities = 0
        self.total_errors = 0
        self.start_time = datetime.now()
        print("↻ [PipelineMonitor] Statistiques remises à zéro")
    
    def _test_pipeline(self):
        """Test rapide du pipeline"""
        # Test basique de connectivité
        if self.ehub_pipeline:
            print("◉ [PipelineMonitor] Test pipeline en cours...")
            # Le test sera implémenté plus tard
    
    def get_current_data(self) -> Optional[MonitoringData]:
        """Récupère les données de monitoring actuelles"""
        try:
            return self.data_queue.get_nowait()
        except queue.Empty:
            return None
    
    def send_command(self, command: Dict[str, Any]):
        """Envoie une commande au pipeline"""
        try:
            self.command_queue.put_nowait(command)
        except queue.Full:
            print("⚠️ [PipelineMonitor] Queue de commandes pleine")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques complètes"""
        uptime = datetime.now() - self.start_time if self.start_time else datetime.now() - datetime.now()
        
        return {
            "uptime_seconds": uptime.total_seconds(),
            "total_packets": self.total_packets,
            "total_entities": self.total_entities,
            "total_errors": self.total_errors,
            "error_rate": self.total_errors / max(self.total_packets, 1) * 100,
            "pipeline_status": self.current_data.pipeline_status,
            "is_running": self.is_running
        }