Après analyse approfondie de ces documents techniques, je peux vous dire que ce projet traite du **développement d'un système de contrôle d'installations lumineuses LED artistiques**.

## Vue d'ensemble du projet

Il s'agit d'un **projet de fin d'année** où les étudiants doivent créer un système complet pour contrôler des installations LED artistiques du **Groupe LAPS**, une entreprise spécialisée dans les installations lumineuses créatives (comme des araignées géantes, arbres lumineux, etc.).

## Architecture technique en 3 couches

### 1. **Couche Artistique** (Unity/Tan)
- Outil de création d'animations 3D
- Système d'**entités** (chaque LED = une entité avec ID unique)
- Protocole personnalisé **eHuB** pour transmettre l'état des LEDs
- Timeline et illuminateurs pour créer des effets visuels

### 2. **Couche de Routage** (Le cœur du projet)
Les étudiants doivent développer un logiciel qui :
- Reçoit les messages eHuB (protocole UDP avec compression GZip)
- Traduit les entités virtuelles en adresses physiques réelles
- Route vers les contrôleurs BC216 via le protocole **ArtNet/DMX512**
- Gère les pannes et reconfigurations dynamiques

### 3. **Couche Matérielle**
- Contrôleurs **BC216** (16 sorties, 1024 canaux chacune)
- Bandes LED RGB programmables
- Protocole DMX512 (512 canaux par univers)
- Réseau Ethernet pour la communication

## Cas d'usage concret : Le mur LED test

Un écran LED de **2m x 2m** avec :
- 128 x 128 LEDs visibles (16 384 LEDs)
- 64 bandes de 259 LEDs chacune
- 4 contrôleurs BC216 (IP: 192.168.1.45-48)
- Mapping complexe entités → univers → canaux

## Objectifs pédagogiques

1. **P1** (obligatoire) : Développer le module de routage
2. **P2** (obligatoire) : Créer des animations artistiques
3. **P3-P5** (bonus) : Développer des outils alternatifs, optimiser les protocoles, créer des expériences interactives

## Défis techniques majeurs

- **Performance** : Routage temps réel de milliers de LEDs
- **Scalabilité** : Supporter de très grandes installations
- **Fiabilité** : Gérer les pannes matérielles en production
- **Ergonomie** : Interface utilisateur pour configurer facilement des installations complexes

Ce projet combine donc **art numérique**, **ingénierie réseau temps réel**, **protocoles de communication** et **développement d'interfaces utilisateur** dans un contexte professionnel réel.