#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Panel DMX Mapping Live - Interface pour l'étape 3 du pipeline
"""

import sys
import os
import threading
import time
import math
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTextEdit, QGroupBox, QGridLayout, QProgressBar, QCheckBox,
    QSpinBox, QLineEdit, QComboBox, QFrame, QSizePolicy, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject
from PyQt6.QtGui import QFont, QPalette, QColor

# Import du pipeline DMX (étape 3)
class DMXMappingWorker(QThread):
    """Worker thread pour exécuter le pipeline DMX mapping"""
    
    # Signaux pour communiquer avec l'UI
    frame_received = pyqtSignal(object)  # Frame 128x128 reçue (liste de QColor)
    stats_updated = pyqtSignal(dict)  # Statistiques de mapping
    error_occurred = pyqtSignal(str)  # Erreur
    status_changed = pyqtSignal(str)  # Changement de statut
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.pipeline = None
        self.frame_buffer = [[QColor(0, 0, 0) for _ in range(128)] for _ in range(128)]
        self.stats = {
            "packets_received": 0,
            "entities_mapped": 0,
            "universes_active": 0,
            "fps": 0,
            "last_update": time.time()
        }
    
    def run(self):
        """Lance le pipeline DMX mapping dans un thread séparé"""
        try:
            # Importer le pipeline DMX depuis FINAL-DEV
            current_dir = Path(__file__).parent.parent.parent
            etape3_path = current_dir / "FINAL-DEV" / "etape-03-mapping-dmx"
            sys.path.insert(0, str(etape3_path))
            
            from ehub_complete_pipeline_mapping_dmx import EHubDMXPipeline
            
            # Créer le pipeline
            self.pipeline = EHubDMXPipeline(port=8765)
            
            # Initialiser
            if not self.pipeline.initialize():
                self.error_occurred.emit("Erreur d'initialisation du pipeline DMX")
                return
            
            self.status_changed.emit("Pipeline DMX initialisé - En écoute...")
            
            # Lancer la réception avec traitement custom
            self.custom_listen_loop()
            
        except Exception as e:
            self.error_occurred.emit(f"Erreur pipeline DMX: {e}")
        finally:
            if self.pipeline:
                self.pipeline.stop()
    
    def custom_listen_loop(self):
        """Boucle d'écoute optimisée pour 60 FPS stable avec minimisation des pixels manquants"""
        # Configuration 60 FPS haute performance
        target_fps = 60
        frame_interval = 1.0 / target_fps  # 16.67ms par frame
        last_frame_time = time.time()
        
        # Buffers optimisés pour couverage complet
        frame_accumulator = {}  # Entités reçues récemment
        persistent_entities = {}  # Entités persistantes pour continuité
        
        # Statistiques de performance
        frame_count = 0
        packet_count = 0
        last_fps_time = time.time()
        actual_fps = 0
        
        print(f"🎯 [DMX] Démarrage boucle 60 FPS (intervalle: {frame_interval*1000:.1f}ms)")
        
        while self.running:
            current_time = time.time()
            
            try:
                # Réception ultra-rapide avec timeout minimal
                message = self.pipeline.receiver.receive_message(timeout=0.005)  # 5ms timeout
                
                if message:
                    packet_count += 1
                    # Décoder le paquet
                    packet = self.pipeline.decode_ehub_packet(message)
                    if packet:
                        # Traiter le mapping DMX
                        modified_universes = self.pipeline.process_ehub_packet(packet)
                        
                        # Accumulation complète pour éviter pixels manquants
                        for entity in packet.entities:
                            entity_id = entity.entity_id
                            frame_accumulator[entity_id] = entity
                            persistent_entities[entity_id] = entity  # Sauvegarde persistante
                
                # Génération de frame à 60 FPS précis
                time_since_last_frame = current_time - last_frame_time
                
                if time_since_last_frame >= frame_interval:
                    # Fusion entités persistantes + nouvelles pour couverture maximale
                    combined_entities = {}
                    combined_entities.update(persistent_entities)  # Base persistante
                    combined_entities.update(frame_accumulator)    # Nouvelles données par-dessus
                    
                    if combined_entities:
                        entities_list = list(combined_entities.values())
                        
                        # Génération frame optimisée
                        self.create_visual_frame_enhanced(entities_list)
                        
                        # Calcul FPS réel
                        frame_count += 1
                        if current_time - last_fps_time >= 1.0:
                            actual_fps = frame_count / (current_time - last_fps_time)
                            frame_count = 0
                            last_fps_time = current_time
                            
                            # Log performance périodique
                            if packet_count % 1000 == 0:
                                print(f"🎯 [DMX] FPS: {actual_fps:.1f} | Entités: {len(entities_list)} | Buffer: {len(frame_accumulator)}")
                        
                        # Mettre à jour les statistiques
                        self.stats = {
                            "packets_received": packet_count,
                            "entities_mapped": len(entities_list),
                            "universes_active": len(modified_universes) if modified_universes else 0,
                            "fps": actual_fps,
                            "last_update": current_time,
                            "buffer_size": len(frame_accumulator)
                        }
                        
                        # Émission des signaux
                        self.frame_received.emit(self.frame_buffer.copy())
                        self.stats_updated.emit(self.stats.copy())
                        
                        # Debug périodique
                        if packet_count % 500 == 0:
                            self.analyze_frame_data(entities_list)
                    
                    last_frame_time = current_time
                    
                    # Gestion intelligente de la mémoire
                    if len(frame_accumulator) > 2500:
                        # Garder 60% des entités les plus récentes dans l'accumulateur
                        sorted_items = sorted(frame_accumulator.items(), 
                                            key=lambda x: getattr(x[1], 'timestamp', current_time),
                                            reverse=True)
                        keep_count = int(len(frame_accumulator) * 0.6)
                        frame_accumulator = dict(sorted_items[:keep_count])
                    
                    # Nettoyage périodique des entités persistantes très anciennes
                    if len(persistent_entities) > 5000:
                        # Garder 80% des entités persistantes
                        sorted_persistent = sorted(persistent_entities.items(), 
                                                 key=lambda x: getattr(x[1], 'timestamp', current_time),
                                                 reverse=True)
                        keep_persistent = int(len(persistent_entities) * 0.8)
                        persistent_entities = dict(sorted_persistent[:keep_persistent])
                
                # Pause minimale pour éviter 100% CPU tout en gardant réactivité
                remaining_time = frame_interval - (time.time() - current_time)
                if remaining_time > 0.002:  # Si plus de 2ms restantes
                    time.sleep(0.001)  # Pause de 1ms seulement
                    
            except Exception as e:
                if self.running:  # Ne pas émettre d'erreur si on s'arrête volontairement
                    self.error_occurred.emit(f"Erreur réception: {e}")
                    time.sleep(0.01)  # Pause avant retry
    
    def create_visual_frame_enhanced(self, entities):
        """Version optimisée de création de frame pour 60 FPS avec couverture maximale"""
        # Réduire la persistance pour éviter traînée tout en gardant continuité
        for y in range(128):
            for x in range(128):
                current = self.frame_buffer[y][x]
                # Fade à 40% pour réduire les traînées mais garder la continuité
                faded = QColor(
                    int(current.red() * 0.4),
                    int(current.green() * 0.4), 
                    int(current.blue() * 0.4)
                )
                self.frame_buffer[y][x] = faded
        
        # Traitement optimisé des entités
        processed_count = 0
        for entity in entities:
            try:
                # Calcul de position optimisé
                x, y = self.calculate_led_position_improved(entity.entity_id)
                
                if 0 <= x < 128 and 0 <= y < 128:
                    # Amplification des couleurs pour visibilité maximale
                    red = min(255, max(1, entity.red * 12))    # Amplification x12
                    green = min(255, max(1, entity.green * 12))
                    blue = min(255, max(1, entity.blue * 12))
                    
                    # Mélange avec couleur existante pour éviter l'écrasement
                    existing = self.frame_buffer[y][x]
                    mixed_red = min(255, max(red, existing.red()))
                    mixed_green = min(255, max(green, existing.green()))
                    mixed_blue = min(255, max(blue, existing.blue()))
                    
                    self.frame_buffer[y][x] = QColor(mixed_red, mixed_green, mixed_blue)
                    processed_count += 1
                    
            except Exception as e:
                continue  # Ignorer les erreurs individuelles
        
        # Log occasionnel pour debug
        if processed_count > 0 and processed_count % 1000 == 0:
            print(f"🎨 [Frame] {processed_count} pixels traités")

    def create_visual_frame(self, entities):
        """Crée une frame visuelle à partir des entités eHub avec mapping spatial optimisé"""
        # CORRECTION: Persistance réduite pour 60 FPS (fade QColor)
        for y in range(128):
            for x in range(128):
                current = self.frame_buffer[y][x]
                faded = QColor(
                    int(current.red() * 0.4),
                    int(current.green() * 0.4), 
                    int(current.blue() * 0.4)
                )
                self.frame_buffer[y][x] = faded
        
        # Traitement des entités avec amplification agressive
        for entity in entities:
            try:
                x, y = self.calculate_led_position_improved(entity.entity_id)
                
                if 0 <= x < 128 and 0 <= y < 128:
                    # Amplification x15 pour visibilité maximale
                    red = min(255, max(1, entity.red * 15))
                    green = min(255, max(1, entity.green * 15))
                    blue = min(255, max(1, entity.blue * 15))
                    
                    # Utiliser le blanc comme boost si RGB faible
                    if hasattr(entity, 'white') and entity.white > 0:
                        white_boost = min(50, entity.white // 5)
                        red = min(255, red + white_boost)
                        green = min(255, green + white_boost)
                        blue = min(255, blue + white_boost)
                    
                    # Mélange additif avec couleur existante
                    existing = self.frame_buffer[y][x]
                    final_red = min(255, red + existing.red())
                    final_green = min(255, green + existing.green())
                    final_blue = min(255, blue + existing.blue())
                    
                    self.frame_buffer[y][x] = QColor(final_red, final_green, final_blue)
                    
            except Exception:
                continue  # Ignorer erreurs individuelles

    def calculate_led_position_improved(self, entity_id):
        """
        Calcule la position spatiale améliorée d'une LED sur l'écran
        Utilise une distribution optimisée pour couvrir tous les pixels
        """
        width = 128
        height = 128
        
        # CORRECTION: Mapping basé sur l'ordre réel des entités dans Unity
        # Supposons un mapping matriciel standard : gauche->droite, haut->bas
        
        # Normaliser l'entity_id dans une plage continue
        if entity_id >= 100:
            normalized_id = (entity_id - 100) % (width * height)
        else:
            normalized_id = entity_id % (width * height)
        
        # Mapping matriciel : ligne par ligne
        y = normalized_id // width
        x = normalized_id % width
        
        # CORRECTION: Ajout de variation pour éviter les patterns réguliers
        # Légère rotation pour plus de naturel
        offset_x = (entity_id * 3) % 7 - 3  # Variation ±3 pixels
        offset_y = (entity_id * 5) % 7 - 3  # Variation ±3 pixels
        
        final_x = max(0, min(width - 1, x + offset_x))
        final_y = max(0, min(height - 1, y + offset_y))
        
        return final_x, final_y
    
    def spiral_distribution(self, index, size):
        """
        Distribution en spirale pour meilleure couverture de l'écran
        Assure que tous les pixels sont couverts même avec peu d'entités
        """
        center = size // 2
        
        if index == 0:
            return center, center
        
        # Spirale de Archimède pour distribution uniforme
        angle = index * 0.5  # Angle en radians
        radius = (index ** 0.5) * 3  # Rayon croissant
        
        x = int(center + radius * math.cos(angle)) % size
        y = int(center + radius * math.sin(angle)) % size
        
        return x, y
    
    def analyze_frame_data(self, entities):
        """Analyse les données pour comprendre la structure spatiale"""
        if not entities:
            return
            
        # Analyser les ranges et couleurs
        min_id = min(e.entity_id for e in entities)
        max_id = max(e.entity_id for e in entities)
        active_entities = [e for e in entities if e.red > 0 or e.green > 0 or e.blue > 0]
        
        print(f"🔍 [DMXAnalyze] Paquet #{self.packet_count}: {len(entities)} entités")
        print(f"    📊 Range IDs: {min_id} → {max_id}")
        print(f"    🌈 Entités actives: {len(active_entities)}")
        
        if active_entities:
            sample = active_entities[0]
            print(f"    🎨 Exemple: Entity {sample.entity_id} = RGB({sample.red},{sample.green},{sample.blue})")
            
        # Analyser la distribution spatiale
        spatial_info = {}
        for entity in active_entities[:10]:  # Limiter à 10 pour éviter spam
            x, y = self.calculate_led_position_improved(entity.entity_id)
            spatial_info[entity.entity_id] = (x, y)
        
        if spatial_info:
            print(f"    📍 Positions calculées: {list(spatial_info.items())[:3]}...")
    
    def start_mapping(self):
        """Démarre le mapping DMX"""
        self.running = True
        self.start()
    
    def stop_mapping(self):
        """Arrête le mapping DMX"""
        self.running = False
        if self.pipeline:
            self.pipeline.stop()
        self.wait(3000)  # Attendre 3 secondes max

class DMXMappingPanel(QWidget):
    """Panel de contrôle pour le DMX Mapping Live"""
    
    # Signaux
    mapping_started = pyqtSignal()
    mapping_stopped = pyqtSignal()
    frame_ready = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.is_mapping_running = False
        self.last_frame = None
        
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Titre
        title = QLabel("🎭 DMX Mapping Live")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #ffffff;
            padding: 10px;
            background-color: #1a1a1a;
            border-radius: 8px;
            border: 2px solid #404040;
        """)
        layout.addWidget(title)
        
        # Description
        description = QLabel(
            "Interface en temps réel pour l'étape 3 du pipeline: "
            "réception eHub depuis Unity → mapping DMX → visualisation"
        )
        description.setStyleSheet("""
            color: #cccccc;
            font-size: 12px;
            padding: 10px;
            background-color: #2d2d2d;
            border-radius: 6px;
        """)
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Contrôles principaux
        controls_group = QGroupBox("Contrôles DMX")
        controls_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: #1e1e1e;
            }
        """)
        controls_layout = QVBoxLayout(controls_group)
        
        # Boutons de contrôle
        buttons_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶ Démarrer DMX Mapping")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.start_btn.clicked.connect(self.start_mapping)
        buttons_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹ Arrêter Mapping")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_mapping)
        self.stop_btn.setEnabled(False)
        buttons_layout.addWidget(self.stop_btn)
        
        controls_layout.addLayout(buttons_layout)
        
        # Configuration
        config_layout = QGridLayout()
        
        config_layout.addWidget(QLabel("Port Unity:"), 0, 0)
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1000, 65535)
        self.port_spin.setValue(8765)
        self.port_spin.setStyleSheet("padding: 5px; font-size: 12px;")
        config_layout.addWidget(self.port_spin, 0, 1)
        
        config_layout.addWidget(QLabel("Mode visualisation:"), 1, 0)
        self.viz_mode = QComboBox()
        self.viz_mode.addItems(["Mapping réel", "Distribution uniforme", "Points lumineux"])
        self.viz_mode.setStyleSheet("padding: 5px; font-size: 12px;")
        config_layout.addWidget(self.viz_mode, 1, 1)
        
        controls_layout.addLayout(config_layout)
        layout.addWidget(controls_group)
        
        # Statistiques en temps réel
        stats_group = QGroupBox("Statistiques Temps Réel")
        stats_group.setStyleSheet(controls_group.styleSheet())
        stats_layout = QGridLayout(stats_group)
        
        self.packets_label = QLabel("Paquets reçus: 0")
        self.packets_label.setStyleSheet("color: #00ff00; font-weight: bold; font-size: 12px;")
        stats_layout.addWidget(self.packets_label, 0, 0)
        
        self.entities_label = QLabel("Entités mappées: 0")
        self.entities_label.setStyleSheet("color: #00ffff; font-weight: bold; font-size: 12px;")
        stats_layout.addWidget(self.entities_label, 0, 1)
        
        self.universes_label = QLabel("Univers actifs: 0")
        self.universes_label.setStyleSheet("color: #ffff00; font-weight: bold; font-size: 12px;")
        stats_layout.addWidget(self.universes_label, 1, 0)
        
        self.fps_label = QLabel("FPS: 0")
        self.fps_label.setStyleSheet("color: #ff00ff; font-weight: bold; font-size: 12px;")
        stats_layout.addWidget(self.fps_label, 1, 1)
        
        layout.addWidget(stats_group)
        
        # Informations système
        info_group = QGroupBox("Informations Système")
        info_group.setStyleSheet(controls_group.styleSheet())
        info_layout = QVBoxLayout(info_group)
        
        self.status_label = QLabel("Status: Arrêté")
        self.status_label.setStyleSheet("""
            color: #ff6b6b;
            font-weight: bold;
            font-size: 13px;
            padding: 8px;
            background-color: #1a1a1a;
            border-radius: 4px;
        """)
        info_layout.addWidget(self.status_label)
        
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(120)
        self.info_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #404040;
                border-radius: 4px;
                font-family: 'Courier New';
                font-size: 10px;
                padding: 5px;
            }
        """)
        self.info_text.setPlaceholderText("Les logs du mapping DMX apparaîtront ici...")
        info_layout.addWidget(self.info_text)
        
        # Bouton de nettoyage des logs
        clear_btn = QPushButton("Nettoyer les logs")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        clear_btn.clicked.connect(self.info_text.clear)
        info_layout.addWidget(clear_btn)
        
        layout.addWidget(info_group)
        layout.addStretch()
    
    def setup_connections(self):
        """Configure les connexions"""
        pass
    
    def start_mapping(self):
        """Démarre le mapping DMX"""
        if self.is_mapping_running:
            return
        
        self.add_log("🚀 Démarrage du mapping DMX...")
        
        # Créer et configurer le worker
        self.worker = DMXMappingWorker()
        self.worker.frame_received.connect(self.on_frame_received)
        self.worker.stats_updated.connect(self.on_stats_updated)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.status_changed.connect(self.on_status_changed)
        
        # Démarrer
        self.worker.start_mapping()
        
        # Mettre à jour l'UI
        self.is_mapping_running = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.port_spin.setEnabled(False)
        
        self.status_label.setText("Status: Démarrage...")
        self.status_label.setStyleSheet("""
            color: #ffc107;
            font-weight: bold;
            font-size: 13px;
            padding: 8px;
            background-color: #1a1a1a;
            border-radius: 4px;
        """)
        
        self.mapping_started.emit()
    
    def stop_mapping(self):
        """Arrête le mapping DMX"""
        if not self.is_mapping_running:
            return
        
        self.add_log("🛑 Arrêt du mapping DMX...")
        
        # Arrêter le worker
        if self.worker:
            self.worker.stop_mapping()
            self.worker = None
        
        # Mettre à jour l'UI
        self.is_mapping_running = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.port_spin.setEnabled(True)
        
        self.status_label.setText("Status: Arrêté")
        self.status_label.setStyleSheet("""
            color: #ff6b6b;
            font-weight: bold;
            font-size: 13px;
            padding: 8px;
            background-color: #1a1a1a;
            border-radius: 4px;
        """)
        
        # Réinitialiser les stats
        self.packets_label.setText("Paquets reçus: 0")
        self.entities_label.setText("Entités mappées: 0")
        self.universes_label.setText("Univers actifs: 0")
        self.fps_label.setText("FPS: 0")
        
        self.mapping_stopped.emit()
    
    def on_frame_received(self, frame):
        """Callback quand une frame est reçue"""
        self.last_frame = frame
        self.frame_ready.emit(frame)
    
    def on_stats_updated(self, stats):
        """Callback pour les statistiques"""
        self.packets_label.setText(f"Paquets reçus: {stats['packets_received']}")
        self.entities_label.setText(f"Entités mappées: {stats['entities_mapped']}")
        self.universes_label.setText(f"Univers actifs: {stats['universes_active']}")
        self.fps_label.setText(f"FPS: {stats['fps']:.1f}")
    
    def on_error(self, error_msg):
        """Callback pour les erreurs"""
        self.add_log(f"❌ ERREUR: {error_msg}")
        # Arrêter en cas d'erreur
        self.stop_mapping()
    
    def on_status_changed(self, status):
        """Callback pour les changements de statut"""
        self.add_log(f"📊 {status}")
        if "initialisé" in status.lower():
            self.status_label.setText("Status: Actif")
            self.status_label.setStyleSheet("""
                color: #51cf66;
                font-weight: bold;
                font-size: 13px;
                padding: 8px;
                background-color: #1a1a1a;
                border-radius: 4px;
            """)
    
    def add_log(self, message):
        """Ajoute un message aux logs"""
        timestamp = time.strftime("%H:%M:%S")
        self.info_text.append(f"[{timestamp}] {message}")
    
    def is_game_running(self):
        """Vérifie si le mapping est en cours"""
        return self.is_mapping_running
    
    def get_game_frame(self):
        """Retourne la dernière frame pour la visualisation, convertie en format numpy"""
        if self.last_frame is None:
            return None
            
        # Convertir QColor matrix en numpy array pour compatibilité visualisation
        if isinstance(self.last_frame[0][0], QColor):
            numpy_frame = np.zeros((128, 128, 3), dtype=np.uint8)
            for y in range(128):
                for x in range(128):
                    color = self.last_frame[y][x]
                    numpy_frame[y, x] = [color.red(), color.green(), color.blue()]
            return numpy_frame
        else:
            return self.last_frame
    
    def closeEvent(self, event):
        """Nettoyage lors de la fermeture"""
        if self.is_mapping_running:
            self.stop_mapping()
        event.accept()
