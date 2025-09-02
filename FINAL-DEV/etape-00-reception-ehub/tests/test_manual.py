#!/usr/bin/env python3
"""
🧪 TEST MANUEL - Récepteur eHub en action
Démonstration du récepteur avec envoi de messages test
"""

import sys
import os
import threading
import time
import socket

# Ajouter les chemins
sys.path.append('/home/joel/projet_ecran/controlleur-ecran-led-unity/FINAL-DEV/etape-00-reception-ehub')

from ehub_receiver import EHubReceiver, EHubMessage

def test_manual_reception():
    """
    Test manuel de réception avec envoi de messages
    """
    print("🎯 === TEST MANUEL RÉCEPTION eHUB ===")
    print()
    
    # Création récepteur
    receiver = EHubReceiver(port=8765)
    
    # Démarrage écoute
    if not receiver.start_listening():
        print("❌ Impossible de démarrer le récepteur")
        return False
    
    print("📡 Récepteur en écoute...")
    print("💡 Envoi de 3 messages test dans 2 secondes...")
    print()
    
    # Thread pour envoyer des messages test
    def sender_worker():
        time.sleep(2)  # Attendre que le récepteur soit prêt
        
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Message 1: Petit message
        msg1 = b"Message test #1 - Court"
        sender.sendto(msg1, ("127.0.0.1", 8765))
        time.sleep(0.5)
        
        # Message 2: Message plus long
        msg2 = b"Message test #2 - Plus long avec plus de contenu pour tester la reception"
        sender.sendto(msg2, ("127.0.0.1", 8765))
        time.sleep(0.5)
        
        # Message 3: Message simulant eHub
        msg3 = b"\x1f\x8b\x08\x00\x00\x00\x00\x00EHUB_SIMULATION_DATA_12345"
        sender.sendto(msg3, ("127.0.0.1", 8765))
        
        sender.close()
        print("📤 3 messages test envoyés!")
    
    # Démarrer l'envoi en arrière-plan
    sender_thread = threading.Thread(target=sender_worker)
    sender_thread.start()
    
    # Réception des messages
    messages_received = 0
    start_time = time.time()
    
    print("🔄 Écoute en cours...")
    
    while messages_received < 3 and (time.time() - start_time) < 10:
        message = receiver.receive_message(timeout=1.0)
        
        if message:
            messages_received += 1
            print(f"✅ Message {messages_received} reçu!")
            
            # Affichage détaillé
            print(f"   📏 Taille: {message.size} bytes")
            print(f"   📍 Source: {message.sender_ip}:{message.sender_port}")
            data_str = message.data[:50].decode('utf-8', errors='ignore')
            print(f"   📄 Contenu: {data_str}{'...' if len(message.data) > 50 else ''}")
            print()
    
    # Arrêt du récepteur
    receiver.stop()
    sender_thread.join()
    
    print(f"📊 Total reçu: {messages_received}/3 messages")
    
    if messages_received == 3:
        print("🎉 Test manuel réussi!")
        return True
    else:
        print("⚠️ Tous les messages n'ont pas été reçus")
        return False

def test_callback_custom():
    """
    Test avec callback personnalisé
    """
    print("🔧 === TEST CALLBACK PERSONNALISÉ ===")
    print()
    
    # Callback qui compte les messages
    message_count = 0
    total_bytes = 0
    
    def my_callback(message: EHubMessage):
        nonlocal message_count, total_bytes
        message_count += 1
        total_bytes += message.size
        
        print(f"🔄 [Callback] Message #{message_count}")
        print(f"   📊 Taille: {message.size} bytes")
        print(f"   📊 Total: {total_bytes} bytes")
        
        # Simulation traitement
        if b"EHUB" in message.data:
            print("   🎯 Message eHub détecté!")
        
        print()
    
    # Test rapide avec callback
    receiver = EHubReceiver(port=8771)
    
    if receiver.start_listening():
        print("📡 Récepteur avec callback en écoute...")
        
        # Envoi message test
        def send_test():
            time.sleep(1)
            sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sender.sendto(b"TEST_CALLBACK_EHUB_MESSAGE", ("127.0.0.1", 8771))
            sender.close()
        
        threading.Thread(target=send_test).start()
        
        # Écoute courte avec callback
        start_time = time.time()
        while time.time() - start_time < 3:
            message = receiver.receive_message(timeout=0.5)
            if message:
                my_callback(message)
                break
        
        receiver.stop()
        
        if message_count > 0:
            print("✅ Callback personnalisé fonctionne!")
            return True
        else:
            print("⚠️ Aucun message traité par le callback")
            return False
    else:
        print("❌ Impossible de démarrer le récepteur")
        return False

if __name__ == "__main__":
    print("🧪 TESTS MANUELS RÉCEPTEUR eHUB")
    print("=" * 50)
    print()
    
    # Test 1: Réception manuelle
    success1 = test_manual_reception()
    print()
    
    # Test 2: Callback personnalisé
    success2 = test_callback_custom()
    print()
    
    # Résumé
    if success1 and success2:
        print("🎉 === TOUS LES TESTS MANUELS RÉUSSIS ! ===")
        print("✅ Réception UDP opérationnelle")
        print("✅ Callbacks fonctionnels")
        print("✅ Prêt pour Unity!")
    else:
        print("⚠️ === QUELQUES PROBLÈMES DÉTECTÉS ===")
        print("🔧 Vérifiez la configuration réseau")
    
    print()
    print("📋 Pour Unity, utilisez:")
    print("🎯 IP: 172.26.223.135")
    print("🎯 Port: 8765")
    print("🎯 Protocole: UDP")
