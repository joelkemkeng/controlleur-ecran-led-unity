"""
🏠 Fenêtre principale moderne avec navigation sidebar
Architecture modulaire pour application de monitoring eHub
"""

import customtkinter as ctk
from typing import Dict, Callable, Optional
import sys
import os
import time

# Import du gestionnaire de thèmes
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.themes import get_theme_manager, get_current_colors, ThemeMode

# Import de la page d'écran virtuel
from .virtual_screen import MonitoringAdvancedPage

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
            ("virtual_screen", "🖥️ Écran Virtuel", "Affichage matriciel LED 128x128"),
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
    Architecture moderne avec sidebar navigation + monitoring intégré
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
        
        # 🔧 INTÉGRATION MONITORING
        self.pipeline_monitor = None
        self.metrics_collector = None
        self.monitoring_active = False
        self.update_job = None
        
        # 📈 Variables pour graphiques temps réel
        self.main_chart = None
        self.chart_update_timer = None
        self.last_chart_update = 0
        
        # Créer l'interface
        self._create_layout()
        self._create_content_area()
        
        # Initialiser le monitoring
        self._initialize_monitoring()
        
        print("🏠 [MainWindow] Fenêtre principale initialisée")
    
    def _initialize_monitoring(self):
        """🔧 Initialise le système de monitoring"""
        try:
            # Import des modules de monitoring
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
            from pipeline_monitor import PipelineMonitor
            from metrics_collector import MetricsCollector
            
            # Initialiser les composants
            self.pipeline_monitor = PipelineMonitor()
            self.metrics_collector = MetricsCollector(history_size=300)
            
            print("✅ [MainWindow] Monitoring initialisé")
            
        except Exception as e:
            print(f"❌ [MainWindow] Erreur init monitoring: {e}")
            # L'interface fonctionne quand même en mode mockup
    
    def _start_monitoring_updates(self):
        """▶ Démarre les mises à jour temps réel de l'UI"""
        if self.update_job:
            return  # Déjà en cours
        
        def update_ui():
            if self.monitoring_active and self.pipeline_monitor:
                self._update_dashboard_with_real_data()
            
            # Programmer la prochaine mise à jour
            self.update_job = self.after(1000, update_ui)  # 1 seconde
        
        self.update_job = self.after(100, update_ui)  # Démarrer dans 100ms
        print("▶ [MainWindow] Mises à jour UI démarrées")
    
    def _stop_monitoring_updates(self):
        """⏸ Arrête les mises à jour temps réel"""
        if self.update_job:
            self.after_cancel(self.update_job)
            self.update_job = None
        print("⏸ [MainWindow] Mises à jour UI arrêtées")
    
    def _update_dashboard_with_real_data(self):
        """📊 Met à jour le dashboard avec les vraies données"""
        if not self.pipeline_monitor:
            return
        
        try:
            # Récupérer les données du pipeline
            monitoring_data = self.pipeline_monitor.get_current_data()
            if monitoring_data:
                # Ajouter aux métriques
                self.metrics_collector.add_metric_point("packets_per_second", monitoring_data.packets_received)
                self.metrics_collector.add_metric_point("entities_processed", monitoring_data.entities_processed)
                self.metrics_collector.add_metric_point("latency_ms", monitoring_data.latency_ms)
                self.metrics_collector.add_metric_point("bytes_per_second", monitoring_data.bytes_per_second)
                self.metrics_collector.add_metric_point("errors_count", monitoring_data.errors_count)
                self.metrics_collector.add_metric_point("controllers_active", monitoring_data.controllers_active)
                
                # Mettre à jour l'affichage si on est sur le dashboard
                if self.current_page == "dashboard":
                    self._refresh_dashboard_metrics(monitoring_data)
            
        except Exception as e:
            print(f"❌ [MainWindow] Erreur mise à jour données: {e}")
    
    def _refresh_dashboard_metrics(self, data):
        """🔄 Rafraîchit l'affichage des métriques du dashboard"""
        try:
            # Pour l'instant, mise à jour via console et stockage des données
            # Les widgets seront mis à jour dynamiquement dans une version future
            
            # Stocker les dernières données pour l'affichage
            if not hasattr(self, 'current_metrics'):
                self.current_metrics = {}
            
            self.current_metrics.update({
                'packets_per_second': data.packets_received,
                'latency_ms': data.latency_ms,
                'entities_processed': data.entities_processed,
                'controllers_active': data.controllers_active,
                'errors_count': data.errors_count,
                'pipeline_status': data.pipeline_status,
                'bytes_per_second': data.bytes_per_second
            })
            
            # Mettre à jour le collecteur de métriques
            if self.metrics_collector:
                for metric_name, value in self.current_metrics.items():
                    if isinstance(value, (int, float)):
                        self.metrics_collector.add_metric_point(metric_name, float(value))
            
            # 📈 Mettre à jour le graphique principal si disponible
            if hasattr(self, 'main_chart') and self.main_chart:
                try:
                    self.main_chart.update_data(data.timestamp, {
                        'packets_per_second': float(data.packets_received),
                        'latency_ms': float(data.latency_ms),
                        'entities_processed': float(data.entities_processed) / 100.0  # Échelle pour visualisation
                    })
                except Exception as chart_error:
                    print(f"⚠️ [Dashboard] Erreur mise à jour graphique: {chart_error}")
            
            # Log pour debug (sera remplacé par mise à jour UI)
            print(f"📊 [Dashboard] Métriques: {data.packets_received} pkt/s, "
                  f"{data.latency_ms:.1f}ms latence, {data.entities_processed} entités, "
                  f"{data.controllers_active} contrôleurs, {data.errors_count} erreurs")
            
            # Mettre à jour le titre de status si nécessaire
            if hasattr(self, 'status_label'):
                colors = get_current_colors()
                if data.errors_count > 0:
                    status_text = f"⚠️ {data.errors_count} erreur(s)"
                    status_color = colors["warning"]
                elif self.monitoring_active:
                    status_text = "● Monitoring actif" 
                    status_color = colors["success"]
                else:
                    status_text = "● En ligne"
                    status_color = colors["info"]
                
                self.status_label.configure(text=status_text, text_color=status_color)
            
        except Exception as e:
            print(f"❌ [Dashboard] Erreur mise à jour métriques: {e}")

    def _schedule_chart_updates(self):
        """🔄 Programme les mises à jour automatiques des graphiques"""
        if self.main_chart and self.monitoring_active:
            try:
                # Mettre à jour toutes les 2 secondes
                current_time = time.time()
                if current_time - self.last_chart_update >= 2.0:
                    if hasattr(self, 'current_metrics') and self.current_metrics:
                        # Utiliser les dernières métriques disponibles
                        metrics_data = {
                            'packets_per_second': self.current_metrics.get('packets_per_second', 0),
                            'latency_ms': self.current_metrics.get('latency_ms', 0),
                            'entities_processed': self.current_metrics.get('entities_processed', 0) / 100.0
                        }
                        self.main_chart.update_data(current_time, metrics_data)
                        self.last_chart_update = current_time
                
                # Programmer la prochaine mise à jour
                self.chart_update_timer = self.after(1000, self._schedule_chart_updates)
                
            except Exception as e:
                print(f"⚠️ [Charts] Erreur programmation mise à jour: {e}")
        else:
            # Arrêter les mises à jour si pas de monitoring
            if self.chart_update_timer:
                self.after_cancel(self.chart_update_timer)
                self.chart_update_timer = None
    
    def destroy(self):
        """🔌 Nettoyage propre à la fermeture"""
        print("🔌 [MainWindow] Fermeture en cours...")
        
        # Arrêter le monitoring
        self._stop_monitoring_updates()
        if self.pipeline_monitor:
            self.pipeline_monitor.stop_monitoring()
        
        # Fermer la fenêtre
        super().destroy()
        print("🔌 [MainWindow] Fermé proprement")
    
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
            "virtual_screen": "🖥️ Écran Virtuel LED",
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
        elif page_id == "virtual_screen":
            self._show_virtual_screen_content()
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
        """📈 Zone graphique avec matplotlib intégré"""
        chart_frame = ctk.CTkFrame(
            parent,
            fg_color=colors["bg_secondary"],
            corner_radius=12
        )
        chart_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        
        # Titre graphique
        chart_title = ctk.CTkLabel(
            chart_frame,
            text="▲ Activité Pipeline (Temps Réel)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=colors["text_primary"]
        )
        chart_title.pack(pady=(15, 10))
        
        try:
            # Import du widget graphique
            import sys
            import os
            chart_path = os.path.join(os.path.dirname(__file__), 'chart_widgets.py')
            if os.path.exists(chart_path):
                from ui.chart_widgets import create_monitoring_chart
                
                # Créer le graphique temps réel
                self.main_chart = create_monitoring_chart(
                    chart_frame, 
                    chart_type="line",
                    title="Métriques Pipeline",
                    width=550,
                    height=280
                )
                self.main_chart.pack(fill="both", expand=True, padx=15, pady=(0, 15))
                
                # Démarrer l'animation
                self.main_chart.start_animation(interval=2000)  # Mise à jour toutes les 2 secondes
                
                print("📈 [Dashboard] Graphique matplotlib intégré")
            else:
                # Fallback sur le mockup si le widget n'existe pas
                self._create_chart_fallback(chart_frame, colors)
                
        except Exception as e:
            print(f"❌ [Dashboard] Erreur graphique matplotlib: {e}")
            # Fallback sur le mockup
            self._create_chart_fallback(chart_frame, colors)
    
    def _create_chart_fallback(self, chart_frame, colors):
        """Fallback mockup si matplotlib ne fonctionne pas"""
        # Zone graphique simulée (code existant)
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
        """🎛️ Gestionnaire des actions rapides connecté au monitoring"""
        print(f"⚡ [QuickAction] Action déclenchée: {action}")
        
        try:
            if action == "start":
                self._start_pipeline_monitoring()
            elif action == "pause":
                self._pause_pipeline_monitoring()
            elif action == "reset":
                self._reset_monitoring_stats()
            elif action == "test":
                self._test_pipeline()
            elif action == "config":
                self._open_configuration()
            elif action == "reports":
                self._generate_reports()
            else:
                print(f"⚠️ [QuickAction] Action non reconnue: {action}")
        
        except Exception as e:
            print(f"❌ [QuickAction] Erreur action {action}: {e}")
    
    def _start_pipeline_monitoring(self):
        """▶ Démarre le monitoring du pipeline"""
        if self.monitoring_active:
            print("⚠️ [Monitoring] Déjà en cours")
            return
        
        if not self.pipeline_monitor:
            print("❌ [Monitoring] Pipeline monitor non initialisé")
            return
        
        try:
            # Démarrer le monitoring pipeline
            success = self.pipeline_monitor.start_monitoring()
            if success:
                self.monitoring_active = True
                self._start_monitoring_updates()
                self._schedule_chart_updates()  # 📈 Démarrer les mises à jour des graphiques
                print("✅ [Monitoring] Pipeline démarré avec succès")
                
                # Mettre à jour le status dans l'UI
                colors = get_current_colors()
                self.status_label.configure(text="● Monitoring actif", text_color=colors["success"])
                
                # Mettre à jour les boutons
                self._update_monitoring_buttons_state(True)
            else:
                print("❌ [Monitoring] Échec démarrage pipeline")
                
        except Exception as e:
            print(f"❌ [Monitoring] Erreur démarrage: {e}")
    
    def _pause_pipeline_monitoring(self):
        """⏸ Met en pause le monitoring"""
        if not self.monitoring_active:
            print("⚠️ [Monitoring] Pas en cours")
            return
        
        try:
            self.pipeline_monitor.stop_monitoring()
            self.monitoring_active = False
            self._stop_monitoring_updates()
            
            # 📈 Arrêter les mises à jour des graphiques
            if self.chart_update_timer:
                self.after_cancel(self.chart_update_timer)
                self.chart_update_timer = None
                
            print("⏸ [Monitoring] Pipeline mis en pause")
            
            # Mettre à jour le status dans l'UI
            colors = get_current_colors()
            self.status_label.configure(text="⏸ En pause", text_color=colors["warning"])
            
            # Mettre à jour les boutons
            self._update_monitoring_buttons_state(False)
            
        except Exception as e:
            print(f"❌ [Monitoring] Erreur pause: {e}")
    
    def _update_monitoring_buttons_state(self, is_active: bool):
        """Met à jour l'état visuel des boutons selon le monitoring"""
        # Cette méthode sera appelée pour changer l'apparence des boutons
        # Peut être étendue plus tard pour désactiver/activer certains boutons
        pass
    
    def _reset_monitoring_stats(self):
        """↻ Reset les statistiques"""
        try:
            if self.pipeline_monitor:
                self.pipeline_monitor.send_command({"action": "reset_stats"})
            
            if self.metrics_collector:
                self.metrics_collector.clear_metrics()
            
            print("✅ [Monitoring] Statistiques remises à zéro")
            
        except Exception as e:
            print(f"❌ [Monitoring] Erreur reset: {e}")
    
    def _test_pipeline(self):
        """◉ Test du pipeline"""
        try:
            if self.pipeline_monitor:
                self.pipeline_monitor.send_command({"action": "test_pipeline"})
                print("◉ [Pipeline] Test en cours...")
            else:
                print("⚠️ [Pipeline] Monitor non disponible pour test")
                
        except Exception as e:
            print(f"❌ [Pipeline] Erreur test: {e}")
    
    def _open_configuration(self):
        """⚙ Ouvre la page de configuration"""
        self._on_page_change("config")
        print("⚙ [Navigation] Ouverture page configuration")
    
    def _generate_reports(self):
        """📊 Génère les rapports"""
        try:
            if self.metrics_collector:
                stats = self.metrics_collector.get_statistics_summary()
                print("📊 [Reports] Génération rapport...")
                for metric, data in stats.items():
                    print(f"   {metric}: {data['current']:.1f} (trend: {data['trend']})")
            else:
                print("⚠️ [Reports] Collecteur métriques non disponible")
                
        except Exception as e:
            print(f"❌ [Reports] Erreur génération: {e}")
    
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
    
    def _show_virtual_screen_content(self):
        """🖥️ Affiche la page d'écran virtuel LED"""
        try:
            # Créer la page d'écran virtuel
            self.virtual_screen_page = MonitoringAdvancedPage(
                self.content_area,
                fg_color="transparent"
            )
            self.virtual_screen_page.pack(fill="both", expand=True)
            
            # Démarrer le monitoring automatiquement
            self.virtual_screen_page.start_monitoring()
            
            # Connecter au pipeline de données si disponible
            if hasattr(self, 'pipeline_monitor') and self.pipeline_monitor:
                # Connecter les données ArtNet simulées à l'écran virtuel
                def artnet_data_callback(universe, channel_data):
                    if self.virtual_screen_page and self.virtual_screen_page.virtual_screen:
                        self.virtual_screen_page.update_artnet_data(universe, channel_data)
                
                self.pipeline_monitor.set_artnet_callback(artnet_data_callback)
                print("📡 [MainWindow] Pipeline ArtNet connecté à l'écran virtuel")
            
            print("🖥️ [MainWindow] Page d'écran virtuel chargée")
            
        except Exception as e:
            print(f"❌ [MainWindow] Erreur chargement écran virtuel: {e}")
            self._show_placeholder_content("virtual_screen")
    
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