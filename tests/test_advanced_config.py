import os
import tempfile
from config.advanced_config import AdvancedConfigManager

def test_create_and_validate_config():
    """
    Teste la génération d'une config avancée et sa validation (pas de chevauchement d'entités).
    """
    mgr = AdvancedConfigManager()
    config = mgr.create_mur_led_config()
    assert mgr.validate_config(config) is True
    # Modifie pour créer un chevauchement
    config.controllers['controller2'].start_entity = 4000
    assert mgr.validate_config(config) is False

def test_export_excel_template():
    """
    Teste l'export d'un template Excel de mapping (fichier temporaire).
    """
    mgr = AdvancedConfigManager()
    config = mgr.create_mur_led_config()
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, 'template.xlsx')
        mgr.export_excel_template(path, config)
        assert os.path.exists(path) 