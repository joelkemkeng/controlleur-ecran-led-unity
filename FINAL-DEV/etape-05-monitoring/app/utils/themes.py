"""
🎨 Système de thèmes moderne pour l'application de monitoring eHub
Gestion des thèmes sombre/clair avec couleurs cohérentes
"""

import customtkinter as ctk
from enum import Enum
from typing import Dict, Any

class ThemeMode(Enum):
    """Modes de thème disponibles"""
    DARK = "dark"
    LIGHT = "light"
    SYSTEM = "system"

class ModernThemes:
    """
    🎨 Gestionnaire de thèmes modernes
    Couleurs cohérentes et design professionnel
    """
    
    def __init__(self):
        self.current_mode = ThemeMode.DARK
        self._setup_themes()
    
    def _setup_themes(self):
        """Configuration des couleurs pour chaque thème"""
        
        # 🌙 THÈME SOMBRE (par défaut)
        self.dark_theme = {
            # Couleurs principales
            "bg_primary": "#1a1a1a",        # Fond principal très sombre
            "bg_secondary": "#2d2d2d",      # Fond secondaire (cards, panels)
            "bg_tertiary": "#404040",       # Fond tertiaire (hover states)
            
            # Texte
            "text_primary": "#ffffff",      # Texte principal blanc
            "text_secondary": "#b3b3b3",    # Texte secondaire gris clair
            "text_disabled": "#666666",     # Texte désactivé
            
            # Accents et status
            "accent_primary": "#1f6aa5",    # Bleu principal (CustomTkinter)
            "accent_hover": "#144870",      # Bleu hover
            "success": "#00d26a",           # Vert succès
            "warning": "#ffb800",           # Orange warning
            "error": "#f04438",             # Rouge erreur
            "info": "#0ea5e9",              # Bleu info
            
            # Graphiques
            "chart_grid": "#404040",        # Grille graphiques
            "chart_text": "#b3b3b3",       # Texte graphiques
            "chart_line1": "#1f6aa5",       # Ligne principale
            "chart_line2": "#00d26a",       # Ligne secondaire
            "chart_line3": "#ffb800",       # Ligne tertiaire
            "chart_fill": "#1f6aa520",      # Remplissage transparent
            
            # Interface
            "sidebar": "#1e1e1e",           # Sidebar
            "header": "#2d2d2d",            # Header
            "border": "#404040",            # Bordures
            "shadow": "#00000030",          # Ombres
        }
        
        # ☀️ THÈME CLAIR
        self.light_theme = {
            # Couleurs principales  
            "bg_primary": "#ffffff",        # Fond principal blanc
            "bg_secondary": "#f8f9fa",      # Fond secondaire très clair
            "bg_tertiary": "#e9ecef",       # Fond tertiaire (hover)
            
            # Texte
            "text_primary": "#212529",      # Texte principal sombre
            "text_secondary": "#6c757d",    # Texte secondaire gris
            "text_disabled": "#adb5bd",     # Texte désactivé
            
            # Accents et status
            "accent_primary": "#1f6aa5",    # Bleu principal (cohérent)
            "accent_hover": "#144870",      # Bleu hover
            "success": "#198754",           # Vert succès
            "warning": "#fd7e14",           # Orange warning
            "error": "#dc3545",             # Rouge erreur
            "info": "#0dcaf0",              # Bleu info
            
            # Graphiques
            "chart_grid": "#dee2e6",        # Grille graphiques
            "chart_text": "#6c757d",       # Texte graphiques
            "chart_line1": "#1f6aa5",       # Ligne principale
            "chart_line2": "#198754",       # Ligne secondaire  
            "chart_line3": "#fd7e14",       # Ligne tertiaire
            "chart_fill": "#1f6aa520",      # Remplissage transparent
            
            # Interface
            "sidebar": "#f1f3f4",           # Sidebar clair
            "header": "#ffffff",            # Header blanc
            "border": "#dee2e6",            # Bordures claires
            "shadow": "#00000020",          # Ombres légères
        }
    
    def set_theme(self, mode: ThemeMode):
        """
        🎨 Applique un thème à l'application
        """
        self.current_mode = mode
        
        if mode == ThemeMode.DARK:
            ctk.set_appearance_mode("dark")
        elif mode == ThemeMode.LIGHT:
            ctk.set_appearance_mode("light")
        else:  # SYSTEM
            ctk.set_appearance_mode("system")
        
        print(f"🎨 [Themes] Thème appliqué: {mode.value}")
    
    def get_colors(self) -> Dict[str, str]:
        """
        🎨 Retourne les couleurs du thème actuel
        """
        if self.current_mode == ThemeMode.LIGHT:
            return self.light_theme
        else:
            return self.dark_theme  # Par défaut sombre
    
    def get_color(self, key: str) -> str:
        """
        🎨 Retourne une couleur spécifique du thème actuel
        """
        colors = self.get_colors()
        return colors.get(key, "#ffffff")  # Blanc par défaut
    
    def apply_to_widget(self, widget: Any, style: Dict[str, str]):
        """
        🎨 Applique le style d'un thème à un widget
        """
        colors = self.get_colors()
        
        # Remplacer les références aux couleurs du thème
        resolved_style = {}
        for key, value in style.items():
            if isinstance(value, str) and value.startswith("theme_"):
                color_key = value[6:]  # Enlever "theme_"
                resolved_style[key] = colors.get(color_key, value)
            else:
                resolved_style[key] = value
        
        # Appliquer le style résolu au widget
        if hasattr(widget, 'configure'):
            widget.configure(**resolved_style)

# 🎨 Instance globale du gestionnaire de thèmes
theme_manager = ModernThemes()

def get_theme_manager() -> ModernThemes:
    """Retourne l'instance globale du gestionnaire de thèmes"""
    return theme_manager

def get_current_colors() -> Dict[str, str]:
    """Raccourci pour obtenir les couleurs du thème actuel"""
    return theme_manager.get_colors()

def get_color(key: str) -> str:
    """Raccourci pour obtenir une couleur spécifique"""
    return theme_manager.get_color(key)