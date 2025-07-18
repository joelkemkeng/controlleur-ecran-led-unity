r"""
tests/test_main.py - Tests d'intégration pour l'application principale (main.py)

Ce module vérifie que l'application LEDRoutingApp s'initialise correctement, que les callbacks
handle_update et handle_config produisent la sortie attendue, et que l'intégration de la config réelle
fonctionne. Ces tests garantissent que le pipeline principal est prêt à recevoir et traiter les messages eHuB.

Exécution :
    $ .\venv\Scripts\activate
    $ pytest tests/test_main.py

Portabilité :
- Pour Linux/Mac/Raspbian, active le venv avec :
    $ source venv/bin/activate
- Les tests et le code sont conçus pour être 100% portables (aucune dépendance exotique, chemins relatifs, pas de code spécifique Windows).
- Tu peux lancer les tests et le projet sur n'importe quelle plateforme sans modification.
"""

import pytest
from main import IntegratedLEDRouter
from core.models import EntityUpdate, EntityRange

def test_router_initialization():
    """
    Vérifie que le routeur principal s'initialise correctement avec la config réelle.
    - Teste la présence du config_mgr, du receiver, du mapper, du patch_handler, de l'artnet_sender, du monitor.
    - Garantit que le pipeline peut démarrer sans erreur.
    """
    router = IntegratedLEDRouter()
    ok = router.initialize()
    assert ok, "Le pipeline n'a pas pu être initialisé."
    assert hasattr(router, 'config_mgr')
    assert hasattr(router, 'receiver')
    assert hasattr(router, 'mapper')
    assert hasattr(router, 'patch_handler')
    assert hasattr(router, 'artnet_sender')
    assert hasattr(router, 'monitor')

def test_handle_update_output(capsys):
    """
    Vérifie que le callback handle_update affiche correctement le nombre d'entités et les 3 premières.
    - Simule la réception d'un message UPDATE avec 4 entités.
    - Capture la sortie console et vérifie la présence des informations clés.
    """
    router = IntegratedLEDRouter()
    router.initialize()
    entities = [
        EntityUpdate(100, 255, 0, 0, 0),
        EntityUpdate(101, 0, 255, 0, 0),
        EntityUpdate(102, 0, 0, 255, 0),
        EntityUpdate(103, 128, 128, 128, 0)
    ]
    router.handle_update(entities)
    captured = capsys.readouterr()
    assert "[eHuB] 4 entités reçues" in captured.out
    assert "Entité 100: RGB(255,0,0)" in captured.out
    assert "Entité 102: RGB(0,0,255)" in captured.out

def test_handle_config_output(capsys):
    """
    Vérifie que le callback handle_config affiche correctement le nombre de plages et les 3 premières.
    - Simule la réception d'un message CONFIG avec 4 plages.
    - Capture la sortie console et vérifie la présence des informations clés.
    """
    router = IntegratedLEDRouter()
    router.initialize()
    ranges = [
        EntityRange(0, 100, 169, 269),
        EntityRange(0, 270, 89, 358),
        EntityRange(0, 400, 169, 569),
        EntityRange(0, 570, 169, 739)
    ]
    router.handle_config(ranges)
    captured = capsys.readouterr()
    assert "🔄 Configuration mise à jour: 4 plages" in captured.out
    assert "Plage: payload 0-169 = entités 100-269" in captured.out or "Plage: payload 0-169 = entités 100-269" in captured.out
    assert "Plage: payload 0-89 = entités 270-358" in captured.out or "Plage: payload 0-89 = entités 270-358" in captured.out 