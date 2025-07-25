#!/usr/bin/env python3
"""
Script pour envoyer les données eHub via UDP en permanence
Serveur UDP: 127.0.0.1:8765
"""

import socket
import time
import threading
import ast

class EHubUDPSender:
    def __init__(self, host='127.0.0.1', port=8765):
        self.host = host
        self.port = port
        self.running = False
        self.clients = set()
        self.ehub_data = []
        self.sock = None
        
    def load_ehub_data(self, filename='data_send.txt'):
        """Charge les données eHub depuis le fichier"""
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
                
            for line in lines:
                line = line.strip()
                if line.startswith('CONFIG:') or line.startswith('UPDATE:'):
                    # Extrait les données après les ':'
                    data_str = line.split(':', 1)[1]
                    # Convertit la chaîne b'...' en bytes
                    try:
                        data_bytes = ast.literal_eval(data_str)
                        self.ehub_data.append(data_bytes)
                        print(f"Données chargées: {len(data_bytes)} bytes")
                    except Exception as e:
                        print(f"Erreur lors du parsing des données: {e}")
                        
            print(f"Total des données chargées: {len(self.ehub_data)} paquets")
            
        except FileNotFoundError:
            print(f"Fichier {filename} non trouvé")
        except Exception as e:
            print(f"Erreur lors du chargement des données: {e}")
    
    def start_server(self):
        """Démarre le serveur UDP"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.sock.settimeout(1.0)  # Timeout pour permettre l'arrêt propre
            
            print(f"Serveur UDP démarré sur {self.host}:{self.port}")
            self.running = True
            
            # Démarre le thread d'envoi des données
            sender_thread = threading.Thread(target=self.send_data_loop)
            sender_thread.daemon = True
            sender_thread.start()
            
            # Boucle d'écoute pour les nouveaux clients
            while self.running:
                try:
                    data, addr = self.sock.recvfrom(1024)
                    if addr not in self.clients:
                        self.clients.add(addr)
                        print(f"Nouveau client connecté: {addr}")
                        
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        print(f"Erreur serveur: {e}")
                    
        except Exception as e:
            print(f"Erreur démarrage serveur: {e}")
        finally:
            if self.sock:
                self.sock.close()
    
    def send_data_loop(self):
        """Boucle d'envoi des données eHub en permanence"""
        if not self.ehub_data:
            print("Aucune donnée eHub à envoyer")
            return
            
        current_index = 0
        
        while self.running:
            if self.clients:
                # Envoie les données au client actuel
                data_to_send = self.ehub_data[current_index]
                
                # Copie des clients pour éviter les modifications pendant l'itération
                clients_copy = self.clients.copy()
                
                for client_addr in clients_copy:
                    try:
                        self.sock.sendto(data_to_send, client_addr)
                        print(f"Envoyé {len(data_to_send)} bytes à {client_addr}")
                    except Exception as e:
                        print(f"Erreur envoi vers {client_addr}: {e}")
                        self.clients.discard(client_addr)
                
                # Passe au paquet suivant (cycle through all data)
                current_index = (current_index + 1) % len(self.ehub_data)
                
            # Attendre avant le prochain envoi (1 seconde entre les paquets)
            time.sleep(1.0)
    
    def stop_server(self):
        """Arrête le serveur"""
        print("Arrêt du serveur...")
        self.running = False
        if self.sock:
            self.sock.close()

def main():
    # Crée le sender eHub
    sender = EHubUDPSender()
    
    # Charge les données depuis le fichier
    sender.load_ehub_data()
    
    if not sender.ehub_data:
        print("Aucune donnée eHub trouvée, arrêt du programme")
        return
    
    try:
        # Démarre le serveur
        sender.start_server()
    except KeyboardInterrupt:
        print("\nInterruption par l'utilisateur")
    finally:
        sender.stop_server()

if __name__ == "__main__":
    main()