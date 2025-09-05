#!/usr/bin/env python3
"""
Interface utilisateur pour le jeu Tetris
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from core.tetris_game import TetrisGame

class TetrisPanel(QWidget):
    """Panneau de contrôle pour le jeu Tetris"""
    
    game_started = pyqtSignal()
    game_stopped = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tetris_game = TetrisGame()
        self.setup_ui()
        self.setup_connections()
        
        self.score_timer = QTimer(self)
        self.score_timer.timeout.connect(self.update_score_display)
        self.score_timer.start(100)
        
        self.game_timer = QTimer(self)
        self.game_timer.timeout.connect(self.update_game)
        self.game_timer.start(50)  # 20 FPS
        
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
    def setup_ui(self):
        """Configure l'interface"""
        layout = QVBoxLayout(self)
        
        title = QLabel("🧱 TETRIS")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff; padding: 10px; text-align: center;")
        layout.addWidget(title)
        
        controls_group = QGroupBox("Contrôles")
        controls_group.setStyleSheet("QGroupBox { color: #ffffff; font-weight: bold; border: 1px solid #404040; border-radius: 6px; margin-top: 8px; padding-top: 8px; }")
        controls_layout = QVBoxLayout(controls_group)
        
        game_buttons_layout = QHBoxLayout()
        self.start_btn = QPushButton("▶ Démarrer")
        self.start_btn.setStyleSheet("QPushButton { background-color: #28a745; color: white; border: none; border-radius: 6px; padding: 10px 20px; font-weight: bold; } QPushButton:hover { background-color: #218838; }")
        game_buttons_layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.setStyleSheet("QPushButton { background-color: #ffc107; color: black; border: none; border-radius: 6px; padding: 10px 20px; font-weight: bold; } QPushButton:hover { background-color: #e0a800; }")
        self.pause_btn.setEnabled(False)
        game_buttons_layout.addWidget(self.pause_btn)
        
        self.reset_btn = QPushButton("🔄 Reset")
        self.reset_btn.setStyleSheet("QPushButton { background-color: #6c757d; color: white; border: none; border-radius: 6px; padding: 10px 20px; font-weight: bold; } QPushButton:hover { background-color: #5a6268; }")
        game_buttons_layout.addWidget(self.reset_btn)
        controls_layout.addLayout(game_buttons_layout)
        
        instructions = QLabel("<b>Contrôles :</b><br><b>Z/↑ :</b> Rotation<br><b>Q/← :</b> Gauche<br><b>S/↓ :</b> Bas<br><b>D/→ :</b> Droite<br><b>Pause :</b> Espace<br><b>Reset :</b> R")
        instructions.setStyleSheet("color: #b0b0b0; font-size: 12px; padding: 10px; background-color: #1a1a1a; border-radius: 4px;")
        instructions.setWordWrap(True)
        controls_layout.addWidget(instructions)
        layout.addWidget(controls_group)
        
        score_group = QGroupBox("Score")
        score_group.setStyleSheet("QGroupBox { color: #ffffff; font-weight: bold; border: 1px solid #404040; border-radius: 6px; margin-top: 8px; padding-top: 8px; }")
        score_layout = QHBoxLayout(score_group)
        
        score_group.setStyleSheet("QGroupBox { color: #ffffff; font-weight: bold; border: 1px solid #404040; border-radius: 6px; margin-top: 8px; padding-top: 8px; }")
        score_layout = QHBoxLayout(score_group)

        # Labels pour Score, Niveau et Lignes
        self.score_label = self._create_score_label("Score", "0", "#28a745")
        self.level_label = self._create_score_label("Niveau", "1", "#17a2b8")
        self.lines_label = self._create_score_label("Lignes", "0", "#ffc107")

        score_layout.addWidget(self.score_label)
        score_layout.addWidget(self._create_separator())
        score_layout.addWidget(self.level_label)
        score_layout.addWidget(self._create_separator())
        score_layout.addWidget(self.lines_label)

        layout.addWidget(score_group)

        self.status_label = QLabel("Prêt à jouer")
        self.status_label.setStyleSheet("color: #51cf66; font-size: 14px; font-weight: bold; padding: 10px; text-align: center; background-color: #1a1a1a; border-radius: 4px;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()

    def _create_score_label(self, title, initial_value, color):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0,0,0,0)
        title_label = QLabel(title)
        value_label = QLabel(initial_value)
        value_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color}; text-align: center;")
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label, alignment=Qt.AlignmentFlag.AlignCenter)
        return widget

    def _create_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet("background-color: #404040;")
        return separator

    def setup_connections(self):
        self.start_btn.clicked.connect(self.toggle_game)
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.reset_btn.clicked.connect(self.reset_game)
        
    def keyPressEvent(self, event):
        key_map = {
            Qt.Key.Key_Z: "z", Qt.Key.Key_Up: "up",
            Qt.Key.Key_Q: "q", Qt.Key.Key_Left: "left",
            Qt.Key.Key_S: "s", Qt.Key.Key_Down: "down",
            Qt.Key.Key_D: "d", Qt.Key.Key_Right: "right",
        }
        if event.key() in key_map:
            self.tetris_game.set_key_pressed(key_map[event.key()], True)
        elif event.key() == Qt.Key.Key_Space:
            self.toggle_pause()
        elif event.key() == Qt.Key.Key_R:
            self.reset_game()

    def keyReleaseEvent(self, event):
        key_map = {
            Qt.Key.Key_Z: "z", Qt.Key.Key_Up: "up",
            Qt.Key.Key_Q: "q", Qt.Key.Key_Left: "left",
            Qt.Key.Key_S: "s", Qt.Key.Key_Down: "down",
            Qt.Key.Key_D: "d", Qt.Key.Key_Right: "right",
        }
        if event.key() in key_map:
            self.tetris_game.set_key_pressed(key_map[event.key()], False)

    def toggle_game(self):
        if self.tetris_game.is_actively_playing():
            self.tetris_game.stop_game()
            self.game_stopped.emit()
        else:
            if self.tetris_game.is_game_over():
                self.tetris_game.reset_game()
            self.tetris_game.start_game()
            self.game_started.emit()
            self.setFocus()
        self.update_ui_state()
        
    def toggle_pause(self):
        if self.tetris_game.is_paused():
            self.tetris_game.resume_game()
        else:
            self.tetris_game.pause_game()
        self.update_ui_state()
        
    def reset_game(self):
        self.tetris_game.reset_game()
        self.tetris_game.start_game()
        self.update_ui_state()
        
    def update_score_display(self):
        stats = self.tetris_game.get_game_stats()
        self.score_label.findChild(QLabel, "").setText(str(stats["score"]))
        self.level_label.findChild(QLabel, "").setText(str(stats["level"]))
        self.lines_label.findChild(QLabel, "").setText(str(stats["lines_cleared"]))
        
        is_actively_playing = self.tetris_game.is_actively_playing()
        game_over = self.tetris_game.is_game_over()

        if game_over:
            self.status_label.setText("Game Over - Appuyez sur Reset")
            self.status_label.setStyleSheet("color: #ff6b6b; font-size: 14px; font-weight: bold; padding: 10px; text-align: center; background-color: #1a1a1a; border-radius: 4px;")
        elif is_actively_playing:
            self.status_label.setText("Jeu en cours")
            self.status_label.setStyleSheet("color: #51cf66; font-size: 14px; font-weight: bold; padding: 10px; text-align: center; background-color: #1a1a1a; border-radius: 4px;")
        elif self.tetris_game.is_paused():
            self.status_label.setText("Jeu en pause")
            self.status_label.setStyleSheet("color: #ffd43b; font-size: 14px; font-weight: bold; padding: 10px; text-align: center; background-color: #1a1a1a; border-radius: 4px;")
        else:
            self.status_label.setText("Prêt à jouer")
            self.status_label.setStyleSheet("color: #51cf66; font-size: 14px; font-weight: bold; padding: 10px; text-align: center; background-color: #1a1a1a; border-radius: 4px;")
            
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(is_actively_playing)
        self.reset_btn.setEnabled(True)
        
        self.start_btn.setText("⏹ Arrêter" if is_actively_playing else "▶ Démarrer")
        self.pause_btn.setText("▶ Reprendre" if self.tetris_game.is_paused() else "⏸ Pause")

    def update_game(self):
        if self.tetris_game.running or self.tetris_game.game_over:
            self.tetris_game.update()
        
    def update_ui_state(self):
        self.update_score_display()
            
    def get_game_frame(self):
        return self.tetris_game.get_frame()
        
    def is_game_running(self):
        return self.tetris_game.is_running()
