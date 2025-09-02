#!/usr/bin/env python3
"""
🧪 TEST DONNÉES RÉELLES - Messages eHub de Unity
Test avec de vrais messages capturés depuis Unity
Mode continu pour observer les animations
"""

import sys
import os
import time
from collections import defaultdict

# Ajouter les chemins
sys.path.append('/home/joel/projet_ecran/controlleur-ecran-led-unity/FINAL-DEV/etape-02-decodage-ehub')

from ehub_complete_pipeline_decoder import EHubDecoder

def test_animation_monitor():
    """
    🎬 MONITEUR D'ANIMATION CONTINU
    Observe les changements de valeurs RGBW en temps réel
    """
    print("� === MONITEUR ANIMATION eHUB ===")
    print()
    
    # Initialisation décodeur
    print("🚀 Initialisation décodeur...")
    decoder = EHubDecoder(port=8765)
    
    if not decoder.initialize():
        print("❌ Échec initialisation")
        return False
    
    print("✅ Décodeur initialisé")
    print()
    print("🎯 MODE ANIMATION CONTINUE")
    print("💡 Lancez Unity et démarrez une animation")
    print("🔍 Les changements de valeurs RGBW s'afficheront ici")
    print("� Appuyez Ctrl+C pour arrêter")
    print("=" * 60)
    print()
    
    # Variables de monitoring
    entity_history = defaultdict(lambda: {"r": None, "g": None, "b": None, "w": None})
    packets_received = 0
    last_stats_time = time.time()
    start_time = time.time()
    
    # Entités à surveiller (les premières trouvées + quelques fixes)
    monitored_entities = set()
    
    try:
        while True:
            message = decoder.receiver.receive_message(timeout=0.5)
            
            if message:
                packets_received += 1
                
                # Décodage du paquet
                packet = decoder.decode_ehub_packet(message)
                
                if packet and packet.entities:
                    # Ajouter nouvelles entités à surveiller (max 10)
                    for entity in packet.entities:
                        if len(monitored_entities) < 10:
                            monitored_entities.add(entity.entity_id)
                    
                    # Analyser changements pour entités surveillées
                    changes_detected = False
                    
                    for entity in packet.entities:
                        if entity.entity_id in monitored_entities:
                            eid = entity.entity_id
                            prev = entity_history[eid]
                            
                            # Vérifier changements
                            changed = False
                            if prev["r"] != entity.red:
                                changed = True
                            elif prev["g"] != entity.green:
                                changed = True
                            elif prev["b"] != entity.blue:
                                changed = True
                            elif prev["w"] != entity.white:
                                changed = True
                            
                            if changed or prev["r"] is None:
                                changes_detected = True
                                
                                # Afficher le changement
                                if prev["r"] is not None:
                                    print(f"🔄 Entité {eid:5}: ", end="")
                                    
                                    # Rouge
                                    if prev["r"] != entity.red:
                                        print(f"R:{prev['r']:3}→{entity.red:3} ", end="")
                                    else:
                                        print(f"R:{entity.red:3}     ", end="")
                                    
                                    # Vert
                                    if prev["g"] != entity.green:
                                        print(f"G:{prev['g']:3}→{entity.green:3} ", end="")
                                    else:
                                        print(f"G:{entity.green:3}     ", end="")
                                    
                                    # Bleu
                                    if prev["b"] != entity.blue:
                                        print(f"B:{prev['b']:3}→{entity.blue:3} ", end="")
                                    else:
                                        print(f"B:{entity.blue:3}     ", end="")
                                    
                                    # Blanc
                                    if prev["w"] != entity.white:
                                        print(f"W:{prev['w']:3}→{entity.white:3}")
                                    else:
                                        print(f"W:{entity.white:3}")
                                
                                else:
                                    # Première valeur détectée
                                    print(f"🆕 Entité {eid:5}: R:{entity.red:3} G:{entity.green:3} B:{entity.blue:3} W:{entity.white:3}")
                                
                                # Mettre à jour l'historique
                                entity_history[eid]["r"] = entity.red
                                entity_history[eid]["g"] = entity.green
                                entity_history[eid]["b"] = entity.blue
                                entity_history[eid]["w"] = entity.white
                    
                    # Afficher stats périodiquement
                    current_time = time.time()
                    if current_time - last_stats_time >= 3.0:  # Toutes les 3 secondes
                        elapsed = current_time - start_time
                        pps = packets_received / elapsed if elapsed > 0 else 0
                        
                        if not changes_detected:
                            print(f"📊 {packets_received} paquets reçus | {pps:.1f} pps | {len(monitored_entities)} entités surveillées")
                        
                        last_stats_time = current_time
            else:
                # Timeout - afficher message d'attente
                current_time = time.time()
                if current_time - last_stats_time >= 5.0:
                    print("⏳ En attente de données Unity... (vérifiez la connexion)")
                    last_stats_time = current_time
    
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par utilisateur")
    
    finally:
        decoder.stop()
    
    # Résumé final
    elapsed = time.time() - start_time
    pps = packets_received / elapsed if elapsed > 0 else 0
    
    print("\n" + "=" * 60)
    print(f"📊 RÉSUMÉ FINAL:")
    print(f"⏱️  Durée: {elapsed:.1f} secondes")
    print(f"📦 Paquets reçus: {packets_received}")
    print(f"📊 Débit moyen: {pps:.1f} paquets/seconde")
    print(f"🎯 Entités surveillées: {len(monitored_entities)}")
    
    if monitored_entities:
        print(f"🔢 IDs surveillés: {sorted(list(monitored_entities))}")
    
    return packets_received > 0

def test_continuous_decoding():
    """
    🔄 Test de décodage simple en continu (pour debug)
    """
    print("🔄 === TEST DÉCODAGE SIMPLE ===")
    print()
    
    decoder = EHubDecoder(port=8765)
    
    if not decoder.initialize():
        print("❌ Échec initialisation")
        return False
    
    print("📊 Décodage simple pendant 10 secondes...")
    print()
    
    start_time = time.time()
    packets_count = 0
    
    try:
        while time.time() - start_time < 10:
            message = decoder.receiver.receive_message(timeout=0.5)
            
            if message:
                packet = decoder.decode_ehub_packet(message)
                if packet:
                    packets_count += 1
                    print(f"📦 Paquet #{packets_count}: {len(packet.entities)} entités")
    
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé")
    
    finally:
        decoder.stop()
    
    print(f"✅ {packets_count} paquets décodés")
    return packets_count > 0

if __name__ == "__main__":
    print("🧪 MONITEUR ANIMATION eHUB EN TEMPS RÉEL")
    print("=" * 60)
    print()
    
    print("🎬 Mode: Analyse continue des changements RGBW")
    print("🎯 Objectif: Observer les animations Unity en temps réel")
    print("🔍 Affichage: Seulement les entités qui changent")
    print()
    
    try:
        # Lancer le moniteur d'animation
        test_animation_monitor()
    
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé")
    
    print("\n✅ Monitoring terminé")
