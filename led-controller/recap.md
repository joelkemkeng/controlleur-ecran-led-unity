# Récapitulatif du projet

Ce document résume l'architecture et les composants clés du projet de contrôleur LED.

## Structure du projet

- `core/` : Contient la logique métier de l'application.
  - `animation.py` : Moteur de gestion des animations.
  - `router.py` : Moteur de routage Art-Net vers DMX.
  - `ehub_receiver.py` : Récepteur pour les données eHub.
- `ui/` : Contient l'interface utilisateur.
  - `app.py`: Point d'entrée principal de l'interface graphique (GUI).
  - `(anciens fichiers)` : Les anciens fichiers de l'interface basée sur les onglets, conservés pour référence mais plus utilisés.
- `utils/` : Utilitaires (logs, configuration).
- `main.py` : Ancien point d'entrée, maintenant obsolète.

## Nouvelle Interface (ui/app.py)

La nouvelle interface est construite avec `CustomTkinter` et suit une architecture moderne :

- **Fenêtre principale (`App`)** : Gère la fenêtre et la disposition générale.
- **Navigation latérale** : Permet de basculer entre les vues (Live, Animation, Monitoring, etc.).
- **Vues conteneurs** : Chaque vue est un `CTkFrame` qui contient les widgets spécifiques à cette section.
- **Intégration directe** : Les composants comme la visualisation sont maintenant intégrés directement dans les vues appropriées. 