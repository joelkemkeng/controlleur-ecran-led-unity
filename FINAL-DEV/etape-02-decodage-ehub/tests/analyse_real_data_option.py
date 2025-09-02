#!/usr/bin/env python3
"""
Script d'analyse interactif des données eHuB avec options multiples
"""

import sys
import os
import time
import signal
from typing import Optional, Dict, Any

# Ajouter les répertoires au path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(os.path.dirname(parent_dir))

sys.path.insert(0, parent_dir)
sys.path.insert(0, root_dir)

from ehub_complete_pipeline_decoder import EHubDecoder, EHubReceiver, EHubEntity

class AnalysisSession:
    """Gestionnaire de session d'analyse avec compteurs et temporisation"""
    
    def __init__(self, mode: str, limit: int, description: str):
        self.mode = mode
        self.limit = limit
        self.description = description
        self.start_time = time.time()
        self.packet_count = 0
        self.entity_changes = {}
        self.last_entities = {}
        self.running = True
        
    def should_continue(self) -> bool:
        """Vérifie si la session doit continuer selon le mode"""
        if not self.running:
            return False
            
        if self.mode == "time":
            elapsed = time.time() - self.start_time
            return elapsed < self.limit
        elif self.mode == "packets":
            return self.packet_count < self.limit
        elif self.mode == "continuous":
            return True
        
        return False
    
    def update_packet_count(self):
        """Met à jour le compteur de paquets"""
        self.packet_count += 1
        
    def get_elapsed_time(self) -> float:
        """Retourne le temps écoulé"""
        return time.time() - self.start_time
        
    def get_status(self) -> str:
        """Retourne le statut actuel de la session"""
        elapsed = self.get_elapsed_time()
        if self.mode == "time":
            remaining = max(0, self.limit - elapsed)
            return f"⏱️  {elapsed:.1f}s écoulé, {remaining:.1f}s restant"
        elif self.mode == "packets":
            remaining = max(0, self.limit - self.packet_count)
            return f"📦 {self.packet_count}/{self.limit} paquets ({remaining} restants)"
        elif self.mode == "continuous":
            return f"🔄 Continu - {elapsed:.1f}s écoulé, {self.packet_count} paquets"
        
        return f"Status: {elapsed:.1f}s, {self.packet_count} paquets"

class InteractiveAnalyzer:
    """Analyseur interactif des données eHuB"""
    
    def __init__(self):
        self.session: Optional[AnalysisSession] = None
        self.decoder = EHubDecoder(port=8765)
        
        # Handler pour arrêt propre
        signal.signal(signal.SIGINT, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handler pour Ctrl+C"""
        print("\n🛑 Arrêt demandé par l'utilisateur...")
        if self.session:
            self.session.running = False
            
    def show_menu(self):
        """Affiche le menu d'options"""
        print("\n" + "="*60)
        print("🔬 ANALYSEUR INTERACTIF DONNÉES eHuB")
        print("="*60)
        print("Choix d'analyse disponibles :")
        print()
        print("1️⃣  Analyse pendant 3 secondes")
        print("2️⃣  Analyse de 3 paquets seulement")
        print("3️⃣  Analyse de 30 paquets")
        print("4️⃣  Analyse pendant 30 secondes")
        print("5️⃣  Analyse continue (Ctrl+C pour arrêter)")
        print()
        print("🔧 Options avancées :")
        print("6️⃣  Analyse personnalisée (temps)")
        print("7️⃣  Analyse personnalisée (paquets)")
        print()
        print("0️⃣  Quitter")
        print("="*60)
        
    def get_user_choice(self) -> Optional[AnalysisSession]:
        """Récupère le choix de l'utilisateur et crée la session"""
        
        while True:
            try:
                choice = input("Votre choix (0-7) : ").strip()
                
                if choice == "0":
                    print("👋 Au revoir !")
                    return None
                    
                elif choice == "1":
                    return AnalysisSession("time", 3, "Analyse 3 secondes")
                    
                elif choice == "2":
                    return AnalysisSession("packets", 3, "Analyse 3 paquets")
                    
                elif choice == "3":
                    return AnalysisSession("packets", 30, "Analyse 30 paquets")
                    
                elif choice == "4":
                    return AnalysisSession("time", 30, "Analyse 30 secondes")
                    
                elif choice == "5":
                    return AnalysisSession("continuous", 0, "Analyse continue")
                    
                elif choice == "6":
                    seconds = int(input("Nombre de secondes : "))
                    if seconds > 0:
                        return AnalysisSession("time", seconds, f"Analyse {seconds} secondes")
                    else:
                        print("❌ Nombre de secondes invalide")
                        
                elif choice == "7":
                    packets = int(input("Nombre de paquets : "))
                    if packets > 0:
                        return AnalysisSession("packets", packets, f"Analyse {packets} paquets")
                    else:
                        print("❌ Nombre de paquets invalide")
                        
                else:
                    print("❌ Choix invalide, essayez à nouveau")
                    
            except ValueError:
                print("❌ Entrée invalide, essayez à nouveau")
            except KeyboardInterrupt:
                print("\n👋 Au revoir !")
                return None
                
    def analyze_entity_changes(self, entities: list):
        """Analyse les changements d'entités"""
        changes_detected = False
        
        for entity in entities:
            entity_id = entity.entity_id
            current_values = (entity.red, entity.green, entity.blue, entity.white)
            
            if entity_id in self.session.last_entities:
                last_values = self.session.last_entities[entity_id]
                if current_values != last_values:
                    changes_detected = True
                    old_r, old_g, old_b, old_w = last_values
                    print(f"🔄 Entité {entity_id}: "
                          f"R={old_r}→{entity.red} G={old_g}→{entity.green} "
                          f"B={old_b}→{entity.blue} W={old_w}→{entity.white}")
            else:
                # Nouvelle entité
                if any([entity.red, entity.green, entity.blue, entity.white]):  # Seulement si non-noir
                    changes_detected = True
                    print(f"✨ Nouvelle entité {entity_id}: "
                          f"R={entity.red} G={entity.green} B={entity.blue} W={entity.white}")
            
            self.session.last_entities[entity_id] = current_values
            
        return changes_detected
        
    def run_analysis(self, session: AnalysisSession):
        """Lance l'analyse selon la session configurée"""
        self.session = session
        
        print(f"\n🚀 Démarrage : {session.description}")
        print(f"📡 Écoute sur port 8765...")
        print("💡 Appuyez Ctrl+C pour arrêter manuellement")
        print("-" * 50)
        
        # Initialiser le décodeur
        if not self.decoder.initialize():
            print("❌ Échec initialisation du décodeur")
            return
            
        print("✅ Décodeur initialisé et prêt")
        
        last_status_time = time.time()
        status_interval = 1.0  # Afficher le statut toutes les secondes
        
        try:
            while session.should_continue():
                # Réception de données avec timeout - utilise directement decoder.receiver
                message = self.decoder.receiver.receive_message(timeout=0.5)
                if not message:
                    # Afficher message d'attente si pas de données depuis longtemps
                    current_time = time.time()
                    if current_time - last_status_time >= 5.0:
                        print("⏳ En attente de données Unity... (vérifiez la connexion)")
                        last_status_time = current_time
                    continue
                
                try:
                    # Debug: afficher réception de données
                    print(f"📨 Données reçues: {len(message.data)} bytes")
                    
                    # Décodage - utilise le message complet comme dans test_real_data.py
                    packet = self.decoder.decode_ehub_packet(message)
                    if packet and packet.entities:
                        session.update_packet_count()
                        print(f"✅ Paquet décodé: {len(packet.entities)} entités")
                        
                        # Analyse des changements
                        changes = self.analyze_entity_changes(packet.entities)
                        
                        # Affichage du statut périodique
                        current_time = time.time()
                        if current_time - last_status_time >= status_interval:
                            print(f"📊 {session.get_status()}")
                            last_status_time = current_time
                    else:
                        print("⚠️  Paquet reçu mais échec décodage")
                            
                except Exception as e:
                    print(f"❌ Erreur décodage: {e}")
                    
        except KeyboardInterrupt:
            print("\n🛑 Analyse arrêtée par l'utilisateur")
            
        finally:
            self.decoder.stop()
        
        # Résumé final
        print("\n" + "="*50)
        print("📋 RÉSUMÉ DE L'ANALYSE")
        print("="*50)
        print(f"⏱️  Durée totale: {session.get_elapsed_time():.1f} secondes")
        print(f"📦 Paquets traités: {session.packet_count}")
        print(f"🎭 Entités uniques vues: {len(session.last_entities)}")
        
        if session.packet_count > 0:
            rate = session.packet_count / session.get_elapsed_time()
            print(f"📈 Débit moyen: {rate:.1f} paquets/seconde")
            
        print("="*50)
        
    def run(self):
        """Point d'entrée principal"""
        print("🔬 Analyseur de données eHuB en temps réel")
        
        while True:
            self.show_menu()
            session = self.get_user_choice()
            
            if session is None:
                break
                
            self.run_analysis(session)
            
            # Demander si on veut recommencer
            print("\n" + "-"*30)
            again = input("🔄 Nouvelle analyse ? (o/N) : ").strip().lower()
            if again not in ['o', 'oui', 'y', 'yes']:
                print("👋 Au revoir !")
                break

def main():
    """Fonction principale"""
    analyzer = InteractiveAnalyzer()
    analyzer.run()

if __name__ == "__main__":
    main()
