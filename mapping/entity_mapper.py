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
        CORRECTION : Calcul correct des univers et canaux DMX selon la vraie structure.
        Args:
            entity_ranges (Dict[int, EntityRange]): Dictionnaire {entity_start: EntityRange}
        """
        if not entity_ranges:
            print("[EntityMapper] Aucune plage d'entités fournie")
            return
            
        self.entity_to_dmx.clear()
        total_mapped = 0
        
        for plage in entity_ranges.values():
            # Validation de la plage
            if plage.entity_start > plage.entity_end:
                print(f"[EntityMapper] Plage invalide: {plage.entity_start} > {plage.entity_end}")
                continue
                
            # Trouver le contrôleur qui englobe cette plage
            controller_found = False
            for ctrl_name, ctrl in self.config.controllers.items():
                if ctrl.start_entity <= plage.entity_start and plage.entity_end <= ctrl.end_entity:
                    if not ctrl.universes:
                        print(f"[EntityMapper] Contrôleur {ctrl_name} sans univers configurés")
                        continue
                        
                    nb_leds = plage.entity_end - plage.entity_start + 1
                    # Calcul correct de l'offset dans le contrôleur
                    entity_offset = plage.entity_start - ctrl.start_entity
                    
                    for i in range(nb_leds):
                        entity_id = plage.entity_start + i
                        current_offset = entity_offset + i
                        
                        # Calcul correct de l'univers (170 LEDs par univers selon spec)
                        universe_index = current_offset // 170
                        led_position_in_universe = current_offset % 170
                        
                        # Validation que l'univers existe
                        if universe_index < len(ctrl.universes):
                            universe = ctrl.universes[universe_index]
                            # Calcul des canaux DMX (1-indexé, 3 canaux RGB)
                            channel_start = (led_position_in_universe * 3) + 1
                            
                            # Validation des limites DMX (512 canaux max)
                            if channel_start + 2 <= 512:
                                self.entity_to_dmx[entity_id] = {
                                    'controller_ip': ctrl.ip,
                                    'universe': universe,
                                    'r_channel': channel_start,
                                    'g_channel': channel_start + 1,
                                    'b_channel': channel_start + 2,
                                }
                                total_mapped += 1
                            else:
                                print(f"[EntityMapper] Canaux DMX > 512 pour entité {entity_id}: {channel_start}")
                        else:
                            print(f"[EntityMapper] Univers {universe_index} non disponible pour contrôleur {ctrl_name}")
                    
                    controller_found = True
                    break
                    
            if not controller_found:
                print(f"[EntityMapper] Aucun contrôleur trouvé pour plage {plage.entity_start}-{plage.entity_end}")
        
        print(f"[EntityMapper] Mapping terminé: {total_mapped} entités mappées")

    def map_entities_to_dmx(self, entities: List[EntityUpdate]) -> List[DMXPacket]:
        """
        Transforme une liste d'entités en paquets DMX groupés par contrôleur et univers.
        CORRECTION : Validation complète des données avant mapping.
        Args:
            entities (List[EntityUpdate]): Liste d'entités à mapper
        Returns:
            List[DMXPacket]: Liste de paquets DMX prêts à l'envoi
        """
        if not entities:
            return []
            
        dmx_packets = {}  # (ip, universe) -> DMXPacket
        mapped_count = 0
        error_count = 0
        
        for entity in entities:
            # Validation des valeurs RGB
            if not (0 <= entity.r <= 255 and 0 <= entity.g <= 255 and 0 <= entity.b <= 255):
                print(f"[EntityMapper] Valeurs RGB invalides pour entité {entity.id}: RGB({entity.r},{entity.g},{entity.b})")
                error_count += 1
                continue
                
            if entity.id not in self.entity_to_dmx:
                error_count += 1
                continue  # Ignore les entités non mappées
                
            mapping = self.entity_to_dmx[entity.id]
            
            # Validation supplémentaire des canaux DMX
            if any(ch > 512 or ch < 1 for ch in [mapping['r_channel'], mapping['g_channel'], mapping['b_channel']]):
                print(f"[EntityMapper] Canaux DMX invalides pour entité {entity.id}: R={mapping['r_channel']}, G={mapping['g_channel']}, B={mapping['b_channel']}")
                error_count += 1
                continue
                
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
            mapped_count += 1
            
        if error_count > 0:
            print(f"[EntityMapper] {error_count} entités ignorées (erreurs de validation)")
            
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