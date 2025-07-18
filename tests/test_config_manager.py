import os
import pytest
from config.manager import ConfigManager, SystemConfig, ControllerConfig

def test_load_real_config():
    # On suppose que config/config.json existe et correspond à la structure Excel
    mgr = ConfigManager("config/config.json")
    config = mgr.config
    assert isinstance(config, SystemConfig)
    assert config.listen_port == 8765
    assert config.ehub_universe == 0
    assert config.max_fps == 40
    # Vérifie les 4 contrôleurs
    assert len(config.controllers) == 4
    assert "controller1" in config.controllers
    assert config.controllers["controller1"].ip == "192.168.1.45"
    assert config.controllers["controller2"].universes[0] == 32
    assert config.controllers["controller4"].end_entity == 19858


def test_create_default_config(tmp_path):
    # Teste la création d'une config par défaut si le fichier n'existe pas
    config_path = tmp_path / "no_file.json"
    mgr = ConfigManager(str(config_path))
    config = mgr.config
    assert config.listen_port == 8765
    assert "controller1" in config.controllers
    assert config.controllers["controller1"].ip == "192.168.1.45"
    assert config.controllers["controller1"].universes[0] == 0 