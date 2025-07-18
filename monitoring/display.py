"""
monitoring/display.py - Affichage temps réel du pipeline LED

Ce module fournit la classe MonitoringDisplay pour afficher en temps réel les données reçues, mappées et envoyées
par le routeur LED (eHuB, DMX, ArtNet). Il permet de diagnostiquer rapidement les problèmes de mapping, de routage
ou de réseau, et d'obtenir des statistiques globales sur le pipeline.

Portabilité :
- Fonctionne sur Linux, Mac, Windows, Raspbian
- Aucun module exotique requis

Exemple d'utilisation :
    >>> from monitoring.display import MonitoringDisplay
    >>> monitor = MonitoringDisplay()
    >>> monitor.log_ehub_data([EntityUpdate(1,255,0,0,0)])
    >>> monitor.log_dmx_data([DMXPacket('192.168.1.45',0,{1:255,2:0,3:0})])
    >>> monitor.log_artnet_send([DMXPacket('192.168.1.45',0,{1:255,2:0,3:0})])
    >>> monitor.display_stats()

Format des logs affichés :
-------------------------
Chaque appel à une méthode de log affiche une ou plusieurs lignes dans la console, au format suivant :

- [eHuB] <N> entités reçues
    Entité <id>: RGB(<r>,<g>,<b>)
  Exemple :
    [eHuB] 2 entités reçues
      Entité 1: RGB(255,0,0)
      Entité 2: RGB(0,255,0)

- [DMX] <N> paquets générés
    <IP> U<univers>: Ch<canal>=<valeur>, Ch<canal>=<valeur>, ...
  Exemple :
    [DMX] 1 paquets générés
      192.168.1.45 U0: Ch1=255, Ch2=0, Ch3=0

- [ArtNet] Envoyé vers <N> contrôleurs
  Exemple :
    [ArtNet] Envoyé vers 1 contrôleurs

- === STATISTIQUES ===
    eHuB: <nb_msg> msg, <nb_entités> entités
    DMX: <nb_paquets> paquets, <nb_canaux> canaux
    ArtNet: <nb_envois> envois vers <nb_ctrl> contrôleurs
  Exemple :
    === STATISTIQUES ===
    eHuB: 2 msg, 4 entités
    DMX: 2 paquets, 6 canaux
    ArtNet: 2 envois vers 1 contrôleurs
    ==================

Comment lire ces logs :
----------------------
- Chaque bloc [eHuB], [DMX], [ArtNet] correspond à une étape du pipeline.
- Les entités sont identifiées par leur ID et leur couleur RGB reçue.
- Les paquets DMX affichent l'IP du contrôleur, l'univers DMX, et les premiers canaux modifiés.
- Les stats globales permettent de voir l'activité cumulée depuis le démarrage.
- Si un type de monitoring est désactivé, rien n'est affiché pour cette étape.

Ce format est conçu pour être lisible d'un coup d'œil, même pour un débutant, et pour permettre de repérer rapidement les problèmes (ex : entités non mappées, paquets non envoyés, etc).
"""

import time
from collections import deque

class MonitoringDisplay:
    """
    Affichage temps réel et statistiques du pipeline LED (eHuB, DMX, ArtNet).
    Permet de logger les données à chaque étape, d'afficher les stats, et d'activer/désactiver chaque moniteur.
    """
    def __init__(self):
        self.ehub_enabled = True
        self.dmx_enabled = True
        self.artnet_enabled = True
        self.ehub_stats = {'messages': 0, 'entities': 0, 'last_update': 0}
        self.dmx_stats = {'packets': 0, 'channels': 0, 'last_update': 0}
        self.artnet_stats = {'sent': 0, 'controllers': set(), 'last_send': 0}
        self.recent_entities = deque(maxlen=10)
        self.recent_dmx = deque(maxlen=10)

    def log_ehub_data(self, entities):
        """
        Logge et affiche les entités reçues via eHuB (après parsing).
        Format affiché :
            [eHuB] <N> entités reçues
              Entité <id>: RGB(<r>,<g>,<b>)
        Exemple :
            [eHuB] 2 entités reçues
              Entité 1: RGB(255,0,0)
              Entité 2: RGB(0,255,0)
        Args:
            entities (list): Liste d'EntityUpdate
        """
        if not self.ehub_enabled:
            return
        self.ehub_stats['messages'] += 1
        self.ehub_stats['entities'] += len(entities)
        self.ehub_stats['last_update'] = time.time()
        self.recent_entities.extend(entities[:5])
        self._display_ehub_update(entities)

    def log_dmx_data(self, packets):
        """
        Logge et affiche les paquets DMX générés (mapping entités → DMX).
        Format affiché :
            [DMX] <N> paquets générés
              <IP> U<univers>: Ch<canal>=<valeur>, Ch<canal>=<valeur>, ...
        Exemple :
            [DMX] 1 paquets générés
              192.168.1.45 U0: Ch1=255, Ch2=0, Ch3=0
        Args:
            packets (list): Liste de DMXPacket
        """
        if not self.dmx_enabled:
            return
        self.dmx_stats['packets'] += len(packets)
        self.dmx_stats['channels'] += sum(len(p.channels) for p in packets)
        self.dmx_stats['last_update'] = time.time()
        self.recent_dmx.extend(packets)
        self._display_dmx_update(packets)

    def log_artnet_send(self, packets):
        """
        Logge et affiche les paquets DMX envoyés via ArtNet (UDP).
        Format affiché :
            [ArtNet] Envoyé vers <N> contrôleurs
        Exemple :
            [ArtNet] Envoyé vers 1 contrôleurs
        Args:
            packets (list): Liste de DMXPacket
        """
        if not self.artnet_enabled:
            return
        self.artnet_stats['sent'] += len(packets)
        self.artnet_stats['controllers'].update(p.controller_ip for p in packets)
        self.artnet_stats['last_send'] = time.time()
        self._display_artnet_send(packets)

    def _display_ehub_update(self, entities):
        print(f"[eHuB] {len(entities)} entités reçues")
        for entity in entities[:3]:
            print(f"  Entité {getattr(entity, 'id', '?')}: RGB({getattr(entity, 'r', '?')},{getattr(entity, 'g', '?')},{getattr(entity, 'b', '?')})")

    def _display_dmx_update(self, packets):
        print(f"[DMX] {len(packets)} paquets générés")
        for packet in packets[:2]:
            channels_str = ', '.join(f"Ch{ch}={val}" for ch, val in list(getattr(packet, 'channels', {}).items())[:3])
            print(f"  {getattr(packet, 'controller_ip', '?')} U{getattr(packet, 'universe', '?')}: {channels_str}")

    def _display_artnet_send(self, packets):
        print(f"[ArtNet] Envoyé vers {len(set(getattr(p, 'controller_ip', '?') for p in packets))} contrôleurs")

    def display_stats(self):
        """
        Affiche les statistiques globales du pipeline (messages, entités, paquets, etc.).
        Format affiché :
            === STATISTIQUES ===
            eHuB: <nb_msg> msg, <nb_entités> entités
            DMX: <nb_paquets> paquets, <nb_canaux> canaux
            ArtNet: <nb_envois> envois vers <nb_ctrl> contrôleurs
            ==================
        Exemple :
            === STATISTIQUES ===
            eHuB: 2 msg, 4 entités
            DMX: 2 paquets, 6 canaux
            ArtNet: 2 envois vers 1 contrôleurs
            ==================
        """
        print("\n=== STATISTIQUES ===")
        print(f"eHuB: {self.ehub_stats['messages']} msg, {self.ehub_stats['entities']} entités")
        print(f"DMX: {self.dmx_stats['packets']} paquets, {self.dmx_stats['channels']} canaux")
        print(f"ArtNet: {self.artnet_stats['sent']} envois vers {len(self.artnet_stats['controllers'])} contrôleurs")
        print("==================\n") 