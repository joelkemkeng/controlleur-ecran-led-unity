# Ticket 4.2.1 – Gestion réseau robuste ArtNet

## Objectif
Ajouter une méthode de validation réseau (`validate_controller_connection`) dans `ArtNetSender` pour tester la connectivité UDP vers un contrôleur ArtNet, et garantir la robustesse du routage sur des installations réelles.

## Importance pour le projet
- Permet de diagnostiquer rapidement les problèmes de réseau (câblage, IP, firewall) avant d'envoyer du DMX.
- Évite de perdre du temps à déboguer des erreurs qui ne viennent pas du code mais de l'infrastructure réseau.
- Indispensable pour les grandes installations (plusieurs contrôleurs, réseaux complexes).

## Explication détaillée
La méthode `validate_controller_connection(ip)` tente d'envoyer un petit paquet UDP ("test") à l'adresse IP du contrôleur ArtNet (port 6454). Si l'envoi ne lève pas d'exception, le contrôleur est considéré comme joignable (au niveau réseau). Sinon, la méthode retourne `False`.

- **Ce que ça vérifie :**
  - Que l'adresse IP est accessible sur le réseau local
  - Que le port UDP 6454 n'est pas bloqué
- **Ce que ça ne vérifie pas :**
  - Que le contrôleur "comprend" ArtNet (juste qu'il reçoit bien des paquets UDP)

**Exemple d'utilisation :**
```python
from artnet.sender import ArtNetSender
sender = ArtNetSender()
if sender.validate_controller_connection('192.168.1.45'):
    print("Contrôleur joignable !")
else:
    print("Contrôleur injoignable !")
```

## Comment tester concrètement
1. Lancer les tests unitaires :
   ```bash
   pytest tests/test_artnet_sender.py
   ```
2. Les tests `test_validate_controller_connection_success` et `test_validate_controller_connection_failure` simulent respectivement un contrôleur joignable et injoignable (mock réseau, pas besoin de matériel réel).
3. Pour tester en vrai :
   - Connecter un contrôleur ArtNet sur le réseau
   - Appeler la méthode avec son IP réelle

## Exemples concrets de cas réels
- **Cas 1 :** Le contrôleur est bien branché, la méthode retourne `True` → on peut envoyer du DMX.
- **Cas 2 :** Le câble réseau est débranché ou l'IP est fausse, la méthode retourne `False` → il faut vérifier le câblage ou la config IP.
- **Cas 3 :** Un firewall bloque le port 6454, la méthode retourne `False` → il faut ouvrir le port UDP sur le réseau.

## Portabilité et conseils pratiques
- Fonctionne sur Linux, Mac, Windows, Raspbian sans modification.
- Peut être utilisée dans un script de diagnostic avant chaque show ou installation.
- Pour les grandes installations, faire un check sur toutes les IP de contrôleurs avant de lancer le routage.

---

**Prochaine étape :** Passer à l'intégration du monitoring temps réel (Epic 5) ou à la gestion avancée des erreurs réseau si besoin. 