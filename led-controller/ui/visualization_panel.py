"""
Fenêtre de visualisation pour l'affichage des animations
"""
import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtGui import QPainter, QColor, QBrush, QImage
from PyQt6.QtCore import Qt, QTimer, QRect
import numpy as np

class VisualizationPanel(QWidget):
    """
    Panneau de visualisation pour afficher une grille de LEDs en temps réel.
    Peut être intégré dans une autre fenêtre.
    """
    def __init__(self, animation_engine, width=128, height=128, parent=None):
        super().__init__(parent)
        self.animation_engine = animation_engine
        self.pong_panel = None  # Sera défini plus tard
        self.snake_panel = None  # Sera défini plus tard
        self.tetris_panel = None # Sera défini plus tard
        self.dmx_mapping_panel = None # Sera défini plus tard
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.canvas = LedCanvas(self.animation_engine, width, height, self)
        layout.addWidget(self.canvas)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.canvas.update_frame)
        self.timer.start(33)  # Démarrer automatiquement à ~30 FPS
    
    def set_pong_panel(self, pong_panel):
        """Définit le panneau Pong pour l'affichage"""
        self.pong_panel = pong_panel
        self.canvas.set_pong_panel(pong_panel)
    
    def set_snake_panel(self, snake_panel):
        """Définit le panneau Snake pour l'affichage"""
        self.snake_panel = snake_panel
        self.canvas.set_snake_panel(snake_panel)
    
    def set_tetris_panel(self, tetris_panel):
        """Définit le panneau Tetris pour l'affichage"""
        self.tetris_panel = tetris_panel
        self.canvas.set_tetris_panel(tetris_panel)
    
    def set_dmx_mapping_panel(self, dmx_mapping_panel):
        """Définit le panneau DMX Mapping pour l'affichage"""
        self.dmx_mapping_panel = dmx_mapping_panel
        self.canvas.set_dmx_mapping_panel(dmx_mapping_panel)

    def start_updates(self):
        """Démarre la mise à jour de la visualisation."""
        if not self.timer.isActive():
            self.timer.start(33) # ~30 FPS

    def stop_updates(self):
        """Arrête la mise à jour de la visualisation."""
        if self.timer.isActive():
            self.timer.stop()

class LedCanvas(QWidget):
    """
    Widget qui dessine la grille de LEDs de manière optimisée en simulant des points.
    """
    def __init__(self, animation_engine, width, height, parent=None):
        super().__init__(parent)
        self.animation_engine = animation_engine
        self.pong_panel = None
        self.snake_panel = None
        self.tetris_panel = None
        self.dmx_mapping_panel = None
        self.grid_width = width
        self.grid_height = height
        # L'image sera 2x plus grande pour simuler les espaces entre les LEDs
        self.image = QImage(self.grid_width * 2, self.grid_height * 2, QImage.Format.Format_RGB888)
        self.image.fill(Qt.GlobalColor.black)
        self.setStyleSheet("background-color: #1a1a1a; border-radius: 12px;")
    
    def set_pong_panel(self, pong_panel):
        """Définit le panneau Pong"""
        self.pong_panel = pong_panel
    
    def set_snake_panel(self, snake_panel):
        """Définit le panneau Snake"""
        self.snake_panel = snake_panel
    
    def set_tetris_panel(self, tetris_panel):
        """Définit le panneau Tetris"""
        self.tetris_panel = tetris_panel
    
    def set_dmx_mapping_panel(self, dmx_mapping_panel):
        """Définit le panneau DMX Mapping"""
        self.dmx_mapping_panel = dmx_mapping_panel

    def update_frame(self):
        """Demande une nouvelle frame, la transforme en 'points' et la convertit en QImage."""
        # Priorité aux jeux et DMX mapping s'ils sont en cours
        if self.pong_panel and self.pong_panel.is_game_running():
            frame_data = self.pong_panel.get_game_frame()
        elif self.snake_panel and self.snake_panel.is_game_running():
            frame_data = self.snake_panel.get_game_frame()
        elif self.tetris_panel and self.tetris_panel.is_game_running():
            frame_data = self.tetris_panel.get_game_frame()
        elif self.dmx_mapping_panel and self.dmx_mapping_panel.is_game_running():
            frame_data = self.dmx_mapping_panel.get_game_frame()
        else:
            frame_data = self.animation_engine.get_frame()
            
        if frame_data is not None:
            # Créer une image plus grande pour simuler les espaces
            display_frame = np.zeros((self.grid_height * 2, self.grid_width * 2, 3), dtype=np.uint8)
            
            # Copier les pixels de la frame originale, en laissant des espaces noirs
            display_frame[::2, ::2] = frame_data
            
            # S'assurer que les données sont contiguës pour QImage
            if not display_frame.flags['C_CONTIGUOUS']:
                display_frame = np.ascontiguousarray(display_frame)
            
            # Créer la QImage à partir du buffer numpy
            self.image = QImage(display_frame.data, self.grid_width * 2, self.grid_height * 2, (self.grid_width * 2) * 3, QImage.Format.Format_RGB888)
            self.update()

    def paintEvent(self, event):
        """Dessine l'image de la grille sur le canevas avec un rendu net et un ratio 1:1."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
        
        # Remplir le fond en noir
        painter.fillRect(self.rect(), Qt.GlobalColor.black)

        # Calculer le plus grand carré possible avec un ratio 1:1
        canvas_w = self.width()
        canvas_h = self.height()
        size = min(canvas_w, canvas_h)
        
        # Créer le rectangle de destination centré
        offset_x = (canvas_w - size) // 2
        offset_y = (canvas_h - size) // 2
        target_rect = QRect(offset_x, offset_y, size, size)

        # Dessine l'image dans le carré de destination
        painter.drawImage(target_rect, self.image) 