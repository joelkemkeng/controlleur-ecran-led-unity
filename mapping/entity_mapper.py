"""
mapping/entity_mapper.py - Mapper principal entités → DMX

Ce module contient la classe EntityMapper qui construit le mapping entre les entités logiques (EntityUpdate)
et leur représentation physique DMX (univers, canal, contrôleur), à partir de la configuration réelle.

Exemple d'utilisation :
    >>> from mapping.entity_mapper import EntityMapper
    >>> from config.manager import ConfigManager
    >>> from core.models import EntityUpdate
    >>> from dmx.models import DMXPacket
    >>> config = ConfigManager("config/config.json").config
    >>> mapper = EntityMapper(config)
    >>> mapper.build_mapping(entity_ranges)
    >>> entities = [EntityUpdate(100, 255, 0, 0, 0)]
    >>> dmx_packets = mapper.map_entities_to_dmx(entities)
    >>> print(dmx_packets)

Portabilité :
- 100% compatible Linux, Raspbian, Mac, Windows
- Aucune dépendance exotique
"""

from dmx.models import DMXPacket
from core.models import EntityUpdate, EntityRange
from config.manager import SystemConfig
from typing import List, Dict

class EntityMapper:
    """
    Mapper principal entités → DMX.
    Construit le mapping à partir de la configuration système et des plages reçues (CONFIG),
    puis permet de transformer une liste d'entités en paquets DMX prêts à l'envoi.

    Args:
        config (SystemConfig): Configuration système complète

    Exemple d'utilisation :
        >>> mapper = EntityMapper(config)
        >>> mapper.build_mapping(entity_ranges)
        >>> dmx_packets = mapper.map_entities_to_dmx(entities)
    """
    def __init__(self, config: SystemConfig):
        self.config = config
        self.entity_to_dmx = {}  # entity_id -> dict(controller_ip, universe, r_channel, g_channel, b_channel)

    def build_mapping(self, entity_ranges: Dict[int, EntityRange]):
        """
        Construit le mapping entité → DMX à partir des plages reçues (CONFIG) et de la config système.
        Args:
            entity_ranges (Dict[int, EntityRange]): Dictionnaire {entity_start: EntityRange}
        """
        self.entity_to_dmx.clear()
        for plage in entity_ranges.values():
            # Trouver le contrôleur qui englobe cette plage
            for ctrl_name, ctrl in self.config.controllers.items():
                if ctrl.start_entity <= plage.entity_start and plage.entity_end <= ctrl.end_entity:
                    nb_leds = plage.entity_end - plage.entity_start + 1
                    # Trouver l'univers ArtNet correspondant à la plage (par index dans la liste des univers du contrôleur)
                    plage_index = None
                    try:
                        plage_index = ctrl.universes.index(plage.payload_start) if plage.payload_start in ctrl.universes else None
                    except Exception:
                        plage_index = None
                    for i in range(nb_leds):
                        entity_id = plage.entity_start + i
                        # Univers ArtNet pour cette plage
                        if plage_index is not None:
                            universe = ctrl.universes[plage_index]
                        else:
                            universe = ctrl.universes[0] if ctrl.universes else 0
                        channel = (i * 3) + 1
                        self.entity_to_dmx[entity_id] = {
                            'controller_ip': ctrl.ip,
                            'universe': universe,
                            'r_channel': channel,
                            'g_channel': channel + 1,
                            'b_channel': channel + 2,
                        }
                    break  # On a trouvé le bon contrôleur pour cette plage, inutile de continuer

    def map_entities_to_dmx(self, entities: List[EntityUpdate]) -> List[DMXPacket]:
        """
        Transforme une liste d'entités en paquets DMX groupés par contrôleur et univers.
        Args:
            entities (List[EntityUpdate]): Liste d'entités à mapper
        Returns:
            List[DMXPacket]: Liste de paquets DMX prêts à l'envoi
        """
        dmx_packets = {}  # (ip, universe) -> DMXPacket
        for entity in entities:
            if entity.id not in self.entity_to_dmx:
                continue  # Ignore les entités non mappées
            mapping = self.entity_to_dmx[entity.id]
            key = (mapping['controller_ip'], mapping['universe'])
            if key not in dmx_packets:
                dmx_packets[key] = DMXPacket(
                    controller_ip=mapping['controller_ip'],
                    universe=mapping['universe'],
                    channels={}
                )
            pkt = dmx_packets[key]
            pkt.channels[mapping['r_channel']] = entity.r
            pkt.channels[mapping['g_channel']] = entity.g
            pkt.channels[mapping['b_channel']] = entity.b
        return list(dmx_packets.values())

    def optimize_mapping(self):
        """
        Optimise le mapping en pré-calculant les correspondances entité → DMX.
        (Ici, le mapping est déjà en cache dans self.entity_to_dmx après build_mapping.)
        Peut être étendu pour des optimisations futures (ex : indexation avancée).
        """
        # Le mapping est déjà en cache dans self.entity_to_dmx
        pass

    def batch_process_entities(self, entities: List[EntityUpdate], batch_size: int = 100):
        """
        Traite les entités par lots pour optimiser la mémoire et la performance.
        Args:
            entities (List[EntityUpdate]): Liste d'entités à traiter
            batch_size (int): Taille du lot (par défaut 100)
        Yields:
            List[DMXPacket]: Paquets DMX pour chaque lot
        Exemple d'utilisation :
            for dmx_packets in mapper.batch_process_entities(entities, batch_size=500):
                # Envoi ou traitement du lot
        """
        for i in range(0, len(entities), batch_size):
            batch = entities[i:i + batch_size]
            yield self.map_entities_to_dmx(batch) 