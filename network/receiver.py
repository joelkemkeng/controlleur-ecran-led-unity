import socket
import threading
from typing import Callable
from ehub.parser import parse_update_message, parse_config_message

class EHubReceiver:
    """
    Récepteur UDP pour les messages eHuB (UPDATE et CONFIG).
    Écoute sur un port donné, filtre par univers, et dispatch les données parsées via des callbacks.

    Args:
        port (int): Port UDP d'écoute (défaut 8765)
        universe (int): Univers eHuB cible (défaut 0)

    Méthodes principales :
        - start_listening(update_callback, config_callback)
        - stop_listening()

    Exemple d'utilisation :
        def update_cb(entities):
            print(f"Reçu {len(entities)} entités")
        def config_cb(ranges):
            print(f"Reçu {len(ranges)} plages")
        receiver = EHubReceiver(port=8765, universe=0)
        receiver.start_listening(update_cb, config_cb)

    Exemples de sortie console réelle :
        # Message UPDATE (entités)
        Reçu 2 entités
        Entité 1 : RGBW(255,0,0,0)
        Entité 2 : RGBW(0,255,0,0)

        # Message CONFIG (plages)
        Reçu 1 plages
        Plage : payload 0-169 = entités 1-170

        # Exemple de callback pour affichage détaillé :
        def update_cb(entities):
            print(f"Reçu {len(entities)} entités")
            for e in entities:
                print(f"Entité {e.id} : RGBW({e.r},{e.g},{e.b},{e.w})")
        def config_cb(ranges):
            print(f"Reçu {len(ranges)} plages")
            for r in ranges:
                print(f"Plage : payload {r.payload_start}-{r.payload_end} = entités {r.entity_start}-{r.entity_end}")
    """
    def __init__(self, port: int = 8765, universe: int = 0):
        self.port = port
        self.universe = universe
        self.socket = None
        self.is_listening = False
        self._thread = None

    def start_listening(self, update_callback: Callable, config_callback: Callable):
        """
        Démarre l'écoute UDP en arrière-plan et dispatch les messages reçus.
        Args:
            update_callback (Callable): Fonction appelée avec la liste d'entités (UPDATE)
            config_callback (Callable): Fonction appelée avec la liste de plages (CONFIG)
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', self.port))
        self.is_listening = True
        self._thread = threading.Thread(target=self._listen_loop, args=(update_callback, config_callback))
        self._thread.daemon = True
        self._thread.start()

    def stop_listening(self):
        """Arrête l'écoute UDP proprement."""
        self.is_listening = False
        if self.socket:
            self.socket.close()
            self.socket = None
        if self._thread:
            self._thread.join(timeout=1)

    def _listen_loop(self, update_callback, config_callback):
        while self.is_listening:
            try:
                data, addr = self.socket.recvfrom(65536)
                # On tente d'abord le parsing du header pour filtrer l'univers
                from ehub.parser import parse_header
                #print(f"\n\n\n\n\n\n DEBUG [data_config_reseau_ehub_primaire] #receiver.py : Données configuration primaire reseau reception ehub :: \n - data_port: {self.port} \n - data_universe: {self.universe}")
                #print(f"\n\n\n\n\n\n DEBUG [data_ehub_recu] : Données brutes recu : {data}")
                header = parse_header(data)
                if header is None:
                    print(f"\n\n\n\n\n\n DEBUG [EHubReceiver] #receiver.py : Erreur de parsing du header")
                    continue
                if header['universe'] != self.universe:
                    continue
                if header['type'] == 2:
                    entities = parse_update_message(data)
                    update_callback(entities)
                elif header['type'] == 1:
                    ranges = parse_config_message(data)
                    config_callback(ranges)
            except Exception as e:
                print(f"[EHubReceiver] #receiver.py : Erreur réception/parsing: {e}")