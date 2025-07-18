"""
tools/debug_tools.py - Outils de test et de débogage eHuB/LED

Ce script permet de générer et d'envoyer des messages eHuB UPDATE simulés pour tester le pipeline LED sans Unity.
- Test séquentiel : allume une série d'entités une à une
- Test balayage couleurs : envoie différentes couleurs sur plusieurs entités
- Test entité unique : envoie une couleur précise sur une entité

Utilisation :
-------------
$ python tools/debug_tools.py

Compatible Windows, Linux, Mac, Raspbian. Nécessite Python 3.7+ (aucune dépendance exotique).

"""
import struct
import gzip
import time
import socket
import sys
import os

# Paramètres par défaut
default_port = 8765

def create_test_ehub_message(entity_id: int, r: int, g: int, b: int, w: int = 0) -> bytes:
    """
    Crée un message eHuB UPDATE compressé pour une entité donnée.
    Args:
        entity_id (int): ID de l'entité
        r, g, b, w (int): Valeurs RGBW (0-255)
    Returns:
        bytes: message eHuB complet prêt à l'envoi
    """
    payload = struct.pack('<H', entity_id) + bytes([r, g, b, w])
    compressed = gzip.compress(payload)
    header = b'eHuB\x02\x00\x01\x00' + struct.pack('<H', len(compressed))
    return header + compressed

def send_test_message(message: bytes, port: int = default_port):
    """
    Envoie un message eHuB via UDP sur localhost.
    Args:
        message (bytes): message eHuB à envoyer
        port (int): port UDP cible
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message, ('127.0.0.1', port))
    sock.close()

def create_sequential_test(start_id=100, count=10, color=(255,0,0), delay=0.1):
    """
    Allume une série d'entités une à une (effet chenillard).
    Args:
        start_id (int): premier ID d'entité
        count (int): nombre d'entités
        color (tuple): couleur RGB
        delay (float): délai entre envois (s)
    """
    for i in range(count):
        eid = start_id + i
        message = create_test_ehub_message(eid, *color)
        send_test_message(message)
        print(f"[DEBUG] Envoyé: Entité {eid} RGB{color}")
        time.sleep(delay)

def create_color_sweep_test(start_id=100, count=7, delay=0.5):
    """
    Envoie différentes couleurs sur plusieurs entités.
    Args:
        start_id (int): premier ID d'entité
        count (int): nombre d'entités
        delay (float): délai entre envois (s)
    """
    colors = [
        (255, 0, 0),    # Rouge
        (0, 255, 0),    # Vert
        (0, 0, 255),    # Bleu
        (255, 255, 0),  # Jaune
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Cyan
        (255, 255, 255) # Blanc
    ]
    for i in range(count):
        eid = start_id + i
        color = colors[i % len(colors)]
        message = create_test_ehub_message(eid, *color)
        send_test_message(message)
        print(f"[DEBUG] Envoyé: Entité {eid} RGB{color}")
        time.sleep(delay)

def send_single_entity():
    """
    Demande à l'utilisateur une entité et une couleur, puis envoie le message.
    """
    try:
        eid = int(input("ID entité: "))
        r = int(input("Rouge (0-255): "))
        g = int(input("Vert (0-255): "))
        b = int(input("Bleu (0-255): "))
    except Exception:
        print("Entrée invalide.")
        return
    message = create_test_ehub_message(eid, r, g, b)
    send_test_message(message)
    print(f"[DEBUG] Envoyé: Entité {eid} RGB({r},{g},{b})")

def checklist_prerequis():
    """
    Vérifie que tous les prérequis sont en place pour un fonctionnement optimal du pipeline LED.
    Affiche des messages clairs en cas de problème.
    """
    print("\n=== Checklist de prérequis ===")
    ok = True

    # 1. Vérifier la version de Python
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ requis. Version détectée :", sys.version)
        print("➡️  Installe Python 3.7 ou supérieur.")
        ok = False
    else:
        print("✅ Version de Python OK :", sys.version.split()[0])

    # 2. Fichiers essentiels
    config_paths = ["config.json", "config/config.json"]
    found_config = False
    for fname in config_paths:
        if os.path.isfile(fname):
            print(f"✅ {fname} présent.")
            found_config = True
            break
    if not found_config:
        print("❌ Fichier manquant : config.json")
        print("➡️  Crée ou copie config.json à la racine ou dans le dossier config/.")
        ok = False

    if not os.path.isfile("main.py"):
        print(f"❌ Fichier manquant : main.py")
        print(f"➡️  Crée ou copie main.py à la racine du projet.")
        ok = False
    else:
        print(f"✅ main.py présent.")

    # 3. Fichier de patchs (optionnel)
    if not os.path.isfile("patches.csv"):
        print("⚠️  Fichier patches.csv absent (ok si pas de patch à appliquer)")
    else:
        print("✅ patches.csv présent.")

    # 4. Dossier patch_record
    if not os.path.isdir("patch_record"):
        try:
            os.makedirs("patch_record", exist_ok=True)
            print("✅ Dossier patch_record créé.")
        except Exception as e:
            print("❌ Impossible de créer le dossier patch_record :", e)
            print("➡️  Vérifie les droits d'écriture dans le dossier du projet.")
            ok = False
    else:
        print("✅ Dossier patch_record présent.")

    # 5. Port UDP disponible
    try:
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_sock.bind(("127.0.0.1", default_port))
        test_sock.close()
        print(f"✅ Port UDP {default_port} disponible.")
    except Exception as e:
        print(f"❌ Port UDP {default_port} déjà utilisé ou indisponible : {e}")
        print(f"➡️  Ferme les autres applications utilisant ce port ou choisis-en un autre dans la config.")
        ok = False

    # 6. Modules Python essentiels
    try:
        import struct, gzip
        print("✅ Modules Python essentiels présents.")
    except ImportError as e:
        print(f"❌ Module manquant : {e}")
        print("➡️  Installe les modules requis avec pip.")
        ok = False

    print("\n---")
    if ok:
        print("✅ Tous les prérequis sont en place. Tu peux lancer le pipeline ou les tests en toute confiance !")
    else:
        print("❌ Certains prérequis sont manquants ou incorrects. Corrige-les avant de continuer.")
    print("---\n")

def create_config_message(ranges):
    """
    Crée un message eHuB CONFIG compressé.
    Args:
        ranges (list of tuples): [(payload_start, entity_start, payload_end, entity_end), ...]
    Returns:
        bytes: message eHuB CONFIG prêt à l'envoi
    """
    payload = b''.join([struct.pack('<HHHH', *r) for r in ranges])
    compressed = gzip.compress(payload)
    header = b'eHuB\x01\x00' + struct.pack('<H', len(ranges)) + struct.pack('<H', len(compressed))
    return header + compressed

def send_real_config_message(port=default_port):
    """
    Envoie un message CONFIG conforme au tableau de mapping réel fourni.
    """
    # Plages extraites du tableau (extrait, à compléter selon le tableau)
    ranges = [
        (0, 100, 169, 269), (0, 270, 89, 359), (0, 400, 169, 569), (0, 700, 169, 869),
        (0, 1000, 169, 1169), (0, 1300, 169, 1469), (0, 1600, 169, 1769), (0, 1900, 169, 2069),
        (0, 2200, 169, 2369), (0, 2500, 169, 2669), (0, 2800, 169, 2969), (0, 3100, 169, 3269),
        (0, 3400, 169, 3569), (0, 3700, 169, 3869), (0, 4000, 169, 4169), (0, 4300, 169, 4469),
        (0, 4600, 169, 4769), (0, 4770, 88, 4858), # Fin du premier contrôleur
        (0, 5100, 169, 5269), (0, 5270, 89, 5359), (0, 5400, 169, 5569), (0, 5700, 169, 5869),
        (0, 6000, 169, 6169), (0, 6300, 169, 6469), (0, 6600, 169, 6769), (0, 6900, 169, 7069),
        (0, 7200, 169, 7369), (0, 7500, 169, 7669), (0, 7800, 169, 7969), (0, 8100, 169, 8269),
        (0, 8400, 169, 8569), (0, 8700, 169, 8869), (0, 9000, 169, 9169), (0, 9300, 169, 9469),
        (0, 9600, 169, 9769), (0, 9770, 88, 9858), # Fin du deuxième contrôleur
        (0, 10100, 169, 10269), (0, 10270, 89, 10359), (0, 10400, 169, 10569), (0, 10700, 169, 10869),
        (0, 11000, 169, 11169), (0, 11300, 169, 11469), (0, 11600, 169, 11769), (0, 11900, 169, 12069),
        (0, 12200, 169, 12369), (0, 12500, 169, 12669), (0, 12800, 169, 12969), (0, 13100, 169, 13269),
        (0, 13400, 169, 13569), (0, 13700, 169, 13869), (0, 14000, 169, 14169), (0, 14300, 169, 14469),
        (0, 14600, 169, 14769), (0, 14770, 88, 14858), # Fin du troisième contrôleur
        (0, 15100, 169, 15269), (0, 15270, 89, 15359), (0, 15400, 169, 15569), (0, 15700, 169, 15869),
        (0, 16000, 169, 16169), (0, 16300, 169, 16469), (0, 16600, 169, 16769), (0, 16900, 169, 17069),
        (0, 17200, 169, 17369), (0, 17500, 169, 17669), (0, 17800, 169, 17969), (0, 18100, 169, 18269),
        (0, 18400, 169, 18569), (0, 18700, 169, 18869), (0, 19000, 169, 19169), (0, 19300, 169, 19469),
        (0, 19600, 169, 19769), (0, 19770, 88, 19858), # Fin du quatrième contrôleur
    ]
    message = create_config_message(ranges)
    send_test_message(message, port)
    print(f"[DEBUG] Message CONFIG réel envoyé avec {len(ranges)} plages.")

if __name__ == "__main__":
    print("🧪 Outils de test eHuB/LED")
    print("1. Test séquentiel (chenillard)")
    print("2. Test balayage couleurs")
    print("3. Test entité unique")
    print("4. Checklist de prérequis")
    print("5. Envoyer message CONFIG réel (full mapping)")
    print("q. Quitter")
    choice = input("Choix (1-5/q): ").strip()
    if choice == "1":
        create_sequential_test()
    elif choice == "2":
        create_color_sweep_test()
    elif choice == "3":
        send_single_entity()
    elif choice == "4":
        checklist_prerequis()
    elif choice == "5":
        send_real_config_message()
    else:
        print("Sortie.") 