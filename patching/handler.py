"""
patching/handler.py - Système de patchs DMX dynamique et historisé

Ce module fournit la classe PatchHandler pour appliquer dynamiquement des patchs DMX (redirections de canaux)
sur le pipeline LED, sans modifier la configuration globale. Il permet de charger/sauvegarder des patchs depuis/vers CSV,
d'enregistrer chaque patch appliqué dans un dossier d'historique (patch_record/), et de rejouer un patch au choix ou le dernier patch appliqué.

Portabilité :
- Fonctionne sur Linux, Mac, Windows, Raspbian
- Aucun module exotique requis (utilise csv, os, datetime)

Format CSV attendu :
--------------------
Source_Channel,Target_Channel
1,389
2,390

Exemple d'utilisation :
----------------------
from patching.handler import PatchHandler
handler = PatchHandler()
handler.load_patches_from_csv('patches.csv')
handler.enabled = True
patched_packets = handler.apply_patches(dmx_packets)
handler.record_patch('patch_record/')  # Sauvegarde automatique avec timestamp
# Pour rejouer un patch :
handler.replay_patch('patch_record/patch_2024-06-21_15-30-00.csv')

Explication pédagogique :
------------------------
- Un patch DMX permet de rediriger dynamiquement les valeurs d'un canal source vers un canal cible (ex : 1→389)
- Utile pour contourner rapidement une panne physique sans toucher à la config Excel ou au mapping principal
- L'historique permet de rejouer un patch précédent ou le dernier patch appliqué
"""

import csv
import os
from datetime import datetime

class PatchHandler:
    """
    Système de patchs DMX dynamique et historisé.
    Permet de charger, appliquer, enregistrer et rejouer des patchs DMX (canal source → canal cible).
    """
    def __init__(self):
        self.patches = {}  # source_channel -> target_channel
        self.enabled = False
        self.last_patch_path = None

    def load_patches_from_csv(self, filepath: str):
        """
        Charge les patchs depuis un fichier CSV (format : Source_Channel,Target_Channel).
        Si le fichier n'existe pas, aucun patch n'est chargé.
        """
        self.patches.clear()
        try:
            with open(filepath, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) >= 2:
                        source = int(row[0])
                        target = int(row[1])
                        self.patches[source] = target
            self.last_patch_path = filepath
        except FileNotFoundError:
            pass

    def save_patches_to_csv(self, filepath: str):
        """
        Sauvegarde les patchs actuels dans un fichier CSV (format : Source_Channel,Target_Channel).
        """
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Source_Channel', 'Target_Channel'])
            for source, target in self.patches.items():
                writer.writerow([source, target])

    def apply_patches(self, dmx_packets):
        """
        Applique les patchs aux paquets DMX (avant envoi ArtNet).
        Pour chaque patch (source→target), copie la valeur du canal source vers le canal cible.
        Si le patching est désactivé ou vide, retourne les paquets inchangés.
        """
        if not self.enabled or not self.patches:
            return dmx_packets
        patched_packets = []
        for packet in dmx_packets:
            new_channels = dict(packet.channels)
            for source_ch, target_ch in self.patches.items():
                if source_ch in packet.channels:
                    new_channels[target_ch] = packet.channels[source_ch]
            patched_packet = type(packet)(
                controller_ip=packet.controller_ip,
                universe=packet.universe,
                channels=new_channels
            )
            patched_packets.append(patched_packet)
        return patched_packets

    def add_patch(self, source_channel: int, target_channel: int):
        """
        Ajoute un patch dynamiquement (source→target).
        """
        self.patches[source_channel] = target_channel

    def remove_patch(self, source_channel: int):
        """
        Supprime un patch (par canal source).
        """
        if source_channel in self.patches:
            del self.patches[source_channel]

    def record_patch(self, record_dir: str = 'patch_record'):
        """
        Enregistre le patch courant dans un fichier CSV dans le dossier d'historique (patch_record/),
        avec un nom unique basé sur la date et l'heure.
        Retourne le chemin du fichier créé.
        """
        os.makedirs(record_dir, exist_ok=True)
        now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'patch_{now}.csv'
        path = os.path.join(record_dir, filename)
        self.save_patches_to_csv(path)
        self.last_patch_path = path
        return path

    def replay_patch(self, patch_path: str = None):
        """
        Recharge un patch depuis un fichier CSV d'historique (ou le dernier patch enregistré si non spécifié).
        """
        if patch_path is None:
            patch_path = self.last_patch_path
        if patch_path:
            self.load_patches_from_csv(patch_path)
            self.enabled = True 