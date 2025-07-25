"""
main.py - Application principale du pipeline de routage LED

Ce module constitue le point d'entrée du pipeline LED professionnel.
Il assemble tous les modules : configuration avancée, parsing eHuB, mapping dynamique, patch system,
envoi ArtNet, monitoring temps réel, et interface utilisateur.

Pipeline global (schéma logique) :
----------------------------------
1. Réception des messages eHuB (UDP)
2. Parsing dynamique (UPDATE/CONFIG)
3. Mapping entités → DMX (aucun hardcoding, basé sur la config réelle)
4. Application des patchs DMX dynamiques
5. Envoi ArtNet (limitation FPS, multi-contrôleurs)
6. Monitoring temps réel (logs, stats, debug)
7. Interface utilisateur simple (stats, patches, arrêt)

Portabilité :
-------------
- Fonctionne sur Windows, Linux, Mac, Raspbian
- Aucun module exotique requis (sauf pandas/openpyxl pour l'export Excel)

Exemple de session complète :
----------------------------
>>> python main.py
🚀 Initialisation du routeur LED...
✅ 2 patches chargés
✅ Initialisation terminée
🎯 Routeur démarré - En attente de messages eHuB...
📊 Affichage des stats toutes les 10 secondes
🔧 Fichiers: config.json, patches.csv
==================================================
COMMANDES DISPONIBLES:
  's' + Enter : Afficher les statistiques
  'p' + Enter : Afficher les patches actifs
  'q' + Enter : Quitter
==================================================
[CONFIG] Reçu 3 plages de configuration
  Plage: payload 0-169 = entités 100-269
  Plage: payload 0-89 = entités 270-358
  Plage: payload 0-169 = entités 400-569
[UPDATE] Reçu 1223 entités
  Entité 100: RGB(255,0,0)
  Entité 101: RGB(0,255,0)
  Entité 102: RGB(0,0,255)
[DMX] 8 paquets générés
  192.168.1.45 U0: Ch1=255, Ch2=0, Ch3=0
[ArtNet] Envoyé vers 1 contrôleurs
=== STATISTIQUES ===
eHuB: 2 msg, 1223 entités
DMX: 8 paquets, 24 canaux
ArtNet: 8 envois vers 1 contrôleurs
==================

Notes pédagogiques :
--------------------
- Chaque étape du pipeline est loguée et expliquée pour faciliter le débogage et l'apprentissage.
- Les erreurs sont affichées avec le contexte pour aider à comprendre et corriger rapidement.
- L'interface utilisateur permet de suivre l'état du système en temps réel et d'agir facilement.

Voir la documentation générée (pdoc) pour des exemples détaillés sur chaque module.
"""

import threading
import time
import argparse
from config.advanced_config import AdvancedConfigManager
from network.receiver import EHubReceiver
from mapping.entity_mapper import EntityMapper
from patching.handler import PatchHandler
from artnet.sender import ArtNetSender
from monitoring.display import MonitoringDisplay
from core.models import EntityUpdate, EntityRange

class IntegratedLEDRouter:
    """
    Application principale intégrée du pipeline LED.

    Cette classe assemble tous les modules : configuration avancée, parsing eHuB, mapping dynamique, patch system,
    envoi ArtNet, monitoring temps réel, et interface utilisateur.

    Attributs principaux :
    ---------------------
    - config_mgr (AdvancedConfigManager) : gestionnaire de configuration avancée
    - receiver (EHubReceiver) : récepteur UDP eHuB
    - mapper (EntityMapper) : mapping dynamique entités → DMX
    - patch_handler (PatchHandler) : gestionnaire de patchs DMX
    - artnet_sender (ArtNetSender) : envoi des paquets DMX via ArtNet
    - monitor (MonitoringDisplay) : affichage temps réel et statistiques

    Exemple d'utilisation :
    ----------------------
    >>> router = IntegratedLEDRouter()
    >>> router.start()

    Exemple de sortie console :
    --------------------------
    🚀 Initialisation du routeur LED...
    ✅ 2 patches chargés
    ✅ Initialisation terminée
    🎯 Routeur démarré - En attente de messages eHuB...
    📊 Affichage des stats toutes les 10 secondes
    🔧 Fichiers: config.json, patches.csv
    ==================================================
    COMMANDES DISPONIBLES:
      's' + Enter : Afficher les statistiques
      'p' + Enter : Afficher les patches actifs
      'q' + Enter : Quitter
    ==================================================

    Conseils pédagogiques :
    ----------------------
    - Pour tester le pipeline, utiliser les outils de test fournis (tools/debug_tools.py)
    - Pour voir la configuration active, utiliser tools/show_config.py
    - Pour vérifier la connectivité réseau, utiliser tools/check_network.py
    - Pour exporter un template Excel du mapping, voir AdvancedConfigManager.export_excel_template
    """
    def __init__(self):
        """
        Initialise tous les modules du pipeline LED :
        - Chargement et validation de la configuration avancée
        - Initialisation du receiver eHuB, du mapper, du patch handler, de l'ArtNet sender, du monitoring
        - Chargement des patchs si disponibles

        Exemple :
        >>> router = IntegratedLEDRouter()
        >>> router.initialize()
        🚀 Initialisation du routeur LED...
        ✅ 2 patches chargés
        ✅ Initialisation terminée
        """
        self.config_mgr = AdvancedConfigManager()
        self.receiver = None
        self.mapper = None
        self.patch_handler = PatchHandler()
        self.artnet_sender = None
        self.monitor = MonitoringDisplay()
        self.is_running = False
        self.stats_thread = None

    def initialize(self):
        """
        Initialise tous les composants du pipeline, valide la configuration, et prépare le mapping dynamique.
        Retourne True si tout est prêt, False sinon.

        Exemple de sortie console :
        --------------------------
        🚀 Initialisation du routeur LED...
        ✅ 2 patches chargés
        ✅ Initialisation terminée
        """
        print("🚀 Initialisation du routeur LED...")
        if not self.config_mgr.validate_config():
            print("❌ Configuration invalide! Vérifiez les plages d'entités et les univers.")
            return False
        try:
            self.receiver = EHubReceiver(
                port=self.config_mgr.config.listen_port,
                universe=self.config_mgr.config.ehub_universe
            )
            self.mapper = EntityMapper(self.config_mgr.config)
            self.artnet_sender = ArtNetSender(
                max_fps=self.config_mgr.config.max_fps
            )
            try:
                self.patch_handler.load_patches_from_csv("patches.csv")
                self.patch_handler.enabled = True
                print(f"✅ {len(self.patch_handler.patches)} patches chargés")
            except Exception as e:
                print(f"⚠️  Aucun fichier de patches trouvé ou erreur: {e}")
            print("✅ Initialisation terminée")
            return True
        except Exception as e:
            print(f"❌ Erreur à l'initialisation: {e}")
            return False

    def start(self):
        """
        Démarre le pipeline LED : écoute eHuB, mapping dynamique, patch, ArtNet, monitoring, interface utilisateur.

        Interaction utilisateur :
        ------------------------
        - 's' + Entrée : affiche les statistiques globales
        - 'p' + Entrée : affiche les patches actifs et leur état
        - 'q' + Entrée : arrête proprement le routeur

        Exemple de session :
        -------------------
        🎯 Routeur démarré - En attente de messages eHuB...
        [UPDATE] Reçu 1223 entités
        [DMX] 8 paquets générés
        [ArtNet] Envoyé vers 1 contrôleurs
        === STATISTIQUES ===
        eHuB: 2 msg, 1223 entités
        DMX: 8 paquets, 24 canaux
        ArtNet: 8 envois vers 1 contrôleurs
        ==================
        """
        if not self.initialize():
            return
        self.is_running = True
        self.receiver.start_listening(
            self.handle_update,
            self.handle_config
        )
        self.stats_thread = threading.Thread(target=self._stats_loop)
        self.stats_thread.daemon = True
        self.stats_thread.start()
        print("🎯 Routeur démarré - En attente de messages eHuB...")
        print("📊 Affichage des stats toutes les 10 secondes")
        print("🔧 Fichiers: config.json, patches.csv")
        print("\n" + "="*50)
        print("COMMANDES DISPONIBLES:")
        print("  's' + Enter : Afficher les statistiques")
        print("  'p' + Enter : Afficher les patches actifs")
        print("  'q' + Enter : Quitter")
        print("="*50)
        try:
            while self.is_running:
                cmd = input().strip().lower()
                if cmd == 'q':
                    break
                elif cmd == 's':
                    self.monitor.display_stats()
                elif cmd == 'p':
                    print(f"Patches actifs: {self.patch_handler.patches}")
                    print(f"Patches activés: {self.patch_handler.enabled}")
        except KeyboardInterrupt:
            print("\n🛑 Arrêt demandé par l'utilisateur")
        except Exception as e:
            print(f"❌ Erreur fatale: {e}")
        finally:
            self.stop()

    def handle_update(self, entities):
        """
        Callback appelé à la réception d'un message UPDATE eHuB.
        Pipeline complet : log, mapping dynamique, patch, envoi ArtNet, monitoring, gestion d'erreur.
        """
        try:
            self.monitor.log_ehub_data(entities)
            #print(f"[DEBUG]  #main.py (handle_update) Entités reçues: {[e.id for e in entities[:10]]} ...")
            dmx_packets = self.mapper.map_entities_to_dmx(entities)
            #print(f"[DEBUG] #main.py (handle_update) Paquets DMX générés: {len(dmx_packets)}")
            #for pkt in dmx_packets[:5]:
                #print(f"  DMXPacket: IP={pkt.controller_ip}, U={pkt.universe}, Channels={list(pkt.channels.items())[:6]} ...")
            self.monitor.log_dmx_data(dmx_packets)
            patched_packets = self.patch_handler.apply_patches(dmx_packets)
            self.artnet_sender.send_dmx_packets(patched_packets)
            self.monitor.log_artnet_send(patched_packets)
        except Exception as e:
            print(f"❌ Erreur traitement UPDATE: {e}")

    def handle_config(self, ranges):
        """
        Callback appelé à la réception d'un message CONFIG eHuB.
        Met à jour le mapping dynamique (aucun hardcoding), log, gestion d'erreur.
        """
        try:
            self.monitor.log_ehub_data([])  # Pas d'entités dans CONFIG
            entity_ranges_dict = {r.entity_start: r for r in ranges}
            self.mapper.build_mapping(entity_ranges_dict)
            for r in ranges:
                print(f"Plage: payload {r.payload_start}-{r.payload_end} = entités {r.entity_start}-{r.entity_end}")
            print(f"🔄 Configuration mise à jour: {len(ranges)} plages")
            # Affiche le mapping construit (premiers éléments)
            print("--- Mapping entité → DMX (extrait) ---")
            for i, (eid, mapping) in enumerate(self.mapper.entity_to_dmx.items()):
                print(f"  Entité {eid}: {mapping}")
                if i >= 10:
                    print("  ... (voir le reste dans self.mapper.entity_to_dmx)")
                    break
            print(f"Total entités mappées: {len(self.mapper.entity_to_dmx)}")
        except Exception as e:
            print(f"❌ Erreur traitement CONFIG: {e}")

    def _stats_loop(self):
        """
        Affiche les statistiques globales toutes les 10 secondes (messages, entités, paquets, etc.).

        Exemple de sortie console :
        --------------------------
        === STATISTIQUES ===
        eHuB: 2 msg, 1223 entités
        DMX: 8 paquets, 24 canaux
        ArtNet: 8 envois vers 1 contrôleurs
        ==================
        """
        while self.is_running:
            time.sleep(10)
            self.monitor.display_stats()

    def stop(self):
        """
        Arrête le pipeline proprement (fermeture sockets, arrêt threads, log).
        Affiche un message de confirmation.
        """
        self.is_running = False
        if self.artnet_sender:
            self.artnet_sender.cleanup_sockets()
        print("🛑 Routeur arrêté")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Routeur LED - pipeline principal intégré, patchs, monitoring, mapping dynamique.")
    args = parser.parse_args()
    router = IntegratedLEDRouter()
    router.start() 