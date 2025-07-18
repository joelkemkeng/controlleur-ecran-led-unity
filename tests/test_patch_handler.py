import os
import tempfile
from patching.handler import PatchHandler

# Classe factice pour DMXPacket
class DMXPacket:
    def __init__(self, controller_ip, universe, channels):
        self.controller_ip = controller_ip
        self.universe = universe
        self.channels = channels

def test_patch_add_and_apply():
    """
    Teste l'ajout d'un patch et son application sur un DMXPacket.
    """
    handler = PatchHandler()
    handler.add_patch(1, 389)
    handler.enabled = True
    packet = DMXPacket('ip', 0, {1: 255, 2: 128, 3: 64})
    patched = handler.apply_patches([packet])[0]
    assert patched.channels[389] == 255
    assert patched.channels[1] == 255
    assert patched.channels[2] == 128
    assert patched.channels[3] == 64

def test_patch_remove():
    """
    Teste la suppression d'un patch.
    """
    handler = PatchHandler()
    handler.add_patch(1, 389)
    handler.remove_patch(1)
    assert 1 not in handler.patches

def test_patch_save_and_load_csv():
    """
    Teste la sauvegarde et le chargement de patchs depuis un CSV temporaire.
    """
    handler = PatchHandler()
    handler.add_patch(1, 389)
    handler.add_patch(2, 390)
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, 'patch.csv')
        handler.save_patches_to_csv(path)
        # Recharge dans un nouveau handler
        handler2 = PatchHandler()
        handler2.load_patches_from_csv(path)
        assert handler2.patches[1] == 389
        assert handler2.patches[2] == 390

def test_patch_record_and_replay():
    """
    Teste l'enregistrement d'un patch dans patch_record/ et le replay du dernier patch.
    """
    handler = PatchHandler()
    handler.add_patch(1, 389)
    handler.add_patch(2, 390)
    with tempfile.TemporaryDirectory() as tmpdir:
        record_dir = os.path.join(tmpdir, 'patch_record')
        path = handler.record_patch(record_dir)
        assert os.path.exists(path)
        # Modifie le handler, puis recharge le patch enregistré
        handler.patches.clear()
        handler.replay_patch(path)
        assert handler.patches[1] == 389
        assert handler.patches[2] == 390

def test_patch_disabled():
    """
    Teste que si le patching est désactivé, les paquets sont inchangés.
    """
    handler = PatchHandler()
    handler.add_patch(1, 389)
    handler.enabled = False
    packet = DMXPacket('ip', 0, {1: 255})
    patched = handler.apply_patches([packet])[0]
    assert 389 not in patched.channels
    assert patched.channels[1] == 255 