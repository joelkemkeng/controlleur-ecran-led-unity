"""
tools/parse_config_message.py - Parsing manuel d'un message CONFIG eHuB

Ce script permet de parser manuellement un message CONFIG eHuB (binaire),
soit depuis un fichier, soit depuis une chaîne hexadécimale, et d'afficher
le résultat de façon lisible (plages d'entités, payload, etc).

Portabilité :
- Fonctionne sur Linux, Mac, Windows, Raspbian
- Aucune dépendance exotique

Exemple d'utilisation :
----------------------
$ python tools/parse_config_message.py --file message_config.bin
$ python tools/parse_config_message.py --hex "65487542010001000600..."

Sortie attendue :
----------------
[CONFIG] 1 plages de configuration
  Plage: payload 0-169 = entités 100-269

Explication pédagogique :
------------------------
- Permet de vérifier le parsing d'un message CONFIG reçu ou généré
- Utile pour le debug, la simulation, ou la documentation
"""

import argparse
from ehub.parser import EHubParser

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parsing manuel d'un message CONFIG eHuB")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', type=str, help="Fichier binaire contenant le message CONFIG")
    group.add_argument('--hex', type=str, help="Chaîne hexadécimale du message CONFIG (sans espaces)")
    args = parser.parse_args()

    if args.file:
        with open(args.file, 'rb') as f:
            data = f.read()
    else:
        data = bytes.fromhex(args.hex)

    parser = EHubParser()
    try:
        ranges = parser.parse_config_message(data)
        print(f"[CONFIG] {len(ranges)} plages de configuration")
        for r in ranges:
            print(f"  Plage: payload {r.payload_start}-{r.payload_end} = entités {r.entity_start}-{r.entity_end}")
    except Exception as e:
        print(f"Erreur de parsing : {e}") 