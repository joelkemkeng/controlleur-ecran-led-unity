from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QPushButton, QTextEdit, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from core.pong_game import PongGame

class PongPanel(QWidget):
    """Panneau de contrôle pour le jeu Pong"""
    
    game_started = pyqtSignal()
    game_stopped = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pong_game = PongGame()
        self.setup_ui()
        self.setup_connections()
        
        # Timer pour mettre à jour les scores
        self.score_timer = QTimer()
        self.score_timer.timeout.connect(self.update_score_display)
        self.score_timer.start(100)  # Mise à jour toutes les 100ms
        
    def setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("🎮 PONG")
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
        <b>Joueur Gauche :</b> W (haut) / S (bas)<br>
        <b>Joueur Droite :</b> O (haut) / L (bas)<br>
        <b>Pause :</b> Espace<br>
        <b>Quitter :</b> Échap
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
        
        # Score joueur gauche
        left_score_layout = QVBoxLayout()
        left_score_layout.addWidget(QLabel("Joueur Gauche"))
        self.left_score_label = QLabel("0")
        self.left_score_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #28a745;
            text-align: center;
        """)
        left_score_layout.addWidget(self.left_score_label)
        score_layout.addLayout(left_score_layout)
        
        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet("background-color: #404040;")
        score_layout.addWidget(separator)
        
        # Score joueur droite
        right_score_layout = QVBoxLayout()
        right_score_layout.addWidget(QLabel("Joueur Droite"))
        self.right_score_label = QLabel("0")
        self.right_score_label.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #28a745;
            text-align: center;
        """)
        right_score_layout.addWidget(self.right_score_label)
        score_layout.addLayout(right_score_layout)
        
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
        
    def toggle_game(self):
        """Démarre ou arrête le jeu"""
        if not self.pong_game.running:
            self.start_game()
        else:
            self.stop_game()
    
    def start_game(self):
        """Démarre le jeu"""
        self.pong_game.start()
        self.start_btn.setText("⏹ Arrêter")
        self.start_btn.setStyleSheet("""
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
        self.pause_btn.setEnabled(True)
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
        self.game_started.emit()
    
    def stop_game(self):
        """Arrête le jeu"""
        self.pong_game.stop()
        self.start_btn.setText("▶ Démarrer")
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
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("⏸ Pause")
        self.status_label.setText("Jeu arrêté")
        self.status_label.setStyleSheet("""
            color: #ff6b6b;
            font-size: 14px;
            font-weight: bold;
            padding: 10px;
            text-align: center;
            background-color: #1a1a1a;
            border-radius: 4px;
        """)
        self.game_stopped.emit()
    
    def toggle_pause(self):
        """Met en pause ou reprend le jeu"""
        if self.pong_game.paused:
            self.pong_game.resume()
            self.pause_btn.setText("⏸ Pause")
            self.status_label.setText("Jeu en cours")
        else:
            self.pong_game.pause()
            self.pause_btn.setText("▶ Reprendre")
            self.status_label.setText("Jeu en pause")
    
    def reset_game(self):
        """Remet à zéro le jeu"""
        self.pong_game.reset()
        self.update_score_display()
        self.status_label.setText("Score remis à zéro")
    
    def update_score_display(self):
        """Met à jour l'affichage des scores"""
        left_score, right_score = self.pong_game.get_score()
        self.left_score_label.setText(str(left_score))
        self.right_score_label.setText(str(right_score))
    
    def get_game_frame(self):
        """Retourne la frame actuelle du jeu"""
        return self.pong_game.get_frame()
    
    def set_key_pressed(self, key: str, pressed: bool):
        """Transmet les touches pressées au jeu"""
        self.pong_game.set_key_pressed(key, pressed)
    
    def is_game_running(self):
        """Vérifie si le jeu est en cours"""
        return self.pong_game.running and not self.pong_game.paused 