#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface PyQt pour le contrôleur LED
Interface Bento Box moderne avec panneau de contrôle latéral
"""

import sys
import os
import json
import threading
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QSpinBox, QLineEdit, QTextEdit,
    QFileDialog, QMessageBox, QTabWidget, QGroupBox, QGridLayout,
    QSlider, QCheckBox, QProgressBar, QSplitter, QFrame, QScrollArea,
    QSizePolicy, QStackedWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap, QPainter, QPen, QIcon
from collections import deque
import math

# Import du backend et des nouveaux modules
import core.artnet as artnet
import core.ehub as ehub
import core.ehub_sender as ehub_sender
import core.excel as excel
from core.animation import AnimationEngine
from core.router_manager import RouterManager
from ui.visualization_panel import VisualizationPanel
from ui.router_config_panel import RouterConfigPanel
from ui.pong_panel import PongPanel
from ui.snake_panel import SnakePanel
from ui.tetris_panel import TetrisPanel
from ui.dmx_mapping_panel import DMXMappingPanel
import numpy as np

class BentoCard(QFrame):
    """Carte bento box pour une section de l'interface"""
    
    def __init__(self, title: str, description: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        self.description = description
        self.setup_ui()
        
    def setup_ui(self):
        """Configure l'apparence de la carte"""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 2px solid #404040;
                border-radius: 12px;
                padding: 16px;
                margin: 8px;
            }
            QFrame:hover {
                border-color: #606060;
                background-color: #333333;
            }
        """)
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(300, 200)
        
        layout = QVBoxLayout(self)
        
        # Titre
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-weight: bold;
                font-size: 16px;
                padding: 4px;
                margin-bottom: 8px;
            }
        """)
        layout.addWidget(title_label)
        
        # Description
        if self.description:
            desc_label = QLabel(self.description)
            desc_label.setStyleSheet("""
                QLabel {
                    color: #b0b0b0;
                    font-size: 12px;
                    padding: 4px;
                    margin-bottom: 12px;
                }
            """)
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
        
        # Contenu spécifique
        self.content_widget = self.create_content()
        if self.content_widget:
            layout.addWidget(self.content_widget)
        
        layout.addStretch()
    
    def create_content(self) -> QWidget:
        """Crée le contenu spécifique de la carte - à surcharger"""
        return None

class EHubCard(BentoCard):
    """Carte de configuration eHub"""
    
    def __init__(self, parent=None):
        self.port = 8765
        self.universe = 1
        self.is_listening = False
        super().__init__("eHub Receiver", "Configuration de la réception eHub", parent)
        
    def create_content(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Configuration
        config_group = QGroupBox("Configuration")
        config_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
            }
        """)
        config_layout = QVBoxLayout(config_group)
        
        # Port
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1000, 65535)
        self.port_spin.setValue(self.port)
        port_layout.addWidget(self.port_spin)
        config_layout.addLayout(port_layout)
        
        # Universe
        universe_layout = QHBoxLayout()
        universe_layout.addWidget(QLabel("Universe:"))
        self.universe_spin = QSpinBox()
        self.universe_spin.setRange(0, 255)
        self.universe_spin.setValue(self.universe)
        universe_layout.addWidget(self.universe_spin)
        config_layout.addLayout(universe_layout)
        
        layout.addWidget(config_group)
        
        return widget
    
    def get_config(self) -> Dict:
        return {
            "port": self.port_spin.value(),
            "universe": self.universe_spin.value(),
            "is_listening": self.is_listening
        }

class ExcelCard(BentoCard):
    """Carte de configuration Excel"""
    
    def __init__(self, parent=None):
        self.file_path = ""
        super().__init__("Excel Config", "Configuration du mapping LED", parent)
        
    def create_content(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Sélection de fichier
        file_group = QGroupBox("Fichier de configuration")
        file_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
            }
        """)
        file_layout = QVBoxLayout(file_group)
        
        self.file_btn = QPushButton("Sélectionner fichier Excel")
        self.file_btn.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_btn)
        
        self.path_label = QLabel("Aucun fichier sélectionné")
        self.path_label.setWordWrap(True)
        self.path_label.setStyleSheet("color: #868e96; font-size: 11px; padding: 8px;")
        file_layout.addWidget(self.path_label)
        
        layout.addWidget(file_group)
        
        # Status
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        self.status_label = QLabel("Non chargé")
        self.status_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        layout.addLayout(status_layout)
        
        return widget
    
    def select_file(self):
        """Sélectionne un fichier Excel"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner fichier Excel", "", "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            self.file_path = file_path
            self.path_label.setText(os.path.basename(file_path))
            self.status_label.setText("Fichier sélectionné")
            self.status_label.setStyleSheet("color: #51cf66; font-weight: bold;")
            
            # Charger la configuration
            if hasattr(self.parent(), 'parent') and hasattr(self.parent().parent(), 'load_excel_config'):
                self.parent().parent().load_excel_config(file_path)
    
    def get_config(self) -> Dict:
        return {"file_path": self.file_path}

class ArtNetCard(BentoCard):
    """Carte de configuration Art-Net"""
    
    def __init__(self, parent=None):
        self.ip = "127.0.0.1"
        self.universe = 0
        self.is_sending = False
        super().__init__("Art-Net Sender", "Configuration de l'envoi Art-Net", parent)
        
    def create_content(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Configuration
        config_group = QGroupBox("Configuration")
        config_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
            }
        """)
        config_layout = QVBoxLayout(config_group)
        
        # IP
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(QLabel("IP:"))
        self.ip_edit = QLineEdit(self.ip)
        ip_layout.addWidget(self.ip_edit)
        config_layout.addLayout(ip_layout)
        
        # Universe
        universe_layout = QHBoxLayout()
        universe_layout.addWidget(QLabel("Universe:"))
        self.universe_spin = QSpinBox()
        self.universe_spin.setRange(0, 255)
        self.universe_spin.setValue(self.universe)
        universe_layout.addWidget(self.universe_spin)
        config_layout.addLayout(universe_layout)
        
        layout.addWidget(config_group)
        
        # Status
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        self.status_label = QLabel("Prêt")
        self.status_label.setStyleSheet("color: #51cf66; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        layout.addLayout(status_layout)
        
        return widget
    
    def get_config(self) -> Dict:
        return {
            "ip": self.ip_edit.text(),
            "universe": self.universe_spin.value(),
            "is_sending": self.is_sending
        }

class RealTimeChart(QWidget):
    """Widget de graphique en temps réel"""
    
    def __init__(self, title: str, max_points: int = 100, parent=None):
        super().__init__(parent)
        self.title = title
        self.max_points = max_points
        self.data = deque(maxlen=max_points)
        self.timestamps = deque(maxlen=max_points)
        self.min_value = 0
        self.max_value = 100
        self.auto_scale = True
        
        self.setMinimumHeight(150)
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border: 1px solid #404040;
                border-radius: 6px;
            }
        """)
    
    def add_data_point(self, value: float, timestamp: float = None):
        """Ajoute un point de données au graphique"""
        if timestamp is None:
            timestamp = time.time()
        
        self.data.append(value)
        self.timestamps.append(timestamp)
        
        if self.auto_scale and len(self.data) > 1:
            self.min_value = min(self.data) * 0.9
            self.max_value = max(self.data) * 1.1
        
        self.update()
    
    def set_scale(self, min_val: float, max_val: float):
        """Définit l'échelle manuelle"""
        self.min_value = min_val
        self.max_value = max_val
        self.auto_scale = False
        self.update()
    
    def paintEvent(self, event):
        """Dessine le graphique"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fond
        painter.fillRect(self.rect(), QColor(26, 26, 26))
        
        if len(self.data) < 2:
            # Pas assez de données
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "En attente de données...")
            return
        
        # Dimensions du graphique
        margin = 40
        chart_rect = self.rect().adjusted(margin, 20, -10, -30)
        
        # Titre
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(10, 15, self.title)
        
        # Grille
        painter.setPen(QPen(QColor(64, 64, 64), 1))
        for i in range(5):
            y = chart_rect.top() + (chart_rect.height() * i / 4)
            painter.drawLine(chart_rect.left(), y, chart_rect.right(), y)
        
        # Axe Y - valeurs
        painter.setFont(QFont("Arial", 8))
        for i in range(5):
            value = self.max_value - (self.max_value - self.min_value) * i / 4
            y = chart_rect.top() + (chart_rect.height() * i / 4)
            painter.drawText(5, y + 5, f"{value:.1f}")
        
        # Ligne du graphique
        if len(self.data) > 1:
            painter.setPen(QPen(QColor(0, 255, 0), 2))
            
            points = []
            for i, (value, timestamp) in enumerate(zip(self.data, self.timestamps)):
                x = chart_rect.left() + (chart_rect.width() * i / (len(self.data) - 1))
                y = chart_rect.bottom() - ((value - self.min_value) / (self.max_value - self.min_value)) * chart_rect.height()
                points.append((x, y))
            
            for i in range(len(points) - 1):
                painter.drawLine(int(points[i][0]), int(points[i][1]), 
                               int(points[i+1][0]), int(points[i+1][1]))
        
        # Valeur actuelle
        if self.data:
            current_value = self.data[-1]
            painter.setPen(QPen(QColor(255, 255, 0), 1))
            painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            painter.drawText(chart_rect.right() - 60, chart_rect.top() + 15, f"{current_value:.1f}")

class EHubMonitorCard(BentoCard):
    """Carte de monitoring eHub avec graphiques en temps réel"""
    
    def __init__(self, parent=None):
        super().__init__("Moniteur eHub", "Suivi graphique des messages eHub en temps réel", parent)
        self.monitoring_active = False
        self.packet_count = 0
        self.entity_count = 0
        self.error_count = 0
        self.last_packet_time = 0
        self.packet_times = deque(maxlen=100)
        
        # Timer pour les mises à jour
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_charts)
        self.update_timer.start(100)  # 10 FPS pour les graphiques
    
    def create_content(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Contrôles
        controls_layout = QHBoxLayout()
        
        self.monitor_toggle = QPushButton("Activer le moniteur")
        self.monitor_toggle.setCheckable(True)
        self.monitor_toggle.clicked.connect(self.toggle_monitoring)
        self.monitor_toggle.setStyleSheet("""
            QPushButton {
                background-color: #2d5a2d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:checked {
                background-color: #4a7c4a;
            }
            QPushButton:hover {
                background-color: #3a6a3a;
            }
        """)
        controls_layout.addWidget(self.monitor_toggle)
        
        self.clear_btn = QPushButton("Effacer")
        self.clear_btn.clicked.connect(self.clear_data)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #5a2d2d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6a3a3a;
            }
        """)
        controls_layout.addWidget(self.clear_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Statistiques en temps réel
        stats_layout = QHBoxLayout()
        
        self.packets_label = QLabel("Paquets: 0")
        self.packets_label.setStyleSheet("color: #00ff00; font-weight: bold;")
        stats_layout.addWidget(self.packets_label)
        
        self.entities_label = QLabel("Entités: 0")
        self.entities_label.setStyleSheet("color: #00ffff; font-weight: bold;")
        stats_layout.addWidget(self.entities_label)
        
        self.errors_label = QLabel("Erreurs: 0")
        self.errors_label.setStyleSheet("color: #ff0000; font-weight: bold;")
        stats_layout.addWidget(self.errors_label)
        
        self.fps_label = QLabel("FPS: 0")
        self.fps_label.setStyleSheet("color: #ffff00; font-weight: bold;")
        stats_layout.addWidget(self.fps_label)
        
        layout.addLayout(stats_layout)
        
        # Graphiques
        charts_layout = QHBoxLayout()
        
        # Graphique du débit de paquets
        self.packet_rate_chart = RealTimeChart("Débit (paquets/s)", 60)
        charts_layout.addWidget(self.packet_rate_chart)
        
        # Graphique des entités
        self.entity_rate_chart = RealTimeChart("Entités/s", 60)
        charts_layout.addWidget(self.entity_rate_chart)
        
        layout.addLayout(charts_layout)
        
        return widget
    
    def toggle_monitoring(self, checked: bool):
        """Active/désactive le monitoring"""
        self.monitoring_active = checked
        if checked:
            self.monitor_toggle.setText("Désactiver le moniteur")
            self.monitor_toggle.setStyleSheet("""
                QPushButton {
                    background-color: #4a7c4a;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """)
        else:
            self.monitor_toggle.setText("Activer le moniteur")
            self.monitor_toggle.setStyleSheet("""
                QPushButton {
                    background-color: #2d5a2d;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
            """)
    
    def clear_data(self):
        """Efface toutes les données"""
        self.packet_count = 0
        self.entity_count = 0
        self.error_count = 0
        self.packet_times.clear()
        self.packet_rate_chart.data.clear()
        self.packet_rate_chart.timestamps.clear()
        self.entity_rate_chart.data.clear()
        self.entity_rate_chart.timestamps.clear()
        self.update_stats()
    
    def on_packet_received(self, entities_count: int):
        """Appelé quand un paquet eHub est reçu"""
        if not self.monitoring_active:
            return
            
        current_time = time.time()
        self.packet_count += 1
        self.entity_count += entities_count
        self.packet_times.append(current_time)
        self.last_packet_time = current_time
    
    def on_error_occurred(self):
        """Appelé quand une erreur se produit"""
        if not self.monitoring_active:
            return
        self.error_count += 1
    
    def update_charts(self):
        """Met à jour les graphiques"""
        if not self.monitoring_active:
            return
            
        current_time = time.time()
        
        # Calculer le débit de paquets (paquets par seconde)
        if len(self.packet_times) > 1:
            # Compter les paquets dans la dernière seconde
            recent_packets = sum(1 for t in self.packet_times if current_time - t <= 1.0)
            self.packet_rate_chart.add_data_point(recent_packets, current_time)
        
        # Calculer le débit d'entités (entités par seconde)
        if len(self.packet_times) > 1:
            # Estimation basée sur les paquets récents
            recent_packets = sum(1 for t in self.packet_times if current_time - t <= 1.0)
            estimated_entities = recent_packets * (self.entity_count / max(1, self.packet_count))
            self.entity_rate_chart.add_data_point(estimated_entities, current_time)
        
        self.update_stats()
    
    def update_stats(self):
        """Met à jour les statistiques affichées"""
        self.packets_label.setText(f"Paquets: {self.packet_count}")
        self.entities_label.setText(f"Entités: {self.entity_count}")
        self.errors_label.setText(f"Erreurs: {self.error_count}")
        
        # Calculer FPS basé sur les paquets récents
        if len(self.packet_times) > 1:
            recent_packets = sum(1 for t in self.packet_times if time.time() - t <= 1.0)
            self.fps_label.setText(f"FPS: {recent_packets}")
        else:
            self.fps_label.setText("FPS: 0")

class MonitorCard(BentoCard):
    """Carte de monitoring des données"""
    
    def __init__(self, parent=None):
        super().__init__("Data Monitor", "Monitoring des données reçues et envoyées", parent)
        
    def create_content(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Statistiques
        stats_group = QGroupBox("Statistiques")
        stats_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
            }
        """)
        stats_layout = QVBoxLayout(stats_group)
        
        self.packets_label = QLabel("Paquets reçus: 0")
        stats_layout.addWidget(self.packets_label)
        
        self.entities_label = QLabel("Entités traitées: 0")
        stats_layout.addWidget(self.entities_label)
        
        self.artnet_label = QLabel("Paquets Art-Net: 0")
        stats_layout.addWidget(self.artnet_label)
        
        layout.addWidget(stats_group)
        
        # Logs
        log_group = QGroupBox("Logs")
        log_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
            }
        """)
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(120)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #404040;
                font-family: 'Courier New';
                font-size: 10px;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        # Bouton de nettoyage
        clear_btn = QPushButton("Nettoyer")
        clear_btn.clicked.connect(self.log_text.clear)
        log_layout.addWidget(clear_btn)
        
        layout.addWidget(log_group)
        
        return widget
    
    def add_log(self, message: str):
        """Ajoute un message au log"""
        self.log_text.append(f"[{time.strftime('%H:%M:%S')}] {message}")
    
    def update_stats(self, packets: int, entities: int, artnet: int):
        """Met à jour les statistiques"""
        self.packets_label.setText(f"Paquets reçus: {packets}")
        self.entities_label.setText(f"Entités traitées: {entities}")
        self.artnet_label.setText(f"Paquets Art-Net: {artnet}")
class BackendController(QObject):
    """Contrôleur du backend"""
    
    # Signaux
    data_received = pyqtSignal(list)
    artnet_sent = pyqtSignal(str, int, bytes)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, animation_engine, router_manager):
        super().__init__()
        self.running = False
        self.source = "idle" # 'idle', 'ehub', 'animation'
        self.socket = None
        self.screen_data = None
        self.pixel_mapping = {}  # Mapping ID -> (x, y) pour les données externes
        self.ehub_frame = np.zeros((128, 128, 3), dtype=np.uint8)  # Frame pour les données eHub
        self.last_ehub_send = 0  # Timestamp du dernier envoi eHub
        self.ehub_send_interval = 1.0 / 45  # 45 FPS pour eHub - équilibre fluidité/stabilité
        self.max_fps_mode = False  # Mode haute performance désactivé par défaut pour éviter les saccades
        self.thread = None
        self.animation_engine = animation_engine
        self.router_manager = router_manager
        
        # Configuration eHub sender
        self.ehub_sender_enabled = False
        self.ehub_sender_ip = "127.0.0.1"
        self.ehub_sender_port = 8765

        # Charger automatiquement la configuration Excel au démarrage
        self._auto_load_excel_config()

    def _auto_load_excel_config(self):
        """Charge automatiquement le fichier Ecran.xlsx au démarrage"""
        import os
        excel_file = "Ecran.xlsx"
        if os.path.exists(excel_file):
            print(f"[DEBUG] Chargement automatique du fichier Excel: {excel_file}")
            try:
                self.load_excel_config(excel_file)
                print("[DEBUG] Configuration Excel chargée automatiquement avec succès")
            except Exception as e:
                print(f"[DEBUG] Erreur lors du chargement automatique: {e}")
        else:
            print(f"[DEBUG] Fichier Excel non trouvé: {excel_file}")

    def load_excel_config(self, file_path: str):
        """Charge la configuration Excel et le mapping des pixels"""
        try:
            # Charger le mapping des pixels pour les données externes
            self.pixel_mapping = excel.get_pixel_mapping(file_path)
            print(f"[eHub] Mapping chargé: {len(self.pixel_mapping)} pixels configurés")
            
            # Afficher quelques exemples de mapping
            if self.pixel_mapping:
                sample_keys = list(self.pixel_mapping.keys())[:5]
                print(f"[eHub] Exemples de mapping: {sample_keys}")
                for key in sample_keys:
                    x, y = self.pixel_mapping[key]
                    print(f"[eHub]   ID {key} -> ({x}, {y})")
            
            return True
        except Exception as e:
            self.error_occurred.emit(f"Erreur chargement Excel: {e}")
            return False
    
    def start(self, source: str, config: Dict):
        """Démarre le backend avec une source spécifique."""
        if self.running:
            self.stop()

        self.source = source
        self.running = True
        
        if self.source == "ehub":
            self.thread = threading.Thread(target=self._listen_loop, args=(config.get("ip", "127.0.0.1"), config.get("port", 8765)), daemon=True)
        elif self.source == "animation":
            self.thread = threading.Thread(target=self._animation_loop, daemon=True)
        
        if self.thread:
            self.thread.start()

    def stop(self):
        """Arrête le backend."""
        self.running = False
        
        # Attendre que le thread se termine proprement
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
            
        # Fermer le socket
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
            
        self.source = "idle"
        
        # Fermer proprement le sender Art-Net
        try:
            artnet.close_artnet_sender()
        except:
            pass
        
        # Réinitialiser les références aux panels pour éviter les erreurs
        if hasattr(self, 'pong_panel'):
            self.pong_panel = None
        if hasattr(self, 'snake_panel'):
            self.snake_panel = None
        if hasattr(self, 'tetris_panel'):
            self.tetris_panel = None
    
    def _listen_loop(self, ip: str, port: int):
        """Boucle d'écoute eHub."""
        import socket
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.bind((ip, port))
            while self.running:
                try:
                    data, addr = self.socket.recvfrom(64*1024)
                    self._process_ehub_packet(data)
                except Exception as e:
                    if self.running: self.error_occurred.emit(f"Erreur réception: {e}")
        except Exception as e:
            self.error_occurred.emit(f"Erreur socket: {e}")
        finally:
            if self.socket: self.socket.close()

    def _animation_loop(self):
        """Boucle pour envoyer les frames d'animation (optimisée pour stabilité)."""
        last_send_time = 0
        target_interval = 1.0 / 45  # 45 FPS pour stabilité
        
        while self.running:
            try:
                current_time = time.time()
                
                # Envoi avec timing précis
                if current_time - last_send_time >= target_interval:
                    # Priorité aux jeux s'ils sont en cours
                    frame = None
                    if hasattr(self, 'pong_panel') and self.pong_panel and self.pong_panel.is_game_running():
                        frame = self.pong_panel.get_game_frame()
                    elif hasattr(self, 'snake_panel') and self.snake_panel and self.snake_panel.is_game_running():
                        frame = self.snake_panel.get_game_frame()
                    elif hasattr(self, 'tetris_panel') and self.tetris_panel and self.tetris_panel.is_game_running():
                        frame = self.tetris_panel.get_game_frame()
                    else:
                        frame = self.animation_engine.get_frame()
                        # NOUVEAU: Créer une frame avec pixel mapping pour eHub
                        if self.ehub_sender_enabled and self.pixel_mapping:
                            self._create_ehub_frame_from_animation(frame)
                    
                    if frame is not None:
                        self._send_frame_to_artnet(frame)
                    last_send_time = current_time
                
                # Délai adaptatif pour maintenir la fréquence cible
                elapsed = time.time() - current_time
                sleep_time = max(0.001, target_interval - elapsed)
                time.sleep(sleep_time)
                
            except Exception as e:
                # Si une erreur survient, vérifier si l'objet a été supprimé
                if not self.running:
                    break
                # Attendre un peu avant de continuer
                time.sleep(0.1)

    def _process_ehub_packet(self, data: bytes):
        """Traite un paquet eHub et met à jour la frame virtuelle (optimisé)."""
        try:
            entities_list = ehub.get_entities_list(data)
            self.data_received.emit(entities_list)
            
            # Mettre à jour la frame virtuelle avec les nouvelles données
            self._update_ehub_frame(entities_list)
            
            # Envoi optimisé - mode haute performance ou limitation de fréquence
            current_time = time.time()
            if self.max_fps_mode or current_time - self.last_ehub_send >= self.ehub_send_interval:
                self._send_frame_to_artnet(self.ehub_frame)
                self.last_ehub_send = current_time
            
        except Exception as e:
            self.error_occurred.emit(f"Erreur traitement paquet: {e}")
    
    def _update_ehub_frame(self, entities_list: List):
        """Met à jour la frame eHub avec les nouvelles données reçues (optimisé)."""
        if not self.pixel_mapping:
            return
            
        # Préparer les mises à jour en batch pour éviter les accès répétés
        updates = []
        for entity in entities_list:
            entity_id = entity[0]
            r, g, b = entity[1], entity[2], entity[3]
            
            if entity_id in self.pixel_mapping:
                x, y = self.pixel_mapping[entity_id]
                # S'assurer que les coordonnées sont dans les limites
                if 0 <= x < 128 and 0 <= y < 128:
                    updates.append((y, x, [r, g, b]))
        
        # Appliquer toutes les mises à jour en une fois
        for y, x, color in updates:
            self.ehub_frame[y, x] = color

    def _send_frame_to_artnet(self, frame: "np.ndarray"):
        """Envoie une frame d'animation vers l'écran LED réel avec le mapping physique dynamique."""
        # NOUVEAU: Envoi eHub si activé - pour TOUTES les frames (animations ET jeux)
        if self.ehub_sender_enabled and self.pixel_mapping:
            self._send_frame_to_ehub(frame)

        # Obtenir la configuration des routeurs activés
        enabled_routers = self.router_manager.get_enabled_routers()
        
        if not enabled_routers:
            # Aucun routeur activé, ne rien envoyer
            return
        
        # Calculer le nombre de bandes par routeur et adapter la largeur
        total_bands = len(enabled_routers) * 16  # 16 bandes par routeur
        bands_per_router = 16
        
        # Calculer la largeur effective de l'écran basée sur le nombre de routeurs
        effective_width = min(128, len(enabled_routers) * 32)  # 32 colonnes par routeur max
        
        # L'écran physique a des bandes réparties sur les routeurs activés
        for router_idx, (router_ip, router_port) in enumerate(enabled_routers):
            base_universe = router_idx * 32
            
            # Chaque contrôleur gère 16 bandes
            for band_in_router in range(bands_per_router):
                # Chaque bande physique correspond à 2 colonnes (montante et descendante)
                col_up = (router_idx * 16 + band_in_router) * 2
                col_down = col_up + 1
                
                # Vérifier que les colonnes sont dans les limites de la frame
                if col_up >= effective_width or col_down >= effective_width:
                    continue
                
                # Chaque bande de 259 LEDs utilise 2 univers Art-Net
                # car 1 univers DMX = 512 canaux / 3 (RVB) = 170 pixels max
                
                # --- Premier univers de la bande (LEDs 0-169) ---
                universe1 = base_universe + band_in_router * 2
                dmx_data1 = bytearray(512)
                
                # Partie montante (130 LEDs)
                for led_idx in range(130):
                    # Utiliser 130 comme diviseur pour mapper exactement 130 LEDs sur 128 pixels
                    y = 127 - (led_idx * 128 // 128) 
                    if 0 <= y < 128:
                        dmx_data1[led_idx*3 : led_idx*3+3] = bytearray(frame[y, col_up])
                
                # Début de la partie descendante (40 LEDs) - doit aller du haut vers le bas
                for led_idx in range(40):
                    y = (led_idx * 128 // 129)  # Utiliser 130 comme diviseur pour s'aligner
                    if 0 <= y < 128:
                        dmx_data1[(130+led_idx)*3 : (130+led_idx)*3+3] = bytearray(frame[y, col_down])

                try:
                    artnet.send_artnet_packet(router_ip, universe1, dmx_data1)
                    if self.running:  # Vérifier que l'objet est toujours actif
                        self.artnet_sent.emit(router_ip, universe1, bytes(dmx_data1))
                except Exception as e:
                    if self.running:  # Vérifier que l'objet est toujours actif
                        self.error_occurred.emit(f"Erreur envoi Art-Net: {e}")
                    
                # --- Deuxième univers de la bande (LEDs 170-258) ---
                universe2 = universe1 + 1
                dmx_data2 = bytearray(512)
                
                # Suite de la partie descendante (89 LEDs)
                for led_idx in range(40, 129):
                    y = (led_idx * 128 // 127)  # Utiliser 130 comme diviseur pour s'aligner
                    if 0 <= y < 128:
                        dmx_data2[(led_idx-40)*3 : (led_idx-40)*3+3] = bytearray(frame[y, col_down])

                try:
                    artnet.send_artnet_packet(router_ip, universe2, dmx_data2)
                    if self.running:  # Vérifier que l'objet est toujours actif
                        self.artnet_sent.emit(router_ip, universe2, bytes(dmx_data2))
                except Exception as e:
                    if self.running:  # Vérifier que l'objet est toujours actif
                        self.error_occurred.emit(f"Erreur envoi Art-Net: {e}")

    def _send_frame_to_ehub(self, frame: "np.ndarray"):
        """Envoie une frame vers eHub pour monitoring"""
        print(f"[eHub] Tentative d'envoi frame shape: {frame.shape}, pixel_mapping: {len(self.pixel_mapping) if self.pixel_mapping else 0} entrées")
        try:
            entities = []
            
            # Convertir la frame en entités eHub en utilisant le pixel mapping
            for entity_id, (x, y) in self.pixel_mapping.items():
                if 0 <= y < frame.shape[0] and 0 <= x < frame.shape[1]:
                    r, g, b = frame[y, x]
                    # Inclure TOUS les pixels du mapping, même noirs (pour les jeux)
                    # Les jeux peuvent avoir des entités "noires" qui sont valides
                    entities.append((entity_id, int(r), int(g), int(b), 0))
            
            # Envoyer les entités via eHub
            if entities:
                ehub_sender.send_ehub_packet(entities, 1, self.ehub_sender_ip, self.ehub_sender_port)
                print(f"[eHub] Envoyé {len(entities)} entités vers {self.ehub_sender_ip}:{self.ehub_sender_port}")
            else:
                print(f"[eHub] Aucune entité à envoyer - pixel_mapping: {len(self.pixel_mapping)} entrées, frame shape: {frame.shape}")
                
        except Exception as e:
            if self.running:
                self.error_occurred.emit(f"Erreur envoi eHub: {e}")
            print(f"[eHub] Erreur: {e}")
    
    def enable_ehub_sender(self, ip: str = "127.0.0.1", port: int = 8765):
        """Active l'envoi eHub"""
        self.ehub_sender_enabled = True
        self.ehub_sender_ip = ip
        self.ehub_sender_port = port
        print(f"[eHub] Sender activé vers {ip}:{port}")
    
    def disable_ehub_sender(self):
        """Désactive l'envoi eHub"""
        self.ehub_sender_enabled = False
        ehub_sender.close_ehub_sender()
        print("[eHub] Sender désactivé")
    
    def _create_ehub_frame_from_animation(self, animation_frame):
        """
        Crée une frame eHub à partir d'une frame d'animation
        en utilisant le pixel mapping Excel
        """
        try:
            if not self.pixel_mapping:
                return
            
            # Créer une frame 128x128 pour eHub
            ehub_frame = np.zeros((128, 128, 3), dtype=np.uint8)
            
            # Copier les données de l'animation dans la frame eHub
            if animation_frame is not None and hasattr(animation_frame, 'shape'):
                # Redimensionner si nécessaire
                if animation_frame.shape != (128, 128, 3):
                    # Copier le centre de l'animation ou redimensionner
                    h, w = animation_frame.shape[:2]
                    start_y = max(0, (h - 128) // 2)
                    start_x = max(0, (w - 128) // 2)
                    end_y = min(h, start_y + 128)
                    end_x = min(w, start_x + 128)
                    
                    ehub_frame[:end_y-start_y, :end_x-start_x] = animation_frame[start_y:end_y, start_x:end_x]
                else:
                    ehub_frame = animation_frame.copy()
            
            # Maintenant envoyer cette frame via eHub
            self._send_frame_to_ehub(ehub_frame)
            
        except Exception as e:
            if self.running:
                self.error_occurred.emit(f"Erreur création frame eHub: {e}")

class MainWindow(QMainWindow):
    """Fenêtre principale avec interface Bento Box et panneau de contrôle."""
    
    def __init__(self):
        super().__init__()
        self.animation_engine = AnimationEngine()
        self.router_manager = RouterManager()
        self.backend = BackendController(self.animation_engine, self.router_manager)
        self.stats = {"packets": 0, "entities": 0, "artnet": 0}
        self.visualization_panel = None # Remplacera la fenêtre
        self.router_config_panel = None
        self.pong_panel = None
        self.snake_panel = None
        self.tetris_panel = None
        print("Initialisation de l'application...")
        self.setup_ui()
        self.setup_connections()
        
        # Connecter le panneau Pong au backend après création
        if self.pong_panel:
            self.backend.pong_panel = self.pong_panel
        
        # Connecter le panneau Snake au backend après création
        if self.snake_panel:
            self.backend.snake_panel = self.snake_panel
        
        # Connecter le panneau Tetris au backend après création
        if self.tetris_panel:
            self.backend.tetris_panel = self.tetris_panel
        
    def setup_ui(self):
        """Configure l'interface principale."""
        self.setWindowTitle("LED Controller Pro - Contrôleur LED Professionnel")
        self.setGeometry(100, 100, 1800, 1000)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
        """)
        
        # Widget central et layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Panneau de navigation latéral
        nav_panel = self.create_navigation_panel()
        main_layout.addWidget(nav_panel)

        # Zone de contenu principale
        content_area = self.create_content_area()
        main_layout.addWidget(content_area, stretch=1)
        
    def create_navigation_panel(self) -> QWidget:
        """Crée le panneau de navigation latéral."""
        panel = QWidget()
        panel.setFixedWidth(280)
        panel.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-right: 1px solid #404040;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # En-tête
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet("background-color: #1a1a1a; border-bottom: 1px solid #404040;")
        header_layout = QVBoxLayout(header)
        
        title = QLabel("LED Controller Pro")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #ffffff;
            padding: 10px;
        """)
        header_layout.addWidget(title)
        
        subtitle = QLabel("Contrôleur LED Professionnel")
        subtitle.setStyleSheet("""
            font-size: 12px;
            color: #888888;
            padding: 0 10px 10px 10px;
        """)
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header)
        
        # Boutons de navigation
        self.nav_buttons = {}
        
        nav_items = [
            ("🏠", "Tableau de Bord", "dashboard"),
            ("🎨", "Animations", "animations"),
            ("🎮", "Jeu Pong", "pong"),
            ("🐍", "Jeu Snake", "snake"),
            ("🧱", "Jeu Tetris", "tetris"),
            ("🎭", "DMX Mapping", "dmx_mapping"),
            ("⚙️", "Configuration", "config"),
            ("📊", "Monitoring", "monitoring")
        ]
        
        for icon, text, key in nav_items:
            btn = self.create_nav_button(icon, text, key)
            self.nav_buttons[key] = btn
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # Statut système en bas
        status_widget = self.create_status_widget()
        layout.addWidget(status_widget)
        
        return panel
    
    def create_nav_button(self, icon: str, text: str, key: str) -> QPushButton:
        """Crée un bouton de navigation."""
        btn = QPushButton(f"{icon} {text}")
        btn.setFixedHeight(60)
        btn.setCheckable(True)
        btn.setProperty("nav_key", key)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #cccccc;
                border: none;
                text-align: left;
                padding: 15px 20px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #404040;
            }
            QPushButton:checked {
                background-color: #007acc;
                color: #ffffff;
            }
        """)
        btn.clicked.connect(lambda: self.navigate_to(key))
        return btn
    
    def create_status_widget(self) -> QWidget:
        """Crée le widget de statut système."""
        widget = QWidget()
        widget.setFixedHeight(120)
        widget.setStyleSheet("""
            background-color: #1a1a1a;
            border-top: 1px solid #404040;
            padding: 10px;
        """)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(5)
        
        self.system_status = QLabel("🟢 Système Prêt")
        self.system_status.setStyleSheet("font-size: 12px; color: #51cf66;")
        layout.addWidget(self.system_status)
        
        self.connection_status = QLabel("🔴 Non connecté")
        self.connection_status.setStyleSheet("font-size: 12px; color: #ff6b6b;")
        layout.addWidget(self.connection_status)
        
        self.fps_status = QLabel("FPS: 45")
        self.fps_status.setStyleSheet("font-size: 12px; color: #888888;")
        layout.addWidget(self.fps_status)
        
        return widget
    
    def create_content_area(self) -> QWidget:
        """Crée la zone de contenu principale."""
        widget = QWidget()
        widget.setStyleSheet("background-color: #1e1e1e;")
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Barre d'outils supérieure
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # Zone de contenu avec QStackedWidget
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #1e1e1e;")
        
        # Créer les différentes pages
        self.dashboard_page = self.create_dashboard_page()
        self.animations_page = self.create_animations_page()
        self.pong_page = self.create_pong_page()
        self.snake_page = self.create_snake_page()
        self.tetris_page = self.create_tetris_page()
        self.dmx_mapping_page = self.create_dmx_mapping_page()
        self.config_page = self.create_config_page()
        self.monitoring_page = self.create_monitoring_page()
        
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.animations_page)
        self.content_stack.addWidget(self.pong_page)
        self.content_stack.addWidget(self.snake_page)
        self.content_stack.addWidget(self.tetris_page)
        self.content_stack.addWidget(self.dmx_mapping_page)
        self.content_stack.addWidget(self.config_page)
        self.content_stack.addWidget(self.monitoring_page)
        
        layout.addWidget(self.content_stack)
        
        return widget
    
    def create_toolbar(self) -> QWidget:
        """Crée la barre d'outils supérieure."""
        toolbar = QWidget()
        toolbar.setFixedHeight(60)
        toolbar.setStyleSheet("""
            background-color: #2d2d2d;
            border-bottom: 1px solid #404040;
        """)
        
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Titre de la page actuelle
        self.page_title = QLabel("Tableau de Bord")
        self.page_title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #ffffff;
        """)
        layout.addWidget(self.page_title)
        
        layout.addStretch()
        
        # Contrôles système
        system_controls = QHBoxLayout()
        
        self.start_stop_btn = QPushButton("▶ Démarrer Système")
        self.start_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        system_controls.addWidget(self.start_stop_btn)
        
        self.high_perf_btn = QPushButton("⚡ Haute Performance")
        self.high_perf_btn.setCheckable(True)
        self.high_perf_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:checked {
                background-color: #ffc107;
                color: black;
            }
        """)
        system_controls.addWidget(self.high_perf_btn)
        
        self.ehub_btn = QPushButton("📡 eHub Monitor")
        self.ehub_btn.setCheckable(True)
        self.ehub_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:checked {
                background-color: #138496;
            }
        """)
        system_controls.addWidget(self.ehub_btn)
        
        layout.addLayout(system_controls)
        
        return toolbar
    
    def navigate_to(self, page_key: str):
        """Navigue vers une page spécifique."""
        # Décocher tous les boutons
        for btn in self.nav_buttons.values():
            btn.setChecked(False)
        
        # Cocher le bouton actuel
        self.nav_buttons[page_key].setChecked(True)
        
        # Changer de page
        page_index = {
            "dashboard": 0,
            "animations": 1,
            "pong": 2,
            "snake": 3,
            "tetris": 4,
            "dmx_mapping": 5,
            "config": 6,
            "monitoring": 7
        }
        
        self.content_stack.setCurrentIndex(page_index[page_key])
        
        # Mettre à jour le titre
        titles = {
            "dashboard": "Tableau de Bord",
            "animations": "Animations LED",
            "pong": "Jeu Pong",
            "snake": "Jeu Snake",
            "tetris": "Jeu Tetris",
            "dmx_mapping": "DMX Mapping Live",
            "config": "Configuration",
            "monitoring": "Monitoring"
        }
        self.page_title.setText(titles[page_key])
        
        # Gérer les contrôles spécifiques
        if page_key == "animations":
            if hasattr(self, 'animations_visualization_panel'):
                self.animations_visualization_panel.start_updates()
        elif page_key == "pong":
            if hasattr(self, 'pong_visualization_panel'):
                self.pong_visualization_panel.start_updates()
        elif page_key == "tetris":
            if hasattr(self, 'tetris_visualization_panel'):
                self.tetris_visualization_panel.start_updates()
        elif page_key == "dmx_mapping":
            if hasattr(self, 'dmx_mapping_visualization_panel'):
                self.dmx_mapping_visualization_panel.start_updates()
        else:
            # Arrêter toutes les visualisations
            if hasattr(self, 'animations_visualization_panel'):
                self.animations_visualization_panel.stop_updates()
            if hasattr(self, 'pong_visualization_panel'):
                self.pong_visualization_panel.stop_updates()
            if hasattr(self, 'tetris_visualization_panel'):
                self.tetris_visualization_panel.stop_updates()
            if hasattr(self, 'dmx_mapping_visualization_panel'):
                self.dmx_mapping_visualization_panel.stop_updates()
    
    def create_dashboard_page(self) -> QWidget:
        """Crée la page tableau de bord."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titre
        title = QLabel("Tableau de Bord")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Grille de cartes
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)
        
        # Carte système
        system_card = self.create_dashboard_card("⚙️", "Système", "Contrôle du système LED", "#007acc")
        grid_layout.addWidget(system_card, 0, 0)
        
        # Carte animations
        anim_card = self.create_dashboard_card("🎨", "Animations", "Gestion des animations", "#28a745")
        grid_layout.addWidget(anim_card, 0, 1)
        
        # Carte jeu Pong
        game_card = self.create_dashboard_card("🎮", "Jeu Pong", "Contrôle du jeu", "#ffc107")
        grid_layout.addWidget(game_card, 0, 2)
        
        # Carte jeu Snake
        snake_card = self.create_dashboard_card("🐍", "Jeu Snake", "Jeu Snake classique", "#17a2b8")
        grid_layout.addWidget(snake_card, 0, 3)
        
        # Carte jeu Tetris
        tetris_card = self.create_dashboard_card("🧱", "Jeu Tetris", "Jeu de blocs classique", "#6f42c1")
        grid_layout.addWidget(tetris_card, 1, 0)
        
        # Carte DMX Mapping
        dmx_card = self.create_dashboard_card("🎭", "DMX Mapping", "Pipeline temps réel Unity→DMX", "#e83e8c")
        grid_layout.addWidget(dmx_card, 1, 1)
        
        # Carte monitoring
        monitor_card = self.create_dashboard_card("📊", "Monitoring", "Surveillance système", "#dc3545")
        grid_layout.addWidget(monitor_card, 1, 2)
        
        # Carte configuration
        config_card = self.create_dashboard_card("🔧", "Configuration", "Paramètres routeurs", "#fd7e14")
        grid_layout.addWidget(config_card, 1, 3)
        
        # Nouvelle ligne pour autres cartes
        # Carte visualisation
        viz_card = self.create_dashboard_card("👁️", "Visualisation", "Aperçu LED", "#20c997")
        grid_layout.addWidget(viz_card, 2, 0)
        
        layout.addLayout(grid_layout)
        layout.addStretch()
        
        return widget
    
    def create_dashboard_card(self, icon: str, title: str, description: str, color: str) -> QWidget:
        """Crée une carte pour le tableau de bord."""
        card = QWidget()
        card.setFixedSize(200, 150)
        card.setStyleSheet(f"""
            QWidget {{
                background-color: #2d2d2d;
                border: 2px solid {color};
                border-radius: 10px;
                padding: 15px;
            }}
            QWidget:hover {{
                background-color: #404040;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 32px; text-align: center;")
        layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff; text-align: center;")
        layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 12px; color: #cccccc; text-align: center;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        return card
    
    def create_animations_page(self) -> QWidget:
        """Crée la page des animations."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Panneau de contrôle des animations
        control_panel = QWidget()
        control_panel.setFixedWidth(300)
        control_panel.setStyleSheet("background-color: #2d2d2d; border-right: 1px solid #404040;")
        control_layout = QVBoxLayout(control_panel)
        
        # Contrôles d'animation
        anim_controls = self.create_animation_tab()
        control_layout.addWidget(anim_controls)
        
        layout.addWidget(control_panel)
        
        # Zone de visualisation (sans connexion Pong)
        self.animations_visualization_panel = VisualizationPanel(self.animation_engine)
        layout.addWidget(self.animations_visualization_panel)
        
        return widget
    
    def create_pong_page(self) -> QWidget:
        """Crée la page du jeu Pong."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Panneau de contrôle du jeu
        control_panel = QWidget()
        control_panel.setFixedWidth(350)
        control_panel.setStyleSheet("background-color: #2d2d2d; border-right: 1px solid #404040;")
        control_layout = QVBoxLayout(control_panel)
        
        # Contrôles du jeu
        pong_controls = self.create_pong_tab()
        control_layout.addWidget(pong_controls)
        
        layout.addWidget(control_panel)
        
        # Zone de visualisation du jeu (avec connexion Pong)
        self.pong_visualization_panel = VisualizationPanel(self.animation_engine)
        layout.addWidget(self.pong_visualization_panel)
        
        # Connecter le panneau Pong à la visualisation après création
        if self.pong_panel:
            self.pong_visualization_panel.set_pong_panel(self.pong_panel)
        
        return widget
    
    def create_snake_page(self) -> QWidget:
        """Crée la page du jeu Snake."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Panneau de contrôle du jeu
        control_panel = QWidget()
        control_panel.setFixedWidth(350)
        control_panel.setStyleSheet("background-color: #2d2d2d; border-right: 1px solid #404040;")
        control_layout = QVBoxLayout(control_panel)
        
        # Contrôles du jeu
        snake_controls = self.create_snake_tab()
        control_layout.addWidget(snake_controls)
        
        layout.addWidget(control_panel)
        
        # Zone de visualisation du jeu (avec connexion Snake)
        self.snake_visualization_panel = VisualizationPanel(self.animation_engine)
        layout.addWidget(self.snake_visualization_panel)
        
        # Connecter le panneau Snake à la visualisation après création
        if self.snake_panel:
            self.snake_visualization_panel.set_snake_panel(self.snake_panel)
        
        return widget
    
    def create_tetris_page(self) -> QWidget:
        """Crée la page du jeu Tetris."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Panneau de contrôle du jeu
        control_panel = QWidget()
        control_panel.setFixedWidth(350)
        control_panel.setStyleSheet("background-color: #2d2d2d; border-right: 1px solid #404040;")
        control_layout = QVBoxLayout(control_panel)
        
        # Contrôles du jeu
        tetris_controls = self.create_tetris_tab()
        control_layout.addWidget(tetris_controls)
        
        layout.addWidget(control_panel)
        
        # Zone de visualisation du jeu
        self.tetris_visualization_panel = VisualizationPanel(self.animation_engine)
        layout.addWidget(self.tetris_visualization_panel)
        
        # Connecter le panneau Tetris à la visualisation
        if self.tetris_panel:
            self.tetris_visualization_panel.set_tetris_panel(self.tetris_panel)
        
        return widget
    
    def create_dmx_mapping_page(self) -> QWidget:
        """Crée la page DMX Mapping Live."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Panneau de contrôle DMX
        control_panel = QWidget()
        control_panel.setFixedWidth(350)
        control_panel.setStyleSheet("background-color: #2d2d2d; border-right: 1px solid #404040;")
        control_layout = QVBoxLayout(control_panel)
        
        # Contrôles DMX
        dmx_controls = self.create_dmx_mapping_tab()
        control_layout.addWidget(dmx_controls)
        
        layout.addWidget(control_panel)
        
        # Zone de visualisation DMX
        self.dmx_mapping_visualization_panel = VisualizationPanel(self.animation_engine)
        layout.addWidget(self.dmx_mapping_visualization_panel)
        
        # Connecter le panneau DMX à la visualisation
        if hasattr(self, 'dmx_mapping_panel') and self.dmx_mapping_panel:
            self.dmx_mapping_visualization_panel.set_dmx_mapping_panel(self.dmx_mapping_panel)
        
        return widget
    
    def create_snake_tab(self) -> QWidget:
        """Crée l'onglet du jeu Snake."""
        if self.snake_panel is None:
            self.snake_panel = SnakePanel()
            self.snake_panel.game_started.connect(self.on_snake_game_started)
            self.snake_panel.game_stopped.connect(self.on_snake_game_stopped)
            # Connecter au backend
            self.backend.snake_panel = self.snake_panel
        return self.snake_panel
    
    def create_tetris_tab(self) -> QWidget:
        """Crée l'onglet du jeu Tetris."""
        if self.tetris_panel is None:
            self.tetris_panel = TetrisPanel()
            self.tetris_panel.game_started.connect(self.on_tetris_game_started)
            self.tetris_panel.game_stopped.connect(self.on_tetris_game_stopped)
            # Connecter au backend
            self.backend.tetris_panel = self.tetris_panel
        return self.tetris_panel
    
    def create_dmx_mapping_tab(self) -> QWidget:
        """Crée l'onglet DMX Mapping."""
        if not hasattr(self, 'dmx_mapping_panel') or self.dmx_mapping_panel is None:
            self.dmx_mapping_panel = DMXMappingPanel()
            self.dmx_mapping_panel.mapping_started.connect(self.on_dmx_mapping_started)
            self.dmx_mapping_panel.mapping_stopped.connect(self.on_dmx_mapping_stopped)
            # Connecter le frame signal pour la visualisation
            self.dmx_mapping_panel.frame_ready.connect(self.on_dmx_frame_ready)
        return self.dmx_mapping_panel
    
    def create_config_page(self) -> QWidget:
        """Crée la page de configuration."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titre
        title = QLabel("Configuration du Système")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Contenu de configuration
        config_content = self.create_router_config_tab()
        layout.addWidget(config_content)
        
        return widget
    
    def create_monitoring_page(self) -> QWidget:
        """Crée la page de monitoring."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Titre
        title = QLabel("Monitoring du Système")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Toggle pour afficher/masquer le moniteur eHub
        toggle_layout = QHBoxLayout()
        toggle_layout.addWidget(QLabel("Moniteur eHub:"))
        
        self.monitor_toggle = QCheckBox("Activer le moniteur eHub")
        self.monitor_toggle.setStyleSheet("""
            QCheckBox {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 10px;
            }
            QCheckBox::indicator:checked {
                background-color: #28a745;
                border: 2px solid #28a745;
                border-radius: 10px;
            }
        """)
        self.monitor_toggle.toggled.connect(self.toggle_ehub_monitor)
        toggle_layout.addWidget(self.monitor_toggle)
        toggle_layout.addStretch()
        
        layout.addLayout(toggle_layout)
        
        # Zone du moniteur eHub (masquée par défaut)
        self.ehub_monitor_container = QWidget()
        self.ehub_monitor_container.setVisible(False)
        ehub_layout = QVBoxLayout(self.ehub_monitor_container)
        
        # Créer le moniteur eHub
        self.ehub_monitor = EHubMonitorCard()
        ehub_layout.addWidget(self.ehub_monitor)
        
        layout.addWidget(self.ehub_monitor_container)
        layout.addStretch()
        
        return widget



    def create_animation_tab(self) -> QWidget:
        """Crée l'onglet de contrôle des animations."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Groupe Sélection
        selection_group = QGroupBox("Sélection de l'Animation")
        selection_layout = QVBoxLayout(selection_group)
        self.anim_combo = QComboBox()
        self.anim_combo.addItems(list(self.animation_engine.animations.keys()))
        selection_layout.addWidget(self.anim_combo)
        layout.addWidget(selection_group)

        # Groupe Contrôle Animation
        anim_control_group = QGroupBox("Contrôle de l'Animation")
        anim_control_layout = QVBoxLayout(anim_control_group)
        self.animation_control_btn = QPushButton("Lancer l'Animation")
        self.animation_control_btn.clicked.connect(self.toggle_animation_state)
        anim_control_layout.addWidget(self.animation_control_btn)
        layout.addWidget(anim_control_group)
        
        layout.addStretch()
        return widget

    def create_router_config_tab(self) -> QWidget:
        """Crée l'onglet de configuration des routeurs."""
        if self.router_config_panel is None:
            self.router_config_panel = RouterConfigPanel(self.router_manager)
            self.router_config_panel.config_updated.connect(self.on_router_config_updated)
        return self.router_config_panel

    def create_pong_tab(self) -> QWidget:
        """Crée l'onglet du jeu Pong."""
        if self.pong_panel is None:
            self.pong_panel = PongPanel()
            self.pong_panel.game_started.connect(self.on_pong_game_started)
            self.pong_panel.game_stopped.connect(self.on_pong_game_stopped)
            # Connecter au backend
            self.backend.pong_panel = self.pong_panel
        return self.pong_panel


        
    def setup_connections(self):
        """Configure les connexions signaux/slots."""
        # Connexions de la barre d'outils
        self.start_stop_btn.clicked.connect(self.toggle_system_state)
        self.high_perf_btn.toggled.connect(self.toggle_high_performance)
        self.ehub_btn.toggled.connect(self.toggle_ehub_sender)

        # Backend
        self.backend.data_received.connect(self.on_data_received)
        self.backend.artnet_sent.connect(self.on_artnet_sent)
        self.backend.error_occurred.connect(self.on_error)
        
        # Connecter le moniteur eHub aux signaux
        if hasattr(self, 'ehub_monitor'):
            self.backend.data_received.connect(self.ehub_monitor.on_packet_received)
            self.backend.error_occurred.connect(self.ehub_monitor.on_error_occurred)
        
        # Connexions de configuration des routeurs
        if self.router_config_panel:
            self.router_config_panel.config_updated.connect(self.on_router_config_updated)
        
        # Navigation par défaut
        self.navigate_to("dashboard")
        
    def toggle_system_state(self):
        """Bascule l'état du système (Démarrer/Arrêter)."""
        if self.backend.running:
            # --- Arrêter le système ---
            self.backend.stop()
            self.start_stop_btn.setText("▶ Démarrer Système")
            self.start_stop_btn.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            self.system_status.setText("🔴 Système Arrêté")
            self.system_status.setStyleSheet("font-size: 12px; color: #ff6b6b;")
            log_msg = "Système arrêté."
            print(f"[{time.strftime('%H:%M:%S')}] [SYSTEM] {log_msg}")
        else:
            # --- Démarrer le système ---
            # Par défaut, démarrer en mode animation
            source = "animation"
            config = {}
            
            self.backend.start(source, config)
            self.start_stop_btn.setText("⏹ Arrêter Système")
            self.start_stop_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            self.system_status.setText("🟢 Système Actif")
            self.system_status.setStyleSheet("font-size: 12px; color: #51cf66;")
            log_msg = f"Système démarré avec la source: {source}"
            print(f"[{time.strftime('%H:%M:%S')}] [SYSTEM] {log_msg}")

    def toggle_high_performance(self, state):
        """Active/désactive le mode haute performance."""
        self.backend.max_fps_mode = state
        mode = "activé" if self.backend.max_fps_mode else "désactivé"
        log_msg = f"Mode haute performance {mode}"
        print(f"[{time.strftime('%H:%M:%S')}] [PERF] {log_msg}")
    
    def toggle_ehub_sender(self, state):
        """Active/désactive l'envoi eHub."""
        if state:
            self.backend.enable_ehub_sender()
        else:
            self.backend.disable_ehub_sender()
        mode = "activé" if state else "désactivé"
        log_msg = f"Envoi eHub {mode}"
        print(f"[{time.strftime('%H:%M:%S')}] [EHUB] {log_msg}")
    
    def toggle_animation_state(self):
        """Bascule l'état de l'animation (Lancer/Arrêter)."""
        if self.animation_engine.running:
            # --- Arrêter l'animation ---
            self.animation_engine.stop()
            self.animation_control_btn.setText("Lancer l'Animation")
            print(f"[{time.strftime('%H:%M:%S')}] [ANIM] Animation arrêtée.")
        else:
            # --- Lancer l'animation ---
            anim_name = self.anim_combo.currentText()
            self.animation_engine.play(anim_name)
            self.animation_control_btn.setText("Arrêter l'Animation")
            log_msg = f"Animation '{anim_name}' lancée."
            print(f"[{time.strftime('%H:%M:%S')}] [ANIM] {log_msg}")
    
    def update_fps(self, fps_value):
        """Met à jour la fréquence cible."""
        self.backend.ehub_send_interval = 1.0 / fps_value
        log_msg = f"FPS cible changé à {fps_value}"
        print(f"[{time.strftime('%H:%M:%S')}] [PERF] {log_msg}")
        

    
    def keyPressEvent(self, event):
        """Gère les événements de touche pressée"""
        # Touches de navigation globales
        if event.key() == Qt.Key.Key_F1:
            self.navigate_to("dashboard")
        elif event.key() == Qt.Key.Key_F2:
            self.navigate_to("animations")
        elif event.key() == Qt.Key.Key_F3:
            self.navigate_to("pong")
        elif event.key() == Qt.Key.Key_F4:
            self.navigate_to("snake")
        elif event.key() == Qt.Key.Key_F5:
            self.navigate_to("tetris")
        elif event.key() == Qt.Key.Key_F6:
            self.navigate_to("dmx_mapping")
        elif event.key() == Qt.Key.Key_F7:
            self.navigate_to("config")
        elif event.key() == Qt.Key.Key_F8:
            self.navigate_to("monitoring")
        
        # Contrôles du jeu Pong (seulement si on est sur la page Pong)
        elif self.content_stack.currentIndex() == 2 and self.pong_panel:  # Page Pong
            key = event.key()
            if key == Qt.Key.Key_W:
                self.pong_panel.set_key_pressed('w', True)
            elif key == Qt.Key.Key_S:
                self.pong_panel.set_key_pressed('s', True)
            elif key == Qt.Key.Key_O:
                self.pong_panel.set_key_pressed('o', True)
            elif key == Qt.Key.Key_L:
                self.pong_panel.set_key_pressed('l', True)
            elif key == Qt.Key.Key_Space:
                if self.pong_panel.is_game_running():
                    self.pong_panel.toggle_pause()
            elif key == Qt.Key.Key_Escape:
                if self.pong_panel.is_game_running():
                    self.pong_panel.stop_game()
        
        # Contrôles du jeu Snake (seulement si on est sur la page Snake)
        elif self.content_stack.currentIndex() == 3 and self.snake_panel:  # Page Snake
            key = event.key()
            if key == Qt.Key.Key_W:
                self.snake_panel.set_key_pressed('w', True)
            elif key == Qt.Key.Key_S:
                self.snake_panel.set_key_pressed('s', True)
            elif key == Qt.Key.Key_A:
                self.snake_panel.set_key_pressed('a', True)
            elif key == Qt.Key.Key_D:
                self.snake_panel.set_key_pressed('d', True)
            elif key == Qt.Key.Key_Space:
                if self.snake_panel.is_game_running():
                    self.snake_panel.toggle_pause()
            elif key == Qt.Key.Key_Escape:
                if self.snake_panel.is_game_running():
                    self.snake_panel.stop_game()
        
        # Contrôles du jeu Tetris (seulement si on est sur la page Tetris)
        elif self.content_stack.currentIndex() == 4 and self.tetris_panel:  # Page Tetris
            key = event.key()
            if key == Qt.Key.Key_Left:
                self.tetris_panel.set_key_pressed('left', True)
            elif key == Qt.Key.Key_Right:
                self.tetris_panel.set_key_pressed('right', True)
            elif key == Qt.Key.Key_Up:
                self.tetris_panel.set_key_pressed('up', True)
            elif key == Qt.Key.Key_Down:
                self.tetris_panel.set_key_pressed('down', True)
            elif key == Qt.Key.Key_Space:
                if self.tetris_panel.is_game_running():
                    self.tetris_panel.toggle_pause()
            elif key == Qt.Key.Key_Escape:
                if self.tetris_panel.is_game_running():
                    self.tetris_panel.stop_game()
        
        # Contrôles système globaux
        elif event.key() == Qt.Key.Key_F12:
            self.toggle_system_state()
        elif event.key() == Qt.Key.Key_F11:
            self.high_perf_btn.setChecked(not self.high_perf_btn.isChecked())
            self.toggle_high_performance(self.high_perf_btn.isChecked())
        
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        """Gère les événements de touche relâchée"""
        # Contrôles du jeu Pong (seulement si on est sur la page Pong)
        if self.content_stack.currentIndex() == 2 and self.pong_panel:  # Page Pong
            key = event.key()
            if key == Qt.Key.Key_W:
                self.pong_panel.set_key_pressed('w', False)
            elif key == Qt.Key.Key_S:
                self.pong_panel.set_key_pressed('s', False)
            elif key == Qt.Key.Key_O:
                self.pong_panel.set_key_pressed('o', False)
            elif key == Qt.Key.Key_L:
                self.pong_panel.set_key_pressed('l', False)
        
        # Contrôles du jeu Snake (seulement si on est sur la page Snake)
        elif self.content_stack.currentIndex() == 3 and self.snake_panel:  # Page Snake
            key = event.key()
            if key == Qt.Key.Key_W:
                self.snake_panel.set_key_pressed('w', False)
            elif key == Qt.Key.Key_S:
                self.snake_panel.set_key_pressed('s', False)
            elif key == Qt.Key.Key_A:
                self.snake_panel.set_key_pressed('a', False)
            elif key == Qt.Key.Key_D:
                self.snake_panel.set_key_pressed('d', False)
        
        # Contrôles du jeu Tetris (seulement si on est sur la page Tetris)
        elif self.content_stack.currentIndex() == 4 and self.tetris_panel:  # Page Tetris
            key = event.key()
            if key == Qt.Key.Key_Left:
                self.tetris_panel.set_key_pressed('left', False)
            elif key == Qt.Key.Key_Right:
                self.tetris_panel.set_key_pressed('right', False)
            elif key == Qt.Key.Key_Up:
                self.tetris_panel.set_key_pressed('up', False)
            elif key == Qt.Key.Key_Down:
                self.tetris_panel.set_key_pressed('down', False)
        
        super().keyReleaseEvent(event)

    def load_excel_config(self, file_path: str):
        """Charge la configuration Excel."""
        log_msg = f"Chargement du fichier de configuration Excel: {os.path.basename(file_path)}"
        print(f"[{time.strftime('%H:%M:%S')}] [CONFIG] {log_msg}")
        if self.backend.load_excel_config(file_path):
            log_msg = "Configuration Excel chargée avec succès."
            print(f"[{time.strftime('%H:%M:%S')}] [CONFIG] {log_msg}")
            # Afficher les informations de mapping
            if self.backend.pixel_mapping:
                print(f"[{time.strftime('%H:%M:%S')}] [CONFIG] Mapping chargé: {len(self.backend.pixel_mapping)} pixels configurés")
        else:
            log_msg = "Erreur lors du chargement de la configuration Excel."
            print(f"[{time.strftime('%H:%M:%S')}] [CONFIG] {log_msg}")
    
    def on_data_received(self, entities_list: List):
        self.stats["packets"] += 1
        self.stats["entities"] += len(entities_list)
        print(f"[{time.strftime('%H:%M:%S')}] [DATA] Reçu {len(entities_list)} entités")
        
        # Notifier le moniteur eHub
        if hasattr(self, 'ehub_monitor'):
            self.ehub_monitor.on_packet_received(len(entities_list))
    
    def on_artnet_sent(self, ip: str, universe: int, data: bytes):
        self.stats["artnet"] += 1
        #print(f"[{time.strftime('%H:%M:%S')}] [ARTNET] {ip}:{universe} ({len(data)} bytes)")
    
    def on_error(self, error_msg: str):
        QMessageBox.critical(self, "Erreur", error_msg)
        print(f"[{time.strftime('%H:%M:%S')}] [ERROR] {error_msg}")
        
        # Notifier le moniteur eHub
        if hasattr(self, 'ehub_monitor'):
            self.ehub_monitor.on_error_occurred()
    
    def on_router_config_updated(self):
        """Appelé quand la configuration des routeurs est mise à jour."""
        log_msg = "Configuration des routeurs mise à jour"
        print(f"[{time.strftime('%H:%M:%S')}] [ROUTER] {log_msg}")
        
        # Mettre à jour les informations de mapping
        mapping_info = self.router_manager.get_mapping_info()
        enabled_count = self.router_manager.get_enabled_count()
        print(f"[{time.strftime('%H:%M:%S')}] [ROUTER] Routeurs actifs: {enabled_count}/4, Bandes: {mapping_info['total_bands']}")
    
    def on_pong_game_started(self):
        """Appelé quand le jeu Pong démarre"""
        log_msg = "Jeu Pong démarré"
        print(f"[{time.strftime('%H:%M:%S')}] [PONG] {log_msg}")
        
        # Basculer vers la page Pong si nécessaire
        if self.content_stack.currentIndex() != 2:  # Si pas sur la page Pong
            self.navigate_to("pong")
    
    def on_pong_game_stopped(self):
        """Appelé quand le jeu Pong s'arrête"""
        log_msg = "Jeu Pong arrêté"
        print(f"[{time.strftime('%H:%M:%S')}] [PONG] {log_msg}")
    
    def on_snake_game_started(self):
        """Appelé quand le jeu Snake démarre"""
        log_msg = "Jeu Snake démarré"
        print(f"[{time.strftime('%H:%M:%S')}] [SNAKE] {log_msg}")
        
        # Basculer vers la page Snake si nécessaire
        if self.content_stack.currentIndex() != 3:  # Si pas sur la page Snake
            self.navigate_to("snake")
    
    def on_snake_game_stopped(self):
        """Appelé quand le jeu Snake s'arrête"""
        log_msg = "Jeu Snake arrêté"
        print(f"[{time.strftime('%H:%M:%S')}] [SNAKE] {log_msg}")
    
    def on_tetris_game_started(self):
        """Appelé quand le jeu Tetris démarre"""
        log_msg = "Jeu Tetris démarré"
        print(f"[{time.strftime('%H:%M:%S')}] [TETRIS] {log_msg}")
        
        # Basculer vers la page Tetris si nécessaire
        if self.content_stack.currentIndex() != 4:  # Si pas sur la page Tetris
            self.navigate_to("tetris")
    
    def on_tetris_game_stopped(self):
        """Appelé quand le jeu Tetris s'arrête"""
        log_msg = "Jeu Tetris arrêté"
        print(f"[{time.strftime('%H:%M:%S')}] [TETRIS] {log_msg}")
    
    def on_dmx_mapping_started(self):
        """Appelé quand le mapping DMX démarre"""
        log_msg = "DMX Mapping démarré"
        print(f"[{time.strftime('%H:%M:%S')}] [DMX] {log_msg}")
        
        # Basculer vers la page DMX Mapping si nécessaire
        if self.content_stack.currentIndex() != 5:  # Si pas sur la page DMX
            self.navigate_to("dmx_mapping")
    
    def on_dmx_mapping_stopped(self):
        """Appelé quand le mapping DMX s'arrête"""
        log_msg = "DMX Mapping arrêté"
        print(f"[{time.strftime('%H:%M:%S')}] [DMX] {log_msg}")
    
    def on_dmx_frame_ready(self, frame):
        """Appelé quand une frame DMX est prête pour la visualisation"""
        if hasattr(self, 'dmx_mapping_visualization_panel'):
            # La visualisation se met à jour automatiquement
            pass
    
    def closeEvent(self, event):
        """Gère la fermeture de l'application"""
        print("Fermeture de l'application...")
        
        # Arrêter le backend proprement
        if hasattr(self, 'backend') and self.backend:
            self.backend.stop()
        
        # Arrêter tous les jeux
        if hasattr(self, 'pong_panel') and self.pong_panel:
            if self.pong_panel.is_game_running():
                self.pong_panel.stop_game()
        
        if hasattr(self, 'snake_panel') and self.snake_panel:
            if self.snake_panel.is_game_running():
                self.snake_panel.snake_game.stop_game()
        
        if hasattr(self, 'tetris_panel') and self.tetris_panel:
            if self.tetris_panel.is_game_running():
                self.tetris_panel.tetris_game.stop_game()
        
        # Arrêter le mapping DMX
        if hasattr(self, 'dmx_mapping_panel') and self.dmx_mapping_panel:
            if self.dmx_mapping_panel.is_mapping_running:
                self.dmx_mapping_panel.stop_mapping()
        
        # Attendre un peu que les threads se terminent
        import time
        time.sleep(0.1)
        
        event.accept()
        
    def toggle_ehub_monitor(self, checked: bool):
        """Active/désactive l'affichage du moniteur eHub."""
        self.ehub_monitor_container.setVisible(checked)
        if checked:
            print(f"[{time.strftime('%H:%M:%S')}] [MONITOR] Moniteur eHub activé")
        else:
            print(f"[{time.strftime('%H:%M:%S')}] [MONITOR] Moniteur eHub désactivé")

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Palette sombre
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(43, 43, 43))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(66, 66, 66))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    # Feuille de style globale pour améliorer le contraste
    app.setStyleSheet("""
        QLineEdit, QSpinBox {
            color: #ffffff;
            background-color: #1e1e1e;
            border: 1px solid #404040;
            border-radius: 4px;
            padding: 5px;
        }
        QComboBox {
            color: #ffffff;
            background-color: #2b2b2b;
            border: 1px solid #404040;
            border-radius: 4px;
            padding: 5px;
        }
        QComboBox::drop-down {
            border: none;
        }
        QComboBox::down-arrow {
            image: url(placeholder.png); /* Un placeholder, peut être amélioré */
        }
    """)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 