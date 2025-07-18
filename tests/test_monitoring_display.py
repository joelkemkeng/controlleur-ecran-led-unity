import pytest
from monitoring.display import MonitoringDisplay

# Classes factices pour le test
class EntityUpdate:
    def __init__(self, id, r, g, b, w=0):
        self.id = id
        self.r = r
        self.g = g
        self.b = b
        self.w = w

class DMXPacket:
    def __init__(self, controller_ip, universe, channels):
        self.controller_ip = controller_ip
        self.universe = universe
        self.channels = channels

def test_monitoring_display_basic(monkeypatch):
    """
    Teste le monitoring temps réel : log eHuB, DMX, ArtNet, stats, activation/désactivation.
    Vérifie que les compteurs augmentent et que l'affichage ne plante pas.
    """
    monitor = MonitoringDisplay()
    entities = [EntityUpdate(1, 255, 0, 0), EntityUpdate(2, 0, 255, 0)]
    dmx_packets = [DMXPacket('192.168.1.45', 0, {1: 255, 2: 0, 3: 0})]

    # Capture l'affichage console
    outputs = []
    monkeypatch.setattr('builtins.print', lambda *args, **kwargs: outputs.append(' '.join(map(str, args))))

    monitor.log_ehub_data(entities)
    monitor.log_dmx_data(dmx_packets)
    monitor.log_artnet_send(dmx_packets)
    monitor.display_stats()

    # Vérifie que les compteurs ont bien augmenté
    assert monitor.ehub_stats['messages'] == 1
    assert monitor.ehub_stats['entities'] == 2
    assert monitor.dmx_stats['packets'] == 1
    assert monitor.artnet_stats['sent'] == 1
    # Désactive le monitoring eHuB et vérifie que le compteur ne bouge plus
    monitor.ehub_enabled = False
    monitor.log_ehub_data(entities)
    assert monitor.ehub_stats['messages'] == 1  # Pas d'incrément
    # Réactive et vérifie
    monitor.ehub_enabled = True
    monitor.log_ehub_data(entities)
    assert monitor.ehub_stats['messages'] == 2
    # Vérifie que l'affichage ne plante pas
    assert any('[eHuB]' in line for line in outputs)
    assert any('[DMX]' in line for line in outputs)
    assert any('[ArtNet]' in line for line in outputs)
    assert any('STATISTIQUES' in line for line in outputs) 