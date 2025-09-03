"""
🏠 Fenêtre principale moderne avec navigation sidebar
Architecture modulaire pour application de monitoring eHub
"""

import customtkinter as ctk
from typing import Dict, Callable, Optional
import sys
import os

# Import du gestionnaire de thèmes
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.themes import get_theme_manager, get_current_colors, ThemeMode

class ModernSidebar(ctk.CTkFrame):
    """
    🎨 Sidebar moderne avec navigation
    """
    
    def __init__(self, parent, on_page_change: Callable[[str], None]):
        colors = get_current_colors()
        
        super().__init__(
            parent, 
            width=250,
            corner_radius=0,
            fg_color=colors["sidebar"]
        )
        
        self.on_page_change = on_page_change
        self.current_page = "dashboard"
        self.nav_buttons: Dict[str, ctk.CTkButton] = {}
        
        self._create_sidebar()
    
    def _create_sidebar(self):
        """Création du contenu de la sidebar"""
        colors = get_current_colors()
        
        # Logo/Titre de l'application
        title_frame = ctk.CTkFrame(self, fg_color="transparent", height=80)
        title_frame.pack(fill="x", padx=20, pady=(20, 30))
        title_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="◆ eHub Monitor",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=colors["text_primary"]
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Monitoring temps réel",
            font=ctk.CTkFont(size=14),
            text_color=colors["text_secondary"]
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))
        
        # Menu de navigation
        nav_items = [
            ("dashboard", "⌂ Dashboard", "Vue d'ensemble des métriques"),
            ("monitoring", "◉ Monitoring", "Surveillance temps réel"),
            ("config", "⚙ Configuration", "Paramètres et réglages"),
            ("logs", "▤ Logs", "Historique et journaux"),
            ("diagnostics", "⚒ Diagnostics", "Tests et validation")
        ]
        
        for page_id, title, description in nav_items:
            self._create_nav_button(page_id, title, description)
        
        # Spacer
        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(fill="both", expand=True)
        
        # Footer avec contrôles thème
        self._create_footer()
    
    def _create_nav_button(self, page_id: str, title: str, description: str):
        """Crée un bouton de navigation moderne"""
        colors = get_current_colors()
        
        # Frame pour le bouton avec padding
        button_frame = ctk.CTkFrame(self, fg_color="transparent", height=70)
        button_frame.pack(fill="x", padx=15, pady=2)
        button_frame.pack_propagate(False)
        
        # Bouton principal
        is_active = page_id == self.current_page
        
        button = ctk.CTkButton(
            button_frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold" if is_active else "normal"),
            fg_color=colors["accent_primary"] if is_active else "transparent",
            hover_color=colors["accent_hover"] if is_active else colors["bg_tertiary"],
            border_width=0,
            corner_radius=8,
            height=50,
            anchor="w",
            command=lambda: self._on_nav_click(page_id)
        )
        button.pack(fill="x", pady=2)
        
        self.nav_buttons[page_id] = button
        
        # Description sous le bouton (seulement si pas actif)
        if not is_active:
            desc_label = ctk.CTkLabel(
                button_frame,
                text=description,
                font=ctk.CTkFont(size=11),
                text_color=colors["text_disabled"],
                anchor="w"
            )
            desc_label.pack(fill="x", padx=10, pady=(2, 0))
    
    def _create_footer(self):
        """Footer avec contrôles de thème"""
        colors = get_current_colors()
        
        footer_frame = ctk.CTkFrame(
            self, 
            fg_color=colors["bg_secondary"], 
            height=100,
            corner_radius=0
        )
        footer_frame.pack(fill="x", side="bottom")
        footer_frame.pack_propagate(False)
        
        # Titre section thème
        theme_label = ctk.CTkLabel(
            footer_frame,
            text="◐ Apparence",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["text_primary"]
        )
        theme_label.pack(pady=(15, 5))
        
        # Switch thème sombre/clair
        self.theme_switch = ctk.CTkSwitch(
            footer_frame,
            text="Mode sombre",
            font=ctk.CTkFont(size=12),
            text_color=colors["text_secondary"],
            progress_color=colors["accent_primary"],
            command=self._toggle_theme
        )
        self.theme_switch.pack(pady=5)
        
        # Définir l'état initial du switch
        current_mode = get_theme_manager().current_mode
        self.theme_switch.select() if current_mode == ThemeMode.DARK else self.theme_switch.deselect()
        
        # Version
        version_label = ctk.CTkLabel(
            footer_frame,
            text="v1.0.0",
            font=ctk.CTkFont(size=10),
            text_color=colors["text_disabled"]
        )
        version_label.pack(pady=(5, 10))
    
    def _on_nav_click(self, page_id: str):
        """Gestion du clic sur un bouton de navigation"""
        if page_id != self.current_page:
            # Mettre à jour l'état visuel
            self._update_active_button(page_id)
            
            # Notifier le changement de page
            self.on_page_change(page_id)
            
            print(f"🧭 [Navigation] Changement vers: {page_id}")
    
    def _update_active_button(self, new_page_id: str):
        """Met à jour l'apparence des boutons de navigation"""
        colors = get_current_colors()
        
        # Réinitialiser tous les boutons
        for page_id, button in self.nav_buttons.items():
            if page_id == new_page_id:
                # Bouton actif
                button.configure(
                    fg_color=colors["accent_primary"],
                    hover_color=colors["accent_hover"],
                    font=ctk.CTkFont(size=16, weight="bold")
                )
            else:
                # Boutons inactifs
                button.configure(
                    fg_color="transparent",
                    hover_color=colors["bg_tertiary"],
                    font=ctk.CTkFont(size=16, weight="normal")
                )
        
        self.current_page = new_page_id
    
    def _toggle_theme(self):
        """Basculer entre thème sombre/clair"""
        theme_manager = get_theme_manager()
        
        if self.theme_switch.get():
            theme_manager.set_theme(ThemeMode.DARK)
        else:
            theme_manager.set_theme(ThemeMode.LIGHT)
        
        # Note: Dans une vraie app, il faudrait rafraîchir l'interface
        print(f"🎨 [Theme] Basculé vers: {'sombre' if self.theme_switch.get() else 'clair'}")

class MainWindow(ctk.CTk):
    """
    🏠 Fenêtre principale de l'application
    Architecture moderne avec sidebar navigation
    """
    
    def __init__(self):
        super().__init__()
        
        # Configuration de la fenêtre
        self.title("eHub Monitor - Application de Monitoring Moderne")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        
        # Appliquer le thème par défaut
        get_theme_manager().set_theme(ThemeMode.DARK)
        
        # Variables d'état
        self.current_page = "dashboard"
        
        # Créer l'interface
        self._create_layout()
        self._create_content_area()
        
        print("🏠 [MainWindow] Fenêtre principale initialisée")
    
    def _create_layout(self):
        """Création du layout principal"""
        colors = get_current_colors()
        
        # Grid configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar
        self.sidebar = ModernSidebar(self, self._on_page_change)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Zone principale
        self.main_area = ctk.CTkFrame(
            self,
            fg_color=colors["bg_primary"],
            corner_radius=0
        )
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=(2, 0))
    
    def _create_content_area(self):
        """Zone de contenu principal avec header"""
        colors = get_current_colors()
        
        # Configuration grid
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(1, weight=1)
        
        # Header
        self.header = ctk.CTkFrame(
            self.main_area,
            height=80,
            fg_color=colors["header"],
            corner_radius=0
        )
        self.header.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 2))
        self.header.grid_propagate(False)
        
        # Titre de la page actuelle
        self.page_title = ctk.CTkLabel(
            self.header,
            text="⌂ Dashboard",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=colors["text_primary"]
        )
        self.page_title.pack(side="left", padx=30, pady=25)
        
        # Status indicator
        self.status_label = ctk.CTkLabel(
            self.header,
            text="● En ligne",
            font=ctk.CTkFont(size=14),
            text_color=colors["success"]
        )
        self.status_label.pack(side="right", padx=30, pady=25)
        
        # Zone de contenu
        self.content_area = ctk.CTkFrame(
            self.main_area,
            fg_color=colors["bg_primary"],
            corner_radius=0
        )
        self.content_area.grid(row=1, column=0, sticky="nsew")
        
        # Contenu par défaut (Dashboard)
        self._show_dashboard_content()
    
    def _on_page_change(self, page_id: str):
        """Gestionnaire de changement de page"""
        self.current_page = page_id
        self._update_page_content(page_id)
    
    def _update_page_content(self, page_id: str):
        """Met à jour le contenu selon la page sélectionnée"""
        colors = get_current_colors()
        
        # Mapping des titres de page
        page_titles = {
            "dashboard": "⌂ Dashboard",
            "monitoring": "◉ Monitoring Temps Réel", 
            "config": "⚙ Configuration",
            "logs": "▤ Logs & Historique",
            "diagnostics": "⚒ Diagnostics"
        }
        
        # Mettre à jour le titre
        self.page_title.configure(text=page_titles.get(page_id, "◇ Page"))
        
        # Vider la zone de contenu
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        # Afficher le contenu selon la page
        if page_id == "dashboard":
            self._show_dashboard_content()
        elif page_id == "monitoring":
            self._show_monitoring_content()
        elif page_id == "config":
            self._show_config_content()
        elif page_id == "logs":
            self._show_logs_content()
        elif page_id == "diagnostics":
            self._show_diagnostics_content()
        else:
            self._show_placeholder_content(page_id)
    
    def _show_dashboard_content(self):
        """🏠 Dashboard avancé avec métriques, graphiques et actions"""
        colors = get_current_colors()
        
        # Container principal avec grid
        main_container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configuration du grid
        main_container.grid_columnconfigure(0, weight=2)  # Colonne gauche plus large
        main_container.grid_columnconfigure(1, weight=1)  # Colonne droite
        main_container.grid_rowconfigure(0, weight=0)     # Header
        main_container.grid_rowconfigure(1, weight=1)     # Content principal
        
        # 📊 SECTION 1: MÉTRIQUES AVANCÉES
        self._create_advanced_metrics_section(main_container, colors)
        
        # 📈 SECTION 2: GRAPHIQUE MOCKUP  
        self._create_chart_mockup_section(main_container, colors)
        
        # ⚡ SECTION 3: QUICK ACTIONS
        self._create_quick_actions_section(main_container, colors)
        
        # 📋 SECTION 4: STATUS DÉTAILLÉ
        self._create_detailed_status_section(main_container, colors)

    def _create_advanced_metrics_section(self, parent, colors):
        """📊 Cards métriques avancées avec tendances"""
        metrics_frame = ctk.CTkFrame(
            parent,
            fg_color=colors["bg_secondary"],
            corner_radius=12,
            height=200
        )
        metrics_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        metrics_frame.grid_propagate(False)
        
        # Titre section
        title = ctk.CTkLabel(
            metrics_frame,
            text="▤ Métriques Temps Réel",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=colors["text_primary"]
        )
        title.pack(pady=(15, 10))
        
        # Container pour les cards
        cards_container = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        cards_container.pack(fill="x", padx=20, pady=(0, 15))
        
        # Données métriques avancées avec tendances
        metrics_data = [
            {
                "title": "Pipeline Status",
                "value": "● Actif",
                "detail": "16,577 LEDs",
                "trend": "↗ +2.1%",
                "color": colors["success"],
                "trend_color": colors["success"]
            },
            {
                "title": "Messages eHub",
                "value": "42.7/sec",
                "detail": "Dernière: 2ms",
                "trend": "↗ +15%",
                "color": colors["info"],
                "trend_color": colors["success"]
            },
            {
                "title": "Contrôleurs BC216",
                "value": "4/4 ●",
                "detail": "192.168.1.45-48",
                "trend": "● Stable",
                "color": colors["success"],
                "trend_color": colors["info"]
            },
            {
                "title": "Latence ArtNet",
                "value": "1.2ms",
                "detail": "Moy: 0.8ms",
                "trend": "↘ -5ms",
                "color": colors["warning"],
                "trend_color": colors["success"]
            },
            {
                "title": "Erreurs",
                "value": "0",
                "detail": "24h: 0",
                "trend": "● Aucune",
                "color": colors["success"],
                "trend_color": colors["success"]
            }
        ]
        
        for i, metric in enumerate(metrics_data):
            self._create_advanced_metric_card(cards_container, metric, colors, i)
    
    def _create_advanced_metric_card(self, parent, metric, colors, index):
        """Crée une card métrique avancée"""
        card = ctk.CTkFrame(
            parent,
            width=200,
            height=120,
            fg_color=colors["bg_tertiary"],
            corner_radius=10
        )
        card.pack(side="left", padx=8, pady=5)
        card.pack_propagate(False)
        
        # Titre
        title_label = ctk.CTkLabel(
            card,
            text=metric["title"],
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=colors["text_secondary"]
        )
        title_label.pack(pady=(12, 4))
        
        # Valeur principale
        value_label = ctk.CTkLabel(
            card,
            text=metric["value"],
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=metric["color"]
        )
        value_label.pack(pady=(0, 2))
        
        # Détail
        detail_label = ctk.CTkLabel(
            card,
            text=metric["detail"],
            font=ctk.CTkFont(size=10),
            text_color=colors["text_disabled"]
        )
        detail_label.pack(pady=(0, 4))
        
        # Tendance
        trend_label = ctk.CTkLabel(
            card,
            text=metric["trend"],
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=metric["trend_color"]
        )
        trend_label.pack()

    def _create_chart_mockup_section(self, parent, colors):
        """📈 Zone graphique mockup avec axes simulés"""
        chart_frame = ctk.CTkFrame(
            parent,
            fg_color=colors["bg_secondary"],
            corner_radius=12
        )
        chart_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        
        # Titre graphique
        chart_title = ctk.CTkLabel(
            chart_frame,
            text="▲ Activité Pipeline (60s)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=colors["text_primary"]
        )
        chart_title.pack(pady=(15, 10))
        
        # Zone graphique simulée
        chart_area = ctk.CTkFrame(
            chart_frame,
            fg_color=colors["bg_primary"],
            corner_radius=8,
            height=300
        )
        chart_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Simuler des axes et données
        self._create_chart_mockup(chart_area, colors)
        
        # Légende
        legend_frame = ctk.CTkFrame(chart_area, fg_color="transparent")
        legend_frame.pack(side="bottom", pady=10)
        
        legend_items = [
            ("● Messages eHub", colors["chart_line1"]),
            ("● Latence (ms)", colors["chart_line2"]), 
            ("● Erreurs", colors["error"])
        ]
        
        for text, color in legend_items:
            ctk.CTkLabel(
                legend_frame,
                text=text,
                font=ctk.CTkFont(size=10),
                text_color=color
            ).pack(side="left", padx=15)

    def _create_chart_mockup(self, parent, colors):
        """Crée un mockup de graphique avec lignes simulées"""
        # Axes Y simulés (labels)
        y_axis_frame = ctk.CTkFrame(parent, fg_color="transparent", width=40)
        y_axis_frame.pack(side="left", fill="y", padx=(10, 5))
        
        y_labels = ["100", "80", "60", "40", "20", "0"]
        for label in y_labels:
            ctk.CTkLabel(
                y_axis_frame,
                text=label,
                font=ctk.CTkFont(size=9),
                text_color=colors["text_disabled"]
            ).pack(expand=True)
        
        # Zone de données simulée
        data_area = ctk.CTkFrame(parent, fg_color=colors["chart_grid"], corner_radius=4)
        data_area.pack(side="left", fill="both", expand=True, padx=5, pady=10)
        
        # Simulation lignes de données (texte pour mockup)
        mockup_text = ctk.CTkLabel(
            data_area,
            text="╭─────────────────────────╮\n│  ∿∿∿∿∿ Données temps réel  │\n│     ╱╲    ╱╲╱╲╱╲    │\n│    ╱  ╲  ╱      ╲   │\n│   ╱    ╲╱        ╲  │\n│  ╱              ╲ │\n│ ╱                ╲│\n│╱                  ╲\n╰─────────────────────────╯\n   60s  45s  30s  15s  0s",
            font=ctk.CTkFont(size=10, family="monospace"),
            text_color=colors["text_disabled"],
            justify="center"
        )
        mockup_text.pack(expand=True)

    def _create_quick_actions_section(self, parent, colors):
        """⚡ Section actions rapides"""
        actions_frame = ctk.CTkFrame(
            parent,
            fg_color=colors["bg_secondary"],
            corner_radius=12
        )
        actions_frame.grid(row=1, column=1, sticky="nsew")
        
        # Titre
        actions_title = ctk.CTkLabel(
            actions_frame,
            text="▶ Actions Rapides",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=colors["text_primary"]
        )
        actions_title.pack(pady=(15, 20))
        
        # Boutons d'action
        action_buttons = [
            ("▶ Start Monitoring", colors["success"], "start"),
            ("⏸ Pause Monitoring", colors["warning"], "pause"),
            ("↻ Reset Stats", colors["info"], "reset"),
            ("◉ Test Pipeline", colors["accent_primary"], "test"),
            ("⚙ Configuration", colors["text_secondary"], "config"),
            ("▤ Rapports", colors["text_secondary"], "reports")
        ]
        
        for text, color, action in action_buttons:
            btn = ctk.CTkButton(
                actions_frame,
                text=text,
                font=ctk.CTkFont(size=14),
                fg_color=color,
                hover_color=colors["accent_hover"],
                corner_radius=8,
                height=35,
                command=lambda a=action: self._handle_quick_action(a)
            )
            btn.pack(fill="x", padx=20, pady=5)
    
    def _create_detailed_status_section(self, parent, colors):
        """📋 Status détaillé en bas"""
        status_frame = ctk.CTkFrame(
            parent,
            fg_color=colors["bg_secondary"],
            corner_radius=12,
            height=100
        )
        status_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(15, 0))
        status_frame.grid_propagate(False)
        
        # Titre
        status_title = ctk.CTkLabel(
            status_frame,
            text="▤ Status Système Détaillé",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["text_primary"]
        )
        status_title.pack(pady=(10, 5))
        
        # Informations détaillées
        details_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        details_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        status_details = [
            "◉ Pipeline: Étapes 0-4 opérationnelles",
            "⚙ BC216: 192.168.1.45-48 (4/4 connectés)",
            "◉ UDP: Port 8765 ouvert, IP WSL détectée",
            "▲ Performance: CPU 2.1%, RAM 156MB",
            "● Uptime: 2h 34min (depuis 23:56)"
        ]
        
        for i, detail in enumerate(status_details):
            ctk.CTkLabel(
                details_frame,
                text=detail,
                font=ctk.CTkFont(size=11),
                text_color=colors["text_secondary"]
            ).pack(side="left", padx=15)
    
    def _handle_quick_action(self, action):
        """Gestionnaire des actions rapides"""
        print(f"⚡ [QuickAction] Action déclenchée: {action}")
        
        # Pour l'instant, juste des logs - sera connecté au pipeline plus tard
        action_messages = {
            "start": "▶ Démarrage du monitoring...",
            "pause": "⏸ Pause du monitoring...", 
            "reset": "↻ Reset des statistiques...",
            "test": "◉ Test du pipeline en cours...",
            "config": "⚙ Ouverture configuration...",
            "reports": "📊 Génération des rapports..."
        }
        
        message = action_messages.get(action, f"Action: {action}")
        print(f"💬 [Dashboard] {message}")
    
    def _show_placeholder_content(self, page_id: str):
        """Contenu placeholder pour les pages en développement"""
        colors = get_current_colors()
        
        placeholder = ctk.CTkFrame(
            self.content_area,
            fg_color=colors["bg_secondary"],
            corner_radius=15
        )
        placeholder.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Icone selon la page
        page_icons = {
            "monitoring": "◉",
            "config": "⚙", 
            "logs": "▤",
            "diagnostics": "⚒"
        }
        
        icon = page_icons.get(page_id, "◇")
        
        ctk.CTkLabel(
            placeholder,
            text=f"{icon}",
            font=ctk.CTkFont(size=80),
        ).pack(pady=(100, 20))
        
        ctk.CTkLabel(
            placeholder,
            text=f"Page {page_id.title()}",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=colors["text_primary"]
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            placeholder,
            text="▶ En cours de développement...\n● Phase 1 - Setup Framework terminée !",
            font=ctk.CTkFont(size=16),
            text_color=colors["text_secondary"],
            justify="center"
        ).pack(pady=(0, 100))
    
    # Méthodes placeholder pour les autres pages
    def _show_monitoring_content(self):
        self._show_placeholder_content("monitoring")
    
    def _show_config_content(self):
        self._show_placeholder_content("config")
    
    def _show_logs_content(self):
        self._show_placeholder_content("logs")
    
    def _show_diagnostics_content(self):
        self._show_placeholder_content("diagnostics")

if __name__ == "__main__":
    # Test de la fenêtre principale
    app = MainWindow()
    app.mainloop()