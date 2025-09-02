# Diagramme UML Corrigé - Module de Routage LED

## Diagramme de Classes

```plantuml
@startuml
!theme plain
title Architecture Logicielle du Module de Routage V2

package "Module de Routage LED" {
  
  class EHubReceiver {
    -port : int
    -univers : int
    -isListening : boolean
    +startListening() : void
    +stopListening() : void
    +parseUpdateMessage(data : byte[]) : EntityUpdate[]
    +parseConfigMessage(data : byte[]) : EntityConfig[]
    +decompressPayload(data : byte[]) : byte[]
  }
  
  class EntityToDMXMapper {
    -mappingTable : Map<EntityID, DMXAddress>
    -channelMode : ChannelMode
    -offset : int
    +configureMapping(mappingTable : Map, channelMode : string, offset : int) : void
    +mapEntitiesToDMX(entities : EntityUpdate[]) : DMXData[]
    +saveConfiguration(filePath : string) : void
    +loadConfiguration(filePath : string) : void
    +validateMapping() : boolean
  }
  
  class PatchMapHandler {
    -patches : Map<int, int>
    -isEnabled : boolean
    +addPatch(sourceChannel : int, targetChannel : int) : void
    +removePatch(sourceChannel : int) : void
    +applyPatches(dmxData : DMXData[]) : DMXData[]
    +loadPatchFromFile(filePath : string) : void
    +savePatchToFile(filePath : string) : void
    +enablePatching() : void
    +disablePatching() : void
  }
  
  class ArtNetSender {
    -targetControllers : List<ControllerConfig>
    -maxFrameRate : int
    -lastSendTime : long
    +addController(ip : string, universes : int[]) : void
    +removeController(ip : string) : void
    +sendDMXPacket(dmxData : DMXData[], targetIP : string, universe : int) : void
    +limitFrameRate() : void
    +isNetworkReady() : boolean
  }
  
  class MonitoringVisualization {
    -eHubMonitorEnabled : boolean
    -dmxMonitorEnabled : boolean
    -artNetMonitorEnabled : boolean
    +enableEHubMonitor() : void
    +disableEHubMonitor() : void
    +displayLiveEHubData(data : EntityUpdate[]) : void
    +displayLiveDMXData(data : DMXData[]) : void
    +displayArtNetTraffic(packets : ArtNetPacket[]) : void
    +generateReport() : string
  }
  
  class TestGenerator {
    -testPatterns : Map<string, TestPattern>
    +generateSequentialTest(entityRange : int[]) : EntityUpdate[]
    +generateColorTest(color : RGB, entityRange : int[]) : EntityUpdate[]
    +generateRandomTest(entityCount : int) : EntityUpdate[]
    +simulateEHubMessages(pattern : TestPattern) : void
  }
  
  class ConfigurationManager {
    -currentConfig : SystemConfig
    +saveSystemConfig(config : SystemConfig) : void
    +loadSystemConfig() : SystemConfig
    +validateConfig(config : SystemConfig) : boolean
    +exportConfig(format : string) : void
  }
  
  ' Relations
  EHubReceiver --> EntityToDMXMapper : "fournit données\nupdate/config"
  EntityToDMXMapper --> PatchMapHandler : "applique patches\nsi nécessaire"
  EntityToDMXMapper --> ArtNetSender : "transmet\nDMX mappé"
  PatchMapHandler --> EntityToDMXMapper : "retourne données\npatchées"
  
  EHubReceiver --> MonitoringVisualization : "données eHuB\nreçues"
  EntityToDMXMapper --> MonitoringVisualization : "DMX généré"
  ArtNetSender --> MonitoringVisualization : "trafic ArtNet"
  
  TestGenerator --> EHubReceiver : "génère messages\nde test"
  ConfigurationManager --> EntityToDMXMapper : "configuration\nmapping"
  ConfigurationManager --> PatchMapHandler : "configuration\npatches"
}

' Types de données
class EntityUpdate {
  +id : int
  +r : byte
  +g : byte
  +b : byte
  +w : byte
}

class DMXData {
  +universe : int
  +channel : int
  +value : byte
  +controllerIP : string
}

class ControllerConfig {
  +ip : string
  +universes : int[]
  +startEntity : int
  +endEntity : int
}

@enduml
```

## Diagramme de Séquence

```plantuml
@startuml
!theme plain
title Flux Temps Réel - Traitement des Messages eHuB

actor "Artiste (Unity/Tan)" as Artist
participant "EHubReceiver" as Receiver
participant "EntityToDMXMapper" as Mapper
participant "PatchMapHandler" as PatchHandler
participant "ArtNetSender" as Sender
participant "MonitoringVisualization" as Monitor

== Initialisation ==
Artist -> Receiver : Démarre l'écoute eHuB
Receiver -> Monitor : Active monitoring eHuB
Mapper -> PatchHandler : Charge les patches

== Message CONFIG (1x/seconde) ==
Artist -> Receiver : Message CONFIG eHuB
activate Receiver
Receiver -> Receiver : Décompresse payload GZip
Receiver -> Receiver : Parse les plages d'entités
Receiver -> Mapper : Met à jour la configuration
activate Mapper
Mapper -> Mapper : Valide le mapping
Mapper -> Monitor : Affiche config reçue
deactivate Mapper
Receiver -> Monitor : Affiche données eHuB
deactivate Receiver

== Message UPDATE (40x/seconde) ==
Artist -> Receiver : Message UPDATE eHuB
activate Receiver
Receiver -> Receiver : Décompresse payload GZip
Receiver -> Receiver : Parse les entités (ID, RGBW)
Receiver -> Mapper : Transmet EntityUpdate[]
activate Mapper
Receiver -> Monitor : Affiche données eHuB reçues

Mapper -> Mapper : Mappe entités → DMX
Mapper -> PatchHandler : Applique patches si activés
activate PatchHandler
PatchHandler -> PatchHandler : Redirige canaux défaillants
PatchHandler -> Mapper : Retourne données patchées
deactivate PatchHandler

Mapper -> Sender : Envoie DMXData[]
activate Sender
Mapper -> Monitor : Affiche DMX généré
deactivate Mapper

Sender -> Sender : Limite le taux de trame
Sender -> Sender : Groupe par contrôleur/univers
loop Pour chaque contrôleur
  Sender -> Sender : Crée packet ArtNet
  Sender -> "Contrôleur BC216" : Envoie via UDP
end
Sender -> Monitor : Affiche trafic ArtNet
deactivate Sender
deactivate Receiver

== Test et Débogage ==
Monitor -> "TestGenerator" : Génère pattern de test
"TestGenerator" -> Receiver : Simule messages eHuB
note right : Permet de tester\nsans Unity

@enduml
```

## Améliorations apportées

### 1. **Syntaxe PlantUML corrigée**
- Séparation claire des diagrammes avec `@startuml` et `@enduml`
- Noms de classes conformes (PascalCase)
- Types de données explicites

### 2. **Architecture enrichie**
- **ConfigurationManager** : Gestion centralisée des configurations
- **Types de données** : EntityUpdate, DMXData, ControllerConfig
- **Méthodes détaillées** : Parsing, compression, validation

### 3. **Diagramme de séquence amélioré**
- **Phases distinctes** : Initialisation, CONFIG, UPDATE, Test
- **Activation/désactivation** des participants
- **Gestion des erreurs** et validation
- **Boucles** pour les contrôleurs multiples

### 4. **Détails techniques ajoutés**
- Décompression GZip explicite
- Limitation du taux de trame
- Groupement par contrôleur/univers
- Validation des configurations

Cette architecture respecte mieux les exigences du cahier des charges et offre une structure plus robuste pour le développement.



Voici le diagramme UML corrigé avec une meilleure structure et syntaxe :J'ai corrigé votre diagramme UML avec les améliorations suivantes :

## 🔧 **Corrections techniques principales**

### 1. **Syntaxe PlantUML corrigée**
- Séparation correcte des diagrammes avec `@startuml` et `@enduml`
- Noms de classes en PascalCase (convention)
- Types de données explicites et cohérents

### 2. **Architecture enrichie**
- **ConfigurationManager** ajouté pour centraliser la gestion des configs
- **Types de données** définis : `EntityUpdate`, `DMXData`, `ControllerConfig`
- **Méthodes détaillées** avec parsing, compression GZip, validation

### 3. **Diagramme de séquence amélioré**
- **Phases distinctes** : Initialisation → CONFIG → UPDATE → Test
- **Activation/désactivation** des participants pour clarifier les interactions
- **Gestion des boucles** pour les contrôleurs multiples
- **Notes explicatives** pour le contexte

## 🚀 **Nouvelles fonctionnalités ajoutées**

### Gestion explicite du protocole eHuB
- Décompression GZip des payloads
- Parsing des structures binaires (sextuors, plages)
- Validation des configurations reçues

### Optimisations réseau
- Limitation du taux de trame (40 FPS max)
- Groupement des données par contrôleur/univers
- Monitoring du trafic ArtNet

### Robustesse
- Validation des mappings avant application
- Gestion des patches activables/désactivables
- Module de test intégré pour déboguer sans Unity

Cette architecture est maintenant prête pour l'implémentation et respecte parfaitement les exigences du projet LAPS !