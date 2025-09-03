"""
🖥️ Écran Virtuel Matriciel - Affichage temps réel des données ArtNet
Simule un écran LED 128x128 avec mise à jour des pixels selon les valeurs RVBG
"""

import tkinter as tk
import customtkinter as ctk
import numpy as np
from PIL import Image, ImageTk
import threading
import time
from typing import Dict, List, Tuple, Optional
import sys
import os

# Import du gestionnaire de thèmes
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.themes import get_current_colors

class VirtualScreen(ctk.CTkFrame):
    """
    🖥️ Widget d'écran virtuel matriciel 128x128
    Affiche les données ArtNet comme un véritable écran LED
    """
    
    def __init__(self, parent, width=512, height=512, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Configuration de l'écran
        self.matrix_size = 128  # 128x128 pixels
        self.display_size = (width, height)  # Taille d'affichage
        self.pixel_size = width // self.matrix_size  # Taille d'un pixel virtuel
        
        # Matrice de pixels (R, G, B, W pour RGBW)
        self.pixel_matrix = np.zeros((self.matrix_size, self.matrix_size, 4), dtype=np.uint8)
        
        # Variables d'état
        self.update_active = False
        self.refresh_rate = 30  # FPS
        self.last_update = 0
        self.current_display_mode = "RGBW"  # Mode par défaut
        
        # Créer l'interface
        self._create_screen_display()
        self._setup_controls()
        
        print(f"🖥️ [VirtualScreen] Écran virtuel {self.matrix_size}x{self.matrix_size} initialisé")
    
    def _create_screen_display(self):
        """🖼️ Crée l'affichage principal de l'écran"""
        # Frame pour l'écran
        self.screen_frame = ctk.CTkFrame(self)
        self.screen_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Titre
        colors = get_current_colors()
        title_label = ctk.CTkLabel(
            self.screen_frame,
            text="🖥️ Écran Virtuel LED 128x128",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=colors["accent_primary"]
        )
        title_label.pack(pady=(10, 5))
        
        # Canvas pour l'affichage matriciel
        self.canvas = tk.Canvas(
            self.screen_frame,
            width=self.display_size[0],
            height=self.display_size[1],
            bg='#000000',  # Fond noir comme un écran éteint
            highlightthickness=0
        )
        self.canvas.pack(pady=10)
        
        # Image pour l'affichage rapide
        self.screen_image = Image.new('RGB', 
                                    (self.matrix_size, self.matrix_size), 
                                    (0, 0, 0))
        self.photo_image = None
        
        # Initialiser l'affichage
        self._update_display()
    
    def _setup_controls(self):
        """🎛️ Crée les contrôles de l'écran virtuel"""
        # Frame pour les contrôles
        controls_frame = ctk.CTkFrame(self.screen_frame)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        colors = get_current_colors()
        
        # Informations en temps réel
        self.info_frame = ctk.CTkFrame(controls_frame)
        self.info_frame.pack(side="left", fill="x", expand=True, padx=5)
        
        # Labels d'information
        self.fps_label = ctk.CTkLabel(
            self.info_frame,
            text="FPS: --",
            font=ctk.CTkFont(size=12),
            text_color=colors["text_secondary"]
        )
        self.fps_label.pack(side="left", padx=10)
        
        self.pixels_label = ctk.CTkLabel(
            self.info_frame,
            text="Pixels actifs: 0",
            font=ctk.CTkFont(size=12),
            text_color=colors["text_secondary"]
        )
        self.pixels_label.pack(side="left", padx=10)
        
        self.data_label = ctk.CTkLabel(
            self.info_frame,
            text="Dernière mise à jour: --",
            font=ctk.CTkFont(size=12),
            text_color=colors["text_secondary"]
        )
        self.data_label.pack(side="left", padx=10)
        
        # Contrôles
        controls_right = ctk.CTkFrame(controls_frame)
        controls_right.pack(side="right", padx=5)
        
        # Mode d'affichage
        self.display_mode = ctk.CTkOptionMenu(
            controls_right,
            values=["RGB", "RGBW", "HSV", "Luminosité"],
            command=self._change_display_mode
        )
        self.display_mode.pack(side="left", padx=5)
        self.display_mode.set(self.current_display_mode)
        
        # Bouton pause/play
        self.play_button = ctk.CTkButton(
            controls_right,
            text="⏸ Pause",
            width=80,
            command=self._toggle_update,
            fg_color=colors["warning"],
            hover_color=colors["accent_hover"]
        )
        self.play_button.pack(side="left", padx=5)
    
    def start_monitoring(self):
        """▶ Démarre la mise à jour de l'écran"""
        if not self.update_active:
            self.update_active = True
            self.play_button.configure(text="⏸ Pause")
            self._start_update_loop()
            print("▶ [VirtualScreen] Monitoring démarré")
    
    def stop_monitoring(self):
        """⏹ Arrête la mise à jour de l'écran"""
        if self.update_active:
            self.update_active = False
            self.play_button.configure(text="▶ Play")
            print("⏹ [VirtualScreen] Monitoring arrêté")
    
    def _toggle_update(self):
        """🔄 Basculer entre play/pause"""
        if self.update_active:
            self.stop_monitoring()
        else:
            self.start_monitoring()
    
    def _start_update_loop(self):
        """🔄 Démarre la boucle de mise à jour"""
        def update_loop():
            while self.update_active:
                try:
                    current_time = time.time()
                    if current_time - self.last_update >= (1.0 / self.refresh_rate):
                        self._update_display()
                        self._update_info_labels()
                        self.last_update = current_time
                    
                    time.sleep(0.01)  # Petite pause pour éviter la surcharge CPU
                    
                except Exception as e:
                    print(f"❌ [VirtualScreen] Erreur update loop: {e}")
                    break
        
        # Démarrer dans un thread séparé
        self.update_thread = threading.Thread(target=update_loop, daemon=True)
        self.update_thread.start()
    
    def update_artnet_data(self, universe: int, channel_data: List[int]):
        """
        📡 Met à jour l'écran avec les données ArtNet
        
        Args:
            universe: Numéro d'univers ArtNet (0-3 pour 4 BC216)
            channel_data: Liste de 512 valeurs DMX (0-255)
        """
        try:
            # Calculer la zone de l'écran pour cet univers
            # 4 univers = 4 quadrants de 64x64 chacun
            quad_size = self.matrix_size // 2  # 64 pixels
            
            # Déterminer le quadrant selon l'univers
            if universe == 0:    # Quadrant haut-gauche
                x_offset, y_offset = 0, 0
            elif universe == 1:  # Quadrant haut-droite
                x_offset, y_offset = quad_size, 0
            elif universe == 2:  # Quadrant bas-gauche
                x_offset, y_offset = 0, quad_size
            elif universe == 3:  # Quadrant bas-droite
                x_offset, y_offset = quad_size, quad_size
            else:
                return  # Univers non supporté
            
            # Traiter les données par groupes de 4 canaux (RGBW)
            pixel_index = 0
            for i in range(0, min(len(channel_data), 512), 4):
                if pixel_index >= quad_size * quad_size:
                    break
                
                # Calculer la position du pixel dans le quadrant
                pixel_x = pixel_index % quad_size
                pixel_y = pixel_index // quad_size
                
                # Position absolue dans la matrice
                abs_x = x_offset + pixel_x
                abs_y = y_offset + pixel_y
                
                # Extraire les valeurs RGBW
                r = channel_data[i] if i < len(channel_data) else 0
                g = channel_data[i + 1] if i + 1 < len(channel_data) else 0
                b = channel_data[i + 2] if i + 2 < len(channel_data) else 0
                w = channel_data[i + 3] if i + 3 < len(channel_data) else 0
                
                # Mettre à jour la matrice
                self.pixel_matrix[abs_y, abs_x] = [r, g, b, w]
                pixel_index += 1
            
            # Marquer pour mise à jour
            self.last_data_update = time.time()
            
        except Exception as e:
            print(f"❌ [VirtualScreen] Erreur mise à jour ArtNet: {e}")
    
    def _update_display(self):
        """🖼️ Met à jour l'affichage visuel de l'écran"""
        try:
            # Convertir la matrice RGBW en RGB pour affichage
            if hasattr(self, 'display_mode') and self.display_mode:
                display_mode = self.display_mode.get()
            else:
                display_mode = self.current_display_mode
            
            if display_mode == "RGB":
                # Mode RGB standard (ignorer W)
                rgb_array = self.pixel_matrix[:, :, :3]
            elif display_mode == "RGBW":
                # Mode RGBW (ajouter W aux composantes RGB)
                rgb_array = np.copy(self.pixel_matrix[:, :, :3])
                w_component = self.pixel_matrix[:, :, 3:4]
                rgb_array = np.minimum(255, rgb_array + w_component)
            elif display_mode == "HSV":
                # Mode HSV (conversion simplifiée)
                rgb_array = self._convert_to_hsv_display()
            elif display_mode == "Luminosité":
                # Mode luminosité (niveaux de gris)
                rgb_array = self._convert_to_brightness_display()
            else:
                rgb_array = self.pixel_matrix[:, :, :3]
            
            # Créer l'image PIL
            rgb_array = np.clip(rgb_array, 0, 255).astype(np.uint8)
            self.screen_image = Image.fromarray(rgb_array, 'RGB')
            
            # Redimensionner pour l'affichage
            display_image = self.screen_image.resize(self.display_size, Image.NEAREST)
            self.photo_image = ImageTk.PhotoImage(display_image)
            
            # Mettre à jour le canvas
            self.canvas.delete("all")
            self.canvas.create_image(
                self.display_size[0] // 2,
                self.display_size[1] // 2,
                image=self.photo_image
            )
            
        except Exception as e:
            print(f"❌ [VirtualScreen] Erreur affichage: {e}")
    
    def _convert_to_hsv_display(self):
        """🌈 Convertit en mode HSV pour l'affichage"""
        # Conversion simplifiée RGB → HSV pour visualisation
        rgb = self.pixel_matrix[:, :, :3].astype(float) / 255.0
        max_val = np.max(rgb, axis=2)
        min_val = np.min(rgb, axis=2)
        diff = max_val - min_val
        
        # Saturation
        sat = np.where(max_val != 0, diff / max_val, 0)
        
        # Créer une visualisation colorée basée sur la saturation
        hsv_display = np.zeros_like(rgb)
        hsv_display[:, :, 0] = sat  # Rouge pour la saturation
        hsv_display[:, :, 1] = max_val  # Vert pour la valeur
        hsv_display[:, :, 2] = diff  # Bleu pour la différence
        
        return (hsv_display * 255).astype(np.uint8)
    
    def _convert_to_brightness_display(self):
        """💡 Convertit en mode luminosité"""
        # Calculer la luminosité avec formule standard
        r, g, b, w = self.pixel_matrix[:, :, 0], self.pixel_matrix[:, :, 1], \
                     self.pixel_matrix[:, :, 2], self.pixel_matrix[:, :, 3]
        
        # Luminosité = 0.299*R + 0.587*G + 0.114*B + 0.5*W
        brightness = (0.299 * r + 0.587 * g + 0.114 * b + 0.5 * w)
        brightness = np.clip(brightness, 0, 255).astype(np.uint8)
        
        # Créer une image en niveaux de gris
        gray_display = np.stack([brightness, brightness, brightness], axis=2)
        return gray_display
    
    def _update_info_labels(self):
        """📊 Met à jour les labels d'information"""
        try:
            current_time = time.time()
            
            # Calculer FPS
            if hasattr(self, 'last_fps_time'):
                fps = 1.0 / (current_time - self.last_fps_time)
                self.fps_label.configure(text=f"FPS: {fps:.1f}")
            self.last_fps_time = current_time
            
            # Compter pixels actifs (luminosité > 0)
            active_pixels = np.sum(np.any(self.pixel_matrix > 0, axis=2))
            self.pixels_label.configure(text=f"Pixels actifs: {active_pixels}")
            
            # Dernière mise à jour des données
            if hasattr(self, 'last_data_update'):
                time_diff = current_time - self.last_data_update
                self.data_label.configure(text=f"Dernière MAJ: {time_diff:.1f}s")
            
        except Exception as e:
            print(f"❌ [VirtualScreen] Erreur update labels: {e}")
    
    def _change_display_mode(self, mode):
        """🎨 Change le mode d'affichage"""
        self.current_display_mode = mode
        print(f"🎨 [VirtualScreen] Mode d'affichage changé: {mode}")
        # La mise à jour sera automatique au prochain cycle
    
    def simulate_test_pattern(self):
        """🧪 Génère un motif de test pour démonstration"""
        try:
            # Créer un motif de test coloré
            for y in range(self.matrix_size):
                for x in range(self.matrix_size):
                    # Motif arc-en-ciel
                    r = int(255 * (x / self.matrix_size))
                    g = int(255 * (y / self.matrix_size))
                    b = int(255 * ((x + y) / (2 * self.matrix_size)))
                    w = int(128 * ((x * y) / (self.matrix_size ** 2)))
                    
                    self.pixel_matrix[y, x] = [r, g, b, w]
            
            self.last_data_update = time.time()
            print("🧪 [VirtualScreen] Motif de test généré")
            
        except Exception as e:
            print(f"❌ [VirtualScreen] Erreur motif test: {e}")


class MonitoringAdvancedPage(ctk.CTkFrame):
    """
    🖥️ Page de monitoring avancée avec écran virtuel
    Surveillance temps réel des données ArtNet
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Variables
        self.virtual_screen = None
        self.monitoring_active = False
        
        # Créer l'interface
        self._create_layout()
        
        print("🖥️ [MonitoringAdvanced] Page de monitoring avancée initialisée")
    
    def _create_layout(self):
        """🏗️ Crée le layout de la page"""
        colors = get_current_colors()
        
        # Titre principal
        title_frame = ctk.CTkFrame(self)
        title_frame.pack(fill="x", padx=10, pady=10)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="🖥️ Monitoring Avancé - Écran Virtuel LED",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=colors["accent_primary"]
        )
        title_label.pack(pady=15)
        
        # Frame principal avec écran virtuel
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Écran virtuel
        self.virtual_screen = VirtualScreen(
            main_frame,
            width=600,
            height=600,
            fg_color=colors["bg_secondary"]
        )
        self.virtual_screen.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Panel de contrôle à droite
        self._create_control_panel(main_frame)
    
    def _create_control_panel(self, parent):
        """🎛️ Crée le panel de contrôle"""
        colors = get_current_colors()
        
        control_frame = ctk.CTkFrame(parent)
        control_frame.pack(side="right", fill="y", padx=5, pady=5)
        
        # Titre du panel
        control_title = ctk.CTkLabel(
            control_frame,
            text="🎛️ Contrôles",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=colors["accent_primary"]
        )
        control_title.pack(pady=10)
        
        # Boutons de contrôle
        buttons_frame = ctk.CTkFrame(control_frame)
        buttons_frame.pack(fill="x", padx=10, pady=5)
        
        # Bouton test pattern
        test_button = ctk.CTkButton(
            buttons_frame,
            text="🧪 Motif Test",
            command=self._generate_test_pattern,
            fg_color=colors["info"],
            hover_color=colors["accent_hover"]
        )
        test_button.pack(fill="x", pady=5)
        
        # Bouton clear screen
        clear_button = ctk.CTkButton(
            buttons_frame,
            text="🧹 Effacer",
            command=self._clear_screen,
            fg_color=colors["warning"],
            hover_color=colors["accent_hover"]
        )
        clear_button.pack(fill="x", pady=5)
        
        # Statistiques en temps réel
        self._create_stats_panel(control_frame)
    
    def _create_stats_panel(self, parent):
        """📊 Crée le panel de statistiques"""
        colors = get_current_colors()
        
        stats_frame = ctk.CTkFrame(parent)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        stats_title = ctk.CTkLabel(
            stats_frame,
            text="📊 Statistiques",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=colors["accent_primary"]
        )
        stats_title.pack(pady=5)
        
        # Labels de statistiques
        self.stats_labels = {}
        stats_info = [
            ("universes", "Univers ArtNet: 0"),
            ("total_pixels", "Pixels total: 16384"),
            ("active_pixels", "Pixels actifs: 0"),
            ("data_rate", "Débit: 0 fps"),
            ("last_update", "Dernière MAJ: --")
        ]
        
        for key, text in stats_info:
            label = ctk.CTkLabel(
                stats_frame,
                text=text,
                font=ctk.CTkFont(size=12),
                text_color=colors["text_secondary"]
            )
            label.pack(anchor="w", padx=10, pady=2)
            self.stats_labels[key] = label
    
    def _generate_test_pattern(self):
        """🧪 Génère un motif de test"""
        if self.virtual_screen:
            self.virtual_screen.simulate_test_pattern()
    
    def _clear_screen(self):
        """🧹 Efface l'écran virtuel"""
        if self.virtual_screen:
            self.virtual_screen.pixel_matrix.fill(0)
    
    def start_monitoring(self):
        """▶ Démarre le monitoring avancé"""
        if self.virtual_screen:
            self.virtual_screen.start_monitoring()
        self.monitoring_active = True
        print("▶ [MonitoringAdvanced] Monitoring démarré")
    
    def stop_monitoring(self):
        """⏹ Arrête le monitoring avancé"""
        if self.virtual_screen:
            self.virtual_screen.stop_monitoring()
        self.monitoring_active = False
        print("⏹ [MonitoringAdvanced] Monitoring arrêté")
    
    def update_artnet_data(self, universe: int, channel_data: List[int]):
        """📡 Met à jour avec les données ArtNet"""
        if self.virtual_screen:
            self.virtual_screen.update_artnet_data(universe, channel_data)
