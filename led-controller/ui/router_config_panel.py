from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QCheckBox, QPushButton, QSpinBox,
    QScrollArea, QFrame, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

from core.router_manager import RouterManager

class RouterConfigCard(QFrame):
    """Carte de configuration pour un routeur individuel"""
    
    config_changed = pyqtSignal(int, str, str, bool, int)  # index, name, ip, enabled, port
    delete_requested = pyqtSignal(int)  # index
    
    def __init__(self, index: int, router_config, parent=None):
        super().__init__(parent)
        self.index = index
        self.router_config = router_config
        self.setup_ui()
        
    def setup_ui(self):
        """Configure l'interface de la carte"""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 12px;
                margin: 4px;
            }
            QFrame:hover {
                border-color: #606060;
                background-color: #333333;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # En-tête avec nom et checkbox d'activation
        header_layout = QHBoxLayout()
        
        self.enabled_checkbox = QCheckBox()
        self.enabled_checkbox.setChecked(self.router_config.enabled)
        self.enabled_checkbox.stateChanged.connect(self.on_config_changed)
        header_layout.addWidget(self.enabled_checkbox)
        
        name_label = QLabel(f"Routeur {self.index + 1}")
        name_label.setStyleSheet("font-weight: bold; color: #ffffff; font-size: 14px;")
        header_layout.addWidget(name_label)
        
        header_layout.addStretch()
        
        # Indicateur de statut
        self.status_label = QLabel("●")
        self.status_label.setStyleSheet("color: #51cf66; font-size: 16px;")
        header_layout.addWidget(self.status_label)
        
        # Bouton de suppression (croix)
        self.delete_btn = QPushButton("×")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                min-width: 24px;
                max-width: 24px;
                min-height: 24px;
                max-height: 24px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.delete_btn.clicked.connect(self.on_delete_clicked)
        header_layout.addWidget(self.delete_btn)
        
        layout.addLayout(header_layout)
        
        # Configuration des champs
        config_layout = QGridLayout()
        
        # Nom du routeur
        config_layout.addWidget(QLabel("Nom:"), 0, 0)
        self.name_edit = QLineEdit(self.router_config.name)
        self.name_edit.setStyleSheet("""
            QLineEdit {
                color: #ffffff;
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
            }
        """)
        self.name_edit.textChanged.connect(self.on_config_changed)
        config_layout.addWidget(self.name_edit, 0, 1)
        
        # Adresse IP
        config_layout.addWidget(QLabel("IP:"), 1, 0)
        self.ip_edit = QLineEdit(self.router_config.ip)
        self.ip_edit.setStyleSheet("""
            QLineEdit {
                color: #ffffff;
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
            }
        """)
        self.ip_edit.textChanged.connect(self.on_config_changed)
        config_layout.addWidget(self.ip_edit, 1, 1)
        
        # Port
        config_layout.addWidget(QLabel("Port:"), 2, 0)
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(self.router_config.port)
        self.port_spin.setStyleSheet("""
            QSpinBox {
                color: #ffffff;
                background-color: #1e1e1e;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px;
            }
        """)
        self.port_spin.valueChanged.connect(self.on_config_changed)
        config_layout.addWidget(self.port_spin, 2, 1)
        
        layout.addLayout(config_layout)
        
        # Mise à jour du statut
        self.update_status()
        
    def on_config_changed(self):
        """Appelé quand la configuration change"""
        self.update_status()
        self.config_changed.emit(
            self.index,
            self.name_edit.text(),
            self.ip_edit.text(),
            self.enabled_checkbox.isChecked(),
            self.port_spin.value()
        )
    
    def on_delete_clicked(self):
        """Appelé quand on clique sur le bouton de suppression"""
        self.delete_requested.emit(self.index)
    
    def update_status(self):
        """Met à jour l'indicateur de statut"""
        if self.enabled_checkbox.isChecked():
            self.status_label.setText("●")
            self.status_label.setStyleSheet("color: #51cf66; font-size: 16px;")
        else:
            self.status_label.setText("○")
            self.status_label.setStyleSheet("color: #868e96; font-size: 16px;")

class RouterConfigPanel(QWidget):
    """Panneau principal de configuration des routeurs"""
    
    config_updated = pyqtSignal()
    
    def __init__(self, router_manager: RouterManager, parent=None):
        super().__init__(parent)
        self.router_manager = router_manager
        self.router_cards = []
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        """Configure l'interface principale"""
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("Configuration des Routeurs LED")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #ffffff;
            padding: 10px;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # Zone de défilement pour les cartes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.cards_widget = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_widget)
        scroll_area.setWidget(self.cards_widget)
        
        layout.addWidget(scroll_area)
        
        # Boutons de contrôle
        buttons_layout = QHBoxLayout()
        
        # Bouton d'ajout
        self.add_btn = QPushButton("+ Ajouter Routeur")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        self.add_btn.clicked.connect(self.add_router)
        buttons_layout.addWidget(self.add_btn)
        
        buttons_layout.addStretch()
        
        # Boutons de sauvegarde/réinitialisation
        self.save_btn = QPushButton("Sauvegarder")
        self.save_btn.setStyleSheet("""
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
        self.save_btn.clicked.connect(self.save_config)
        buttons_layout.addWidget(self.save_btn)
        
        self.reset_btn = QPushButton("Réinitialiser")
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
        self.reset_btn.clicked.connect(self.reset_config)
        buttons_layout.addWidget(self.reset_btn)
        
        layout.addLayout(buttons_layout)
        
        # Informations de mapping
        mapping_layout = QHBoxLayout()
        mapping_layout.addStretch()
        
        self.mapping_info = QLabel()
        self.mapping_info.setStyleSheet("""
            color: #b0b0b0;
            font-size: 12px;
            padding: 8px;
            background-color: #1a1a1a;
            border-radius: 4px;
        """)
        mapping_layout.addWidget(self.mapping_info)
        
        layout.addLayout(mapping_layout)
        
    def load_config(self):
        """Charge la configuration et crée les cartes"""
        # Nettoyer les cartes existantes
        for card in self.router_cards:
            self.cards_layout.removeWidget(card)
            card.deleteLater()
        self.router_cards.clear()
        
        # Créer les nouvelles cartes
        for i, router in enumerate(self.router_manager.routers):
            card = RouterConfigCard(i, router)
            card.config_changed.connect(self.on_router_config_changed)
            card.delete_requested.connect(self.on_router_delete_requested)
            self.cards_layout.addWidget(card)
            self.router_cards.append(card)
        
        # Mettre à jour les indices des cartes
        self.update_card_indices()
        self.update_mapping_info()
    
    def update_card_indices(self):
        """Met à jour les indices des cartes après suppression/ajout"""
        for i, card in enumerate(self.router_cards):
            card.index = i
            # Mettre à jour le nom affiché
            name_label = card.findChild(QLabel, "")
            if name_label:
                name_label.setText(f"Routeur {i + 1}")
        
    def on_router_config_changed(self, index: int, name: str, ip: str, enabled: bool, port: int):
        """Appelé quand la configuration d'un routeur change"""
        self.router_manager.update_router(index, name, ip, enabled, port)
        self.update_mapping_info()
        self.config_updated.emit()
        
    def save_config(self):
        """Sauvegarde la configuration"""
        if self.router_manager.save_config():
            QMessageBox.information(self, "Succès", "Configuration sauvegardée avec succès!")
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de la sauvegarde de la configuration.")
            
    def reset_config(self):
        """Réinitialise la configuration par défaut"""
        reply = QMessageBox.question(
            self, "Confirmation",
            "Voulez-vous vraiment réinitialiser la configuration par défaut ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.router_manager.reset_to_default():
                self.load_config()
                QMessageBox.information(self, "Succès", "Configuration réinitialisée!")
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de la réinitialisation.")
            
    def update_mapping_info(self):
        """Met à jour les informations de mapping"""
        info = self.router_manager.get_mapping_info()
        enabled_count = self.router_manager.get_enabled_count()
        
        text = f"Routeurs actifs: {enabled_count}/{len(self.router_manager.routers)} | "
        text += f"Bandes totales: {info['total_bands']} | "
        text += f"Univers Art-Net: {info['total_bands'] * 2}"
        
        self.mapping_info.setText(text)
    
    def add_router(self):
        """Ajoute un nouveau routeur"""
        if self.router_manager.add_router():
            self.load_config()
            QMessageBox.information(self, "Succès", "Nouveau routeur ajouté!")
        else:
            QMessageBox.critical(self, "Erreur", "Erreur lors de l'ajout du routeur.")
    
    def on_router_delete_requested(self, index: int):
        """Appelé quand on demande la suppression d'un routeur"""
        # Vérifier qu'on ne supprime pas tous les routeurs
        if len(self.router_manager.routers) <= 1:
            QMessageBox.warning(self, "Attention", "Impossible de supprimer le dernier routeur. Au moins un routeur doit rester actif.")
            return
        
        # Confirmation
        router_name = self.router_manager.routers[index].name
        message = f"Voulez-vous vraiment supprimer le routeur '{router_name}' ?"
        reply = QMessageBox.question(
            self, "Confirmation", message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.router_manager.remove_router(index):
                self.load_config()
                QMessageBox.information(self, "Succès", f"Routeur '{router_name}' supprimé!")
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de la suppression.") 