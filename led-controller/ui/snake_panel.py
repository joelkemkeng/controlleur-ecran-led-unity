#!/usr/bin/env python3
"""
Interface utilisateur pour le jeu Snake
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QPushButton, QTextEdit, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from core.snake_game import SnakeGame, Direction

class SnakePanel(QWidget):
    """Panneau de contrôle pour le jeu Snake"""
    
    game_started = pyqtSignal()
    game_stopped = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.snake_game = SnakeGame()
        self.setup_ui()
        self.setup_connections()
        
        # Timer pour mettre à jour les scores
        self.score_timer = QTimer()
        self.score_timer.timeout.connect(self.update_score_display)
        self.score_timer.start(100)  # Mise à jour toutes les 100ms
        
        # Timer pour mettre à jour le jeu
        self.game_timer = QTimer()
        self.game_timer.timeout.connect(self.update_game)
        self.game_timer.start(50)  # 20 FPS pour le jeu
        
        # S'assurer que le widget peut recevoir le focus pour les événements clavier
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
    def setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("🐍 SNAKE")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #ffffff;
            padding: 10px;
            text-align: center;
        """)
        layout.addWidget(title)
        
        # Groupe Contrôles
        controls_group = QGroupBox("Contrôles")
        controls_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
            }
        """)
        controls_layout = QVBoxLayout(controls_group)
        
        # Boutons de contrôle du jeu
        game_buttons_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶ Démarrer")
        self.start_btn.setStyleSheet("""
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
        game_buttons_layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: black;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """)
        self.pause_btn.setEnabled(False)
        game_buttons_layout.addWidget(self.pause_btn)
        
        self.reset_btn = QPushButton("🔄 Reset")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        game_buttons_layout.addWidget(self.reset_btn)
        
        controls_layout.addLayout(game_buttons_layout)
        
        # Instructions de contrôle
        instructions = QLabel("""
        <b>Contrôles :</b><br>
        <b>Z :</b> Haut<br>
        <b>Q :</b> Gauche<br>
        <b>S :</b> Bas<br>
        <b>D :</b> Droite<br>
        <b>Pause :</b> Espace<br>
        <b>Reset :</b> R
        """)
        instructions.setStyleSheet("""
            color: #b0b0b0;
            font-size: 12px;
            padding: 10px;
            background-color: #1a1a1a;
            border-radius: 4px;
        """)
        instructions.setWordWrap(True)
        controls_layout.addWidget(instructions)
        
        layout.addWidget(controls_group)
        
        # Groupe Score
        score_group = QGroupBox("Score")
        score_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 1px solid #404040;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
            }
        """)
        score_layout = QHBoxLayout(score_group)
        
        # Score actuel
        current_score_layout = QVBoxLayout()
        current_score_layout.addWidget(QLabel("Score Actuel"))
        self.current_score_label = QLabel("0")
        self.current_score_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #28a745;
            text-align: center;
        """)
        current_score_layout.addWidget(self.current_score_label)
        score_layout.addLayout(current_score_layout)
        
        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet("background-color: #404040;")
        score_layout.addWidget(separator)
        
        # Meilleur score
        best_score_layout = QVBoxLayout()
        best_score_layout.addWidget(QLabel("Meilleur Score"))
        self.best_score_label = QLabel("0")
        self.best_score_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #ffc107;
            text-align: center;
        """)
        best_score_layout.addWidget(self.best_score_label)
        score_layout.addLayout(best_score_layout)
        
        layout.addWidget(score_group)
        
        # Statut du jeu
        self.status_label = QLabel("Prêt à jouer")
        self.status_label.setStyleSheet("""
            color: #51cf66;
            font-size: 14px;
            font-weight: bold;
            padding: 10px;
            text-align: center;
            background-color: #1a1a1a;
            border-radius: 4px;
        """)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
    def setup_connections(self):
        """Configure les connexions signaux/slots"""
        self.start_btn.clicked.connect(self.toggle_game)
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.reset_btn.clicked.connect(self.reset_game)
        
    def keyPressEvent(self, event):
        """Gère les événements clavier"""
        key = event.key()
        
        # Contrôles ZQSD
        if key == Qt.Key.Key_Z:
            self.change_direction(Direction.UP)
        elif key == Qt.Key.Key_S:
            self.change_direction(Direction.DOWN)
        elif key == Qt.Key.Key_Q:
            self.change_direction(Direction.LEFT)
        elif key == Qt.Key.Key_D:
            self.change_direction(Direction.RIGHT)
        elif key == Qt.Key.Key_Space:
            self.toggle_pause()
        elif key == Qt.Key.Key_R:
            self.reset_game()
            
    def toggle_game(self):
        """Démarre ou arrête le jeu"""
        # Utiliser l'état de jeu actif pour décider d'arrêter
        if self.snake_game.is_actively_playing():
            self.snake_game.stop_game()
            self.game_stopped.emit()
        else:
            # Si le jeu est terminé, le remettre à zéro d'abord
            if self.snake_game.is_game_over():
                self.snake_game.reset_game()
            self.snake_game.start_game()
            self.game_started.emit()
            # S'assurer que le focus est sur ce widget pour les contrôles clavier
            self.setFocus()
        self.update_ui_state()
        
    def toggle_pause(self):
        """Met en pause ou reprend le jeu"""
        if self.snake_game.running:
            self.snake_game.pause_game()
        else:
            self.snake_game.resume_game()
        self.update_ui_state()
        
    def reset_game(self):
        """Remet à zéro le jeu"""
        self.snake_game.reset_game()
        self.snake_game.start_game()
        self.update_ui_state()
        
    def change_direction(self, direction: Direction):
        """Change la direction du serpent"""
        if self.snake_game.is_running():
            self.snake_game.change_direction(direction)
            
    def update_score_display(self):
        """Met à jour l'affichage des scores"""
        self.current_score_label.setText(str(self.snake_game.get_score()))
        self.best_score_label.setText(str(self.snake_game.get_high_score()))

        # Mettre à jour le statut en fonction des états du jeu
        is_actively_playing = self.snake_game.is_actively_playing()
        game_over = self.snake_game.is_game_over()

        if game_over:
            self.status_label.setText("Game Over - Appuyez sur Reset")
            self.status_label.setStyleSheet("""
                color: #ff6b6b;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                text-align: center;
                background-color: #1a1a1a;
                border-radius: 4px;
            """)
        elif is_actively_playing:
            self.status_label.setText("Jeu en cours")
            self.status_label.setStyleSheet("""
                color: #51cf66;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                text-align: center;
                background-color: #1a1a1a;
                border-radius: 4px;
            """)
        elif self.snake_game.is_paused():
            self.status_label.setText("Jeu en pause")
            self.status_label.setStyleSheet("""
                color: #ffd43b;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                text-align: center;
                background-color: #1a1a1a;
                border-radius: 4px;
            """)
        else:
            self.status_label.setText("Prêt à jouer")
            self.status_label.setStyleSheet("""
                color: #51cf66;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                text-align: center;
                background-color: #1a1a1a;
                border-radius: 4px;
            """)
            
        # Mettre à jour les boutons
        self.start_btn.setEnabled(True)  # Le bouton Démarrer/Arrêter est toujours actif
        self.pause_btn.setEnabled(is_actively_playing)
        self.reset_btn.setEnabled(True)
        
        # Mettre à jour le texte du bouton start
        if is_actively_playing:
            self.start_btn.setText("⏹ Arrêter")
        else:
            self.start_btn.setText("▶ Démarrer")
            
        # Mettre à jour le texte du bouton pause
        if self.snake_game.is_paused():
            self.pause_btn.setText("▶ Reprendre")
        else:
            self.pause_btn.setText("⏸ Pause")
            
    def update_game(self):
        """Met à jour le jeu"""
        # Ne mettre à jour que si le jeu est vraiment en cours ou en game over pour l'affichage
        if self.snake_game.running or self.snake_game.game_over:
            self.snake_game.update()
        
    def update_ui_state(self):
        """Met à jour l'interface utilisateur"""
        self.update_score_display()
            
    def get_game_frame(self):
        """Retourne la frame actuelle du jeu"""
        return self.snake_game.get_frame()
        
    def set_key_pressed(self, key: str, pressed: bool):
        """Transmet les touches pressées au jeu"""
        self.snake_game.set_key_pressed(key, pressed)
        
    def is_game_running(self):
        """Retourne True si le jeu est en cours"""
        return self.snake_game.is_running()
