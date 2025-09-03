"""
📈 Widgets graphiques modernes avec matplotlib intégré dans CustomTkinter
Graphiques temps réel pour monitoring eHub
"""

import customtkinter as ctk
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from typing import List, Tuple, Dict, Optional, Any
from datetime import datetime, timedelta
from collections import deque
import threading
import time

# Import du système de thèmes
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.themes import get_current_colors

class ModernChart(ctk.CTkFrame):
    """
    📈 Widget graphique moderne intégré dans CustomTkinter
    Supporte les mises à jour temps réel et les thèmes
    """
    
    def __init__(self, parent, title: str = "Graphique", width: int = 600, height: int = 400):
        colors = get_current_colors()
        
        super().__init__(
            parent,
            width=width,
            height=height,
            fg_color=colors["bg_secondary"],
            corner_radius=12
        )
        
        self.title = title
        self.width = width
        self.height = height
        
        # Configuration matplotlib pour thème sombre
        plt.style.use('dark_background' if colors["bg_primary"] == "#1a1a1a" else 'default')
        
        # Créer la figure matplotlib
        self.figure = Figure(figsize=(width/100, height/100), dpi=100)
        self.figure.patch.set_facecolor(colors["bg_secondary"])
        
        # Créer l'axe principal
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(colors["bg_primary"])
        
        # Styling de l'axe
        self._style_axis()
        
        # Canvas tkinter
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas_widget = self.canvas.get_tk_widget()
        
        # Configuration du canvas
        self.canvas_widget.configure(
            bg=colors["bg_secondary"],
            highlightthickness=0
        )
        
        # Layout
        self._create_layout()
        
        # Données du graphique
        self.data_history = deque(maxlen=100)  # Derniers 100 points
        self.lines = {}  # Lignes du graphique
        
        # Animation
        self.animation = None
        self.is_animating = False
        
        print(f"📈 [ModernChart] Widget '{title}' créé")
    
    def _style_axis(self):
        """Style l'axe selon le thème actuel"""
        colors = get_current_colors()
        
        # Couleurs de l'axe
        self.ax.tick_params(colors=colors["text_secondary"], which='both')
        
        # Labels et titre
        self.ax.set_title(self.title, color=colors["text_primary"], fontsize=14, weight='bold', pad=20)
        
        # Grille
        self.ax.grid(True, alpha=0.3, color=colors["text_disabled"])
        
        # Bordures
        for spine in self.ax.spines.values():
            spine.set_color(colors["border"])
        
        # Marges
        self.figure.tight_layout(pad=3.0)
    
    def _create_layout(self):
        """Crée le layout du widget"""
        # Pack le canvas
        self.canvas_widget.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame pour les contrôles (optionnel)
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent", height=40)
        # Ne pas pack pour l'instant - sera ajouté si nécessaire
    
    def add_line(self, name: str, color: str = None, style: str = '-'):
        """Ajoute une ligne au graphique"""
        colors = get_current_colors()
        
        if color is None:
            # Couleurs par défaut selon le thème
            default_colors = [
                colors["chart_line1"], 
                colors["chart_line2"], 
                colors["chart_line3"]
            ]
            color = default_colors[len(self.lines) % len(default_colors)]
        
        line, = self.ax.plot([], [], color=color, linestyle=style, linewidth=2, label=name)
        self.lines[name] = line
        
        # Mettre à jour la légende
        if len(self.lines) > 0:
            self.ax.legend(loc='upper right', fancybox=True, framealpha=0.8)
        
        print(f"📈 [ModernChart] Ligne '{name}' ajoutée")
    
    def update_data(self, timestamp: datetime, data: Dict[str, float]):
        """Met à jour les données du graphique"""
        # Ajouter le point de données
        data_point = {'timestamp': timestamp, **data}
        self.data_history.append(data_point)
        
        # Limiter l'historique
        if len(self.data_history) > 100:
            self.data_history.popleft()
    
    def refresh_plot(self):
        """Rafraîchit l'affichage du graphique"""
        if not self.data_history:
            return
        
        # Extraire les timestamps et données
        timestamps = [point['timestamp'] for point in self.data_history]
        
        # Mettre à jour chaque ligne
        for line_name, line in self.lines.items():
            if line_name in self.data_history[-1]:
                values = [point.get(line_name, 0) for point in self.data_history]
                line.set_data(range(len(values)), values)
        
        # Ajuster les axes
        if self.data_history:
            self.ax.set_xlim(0, len(self.data_history)-1)
            
            # Y-axis auto-scale
            all_values = []
            for point in self.data_history:
                for line_name in self.lines:
                    if line_name in point:
                        all_values.append(point[line_name])
            
            if all_values:
                min_val, max_val = min(all_values), max(all_values)
                margin = (max_val - min_val) * 0.1
                self.ax.set_ylim(min_val - margin, max_val + margin)
        
        # Redessiner
        self.canvas.draw()
    
    def start_animation(self, interval: int = 1000):
        """Démarre l'animation temps réel"""
        if self.is_animating:
            return
        
        def animate(frame):
            self.refresh_plot()
            return list(self.lines.values())
        
        self.animation = animation.FuncAnimation(
            self.figure, animate, interval=interval, blit=False, repeat=True
        )
        self.is_animating = True
        
        print(f"📈 [ModernChart] Animation démarrée (interval: {interval}ms)")
    
    def stop_animation(self):
        """Arrête l'animation"""
        if self.animation:
            self.animation.event_source.stop()
            self.is_animating = False
        print("📈 [ModernChart] Animation arrêtée")

class RealTimeLineChart(ModernChart):
    """
    📈 Graphique linéaire temps réel spécialisé pour métriques eHub
    """
    
    def __init__(self, parent, title: str = "Métriques Temps Réel", **kwargs):
        super().__init__(parent, title, **kwargs)
        
        # Configuration spécifique aux métriques
        self.ax.set_xlabel("Temps (secondes)", color=get_current_colors()["text_secondary"])
        self.ax.set_ylabel("Valeur", color=get_current_colors()["text_secondary"])
        
        # Ajouter les lignes principales
        self.add_line("packets_per_second", color=get_current_colors()["chart_line1"])
        self.add_line("latency_ms", color=get_current_colors()["chart_line2"])
        self.add_line("entities_processed", color=get_current_colors()["chart_line3"])

class HeatmapWidget(ctk.CTkFrame):
    """
    🔥 Widget heatmap pour visualiser la charge des contrôleurs BC216
    """
    
    def __init__(self, parent, width: int = 400, height: int = 300):
        colors = get_current_colors()
        
        super().__init__(
            parent,
            width=width, 
            height=height,
            fg_color=colors["bg_secondary"],
            corner_radius=12
        )
        
        # Configuration matplotlib
        self.figure = Figure(figsize=(width/100, height/100), dpi=100)
        self.figure.patch.set_facecolor(colors["bg_secondary"])
        
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(colors["bg_primary"])
        
        # Canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.configure(bg=colors["bg_secondary"], highlightthickness=0)
        self.canvas_widget.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Données des contrôleurs (4 contrôleurs BC216)
        self.controllers_data = np.zeros((2, 2))  # 2x2 grid pour 4 contrôleurs
        self.controller_labels = ["BC216-45", "BC216-46", "BC216-47", "BC216-48"]
        
        # Style initial
        self._setup_heatmap()
        
        print("🔥 [HeatmapWidget] Widget heatmap créé")
    
    def _setup_heatmap(self):
        """Configure l'affichage initial de la heatmap"""
        colors = get_current_colors()
        
        # Créer la heatmap
        self.im = self.ax.imshow(
            self.controllers_data, 
            cmap='RdYlGn_r',  # Rouge = haute charge, Vert = faible charge
            aspect='auto',
            vmin=0, vmax=100
        )
        
        # Labels des contrôleurs
        self.ax.set_xticks([0, 1])
        self.ax.set_yticks([0, 1])
        self.ax.set_xticklabels(["45", "46"], color=colors["text_secondary"])
        self.ax.set_yticklabels(["47", "48"], color=colors["text_secondary"])
        
        # Titre
        self.ax.set_title("Charge Contrôleurs BC216", color=colors["text_primary"], fontsize=12, weight='bold')
        
        # Colorbar
        cbar = self.figure.colorbar(self.im, ax=self.ax, shrink=0.8)
        cbar.set_label("Charge CPU (%)", color=colors["text_secondary"])
        
        # Annotations des valeurs
        self.text_annotations = []
        for i in range(2):
            for j in range(2):
                text = self.ax.text(j, i, '0%', ha="center", va="center", 
                                  color=colors["text_primary"], fontweight='bold')
                self.text_annotations.append(text)
        
        self.figure.tight_layout()
    
    def update_controllers_load(self, loads: Dict[str, float]):
        """Met à jour la charge des contrôleurs"""
        # Mapping IP → position dans la grille
        ip_to_pos = {
            "192.168.1.45": (0, 0),
            "192.168.1.46": (0, 1), 
            "192.168.1.47": (1, 0),
            "192.168.1.48": (1, 1)
        }
        
        # Mettre à jour les données
        for ip, load in loads.items():
            if ip in ip_to_pos:
                i, j = ip_to_pos[ip]
                self.controllers_data[i, j] = min(load, 100)  # Limiter à 100%
        
        # Mettre à jour l'affichage
        self.im.set_array(self.controllers_data)
        
        # Mettre à jour les annotations
        for idx, (i, j) in enumerate([(0,0), (0,1), (1,0), (1,1)]):
            load_value = self.controllers_data[i, j]
            self.text_annotations[idx].set_text(f'{load_value:.0f}%')
        
        # Redessiner
        self.canvas.draw()

# Fonction utilitaire pour créer des graphiques rapidement
def create_monitoring_chart(parent, chart_type: str = "line", **kwargs) -> ModernChart:
    """
    🎨 Factory pour créer des graphiques de monitoring
    """
    if chart_type == "line":
        return RealTimeLineChart(parent, **kwargs)
    elif chart_type == "heatmap":
        return HeatmapWidget(parent, **kwargs)
    else:
        return ModernChart(parent, **kwargs)
