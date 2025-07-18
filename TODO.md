- fair le Readme Generale , 

qui explique comment executer tout le projet apres un clone du git , 
qui explique comment executer la doc du code pdoc et le lire , 
qui explique comment faire les configuration possible avant tout lancement , 
qui explique comment tester le bon fonctionnemenr de la config sur l'ecran physique, 
qui explique comment voir le monitoring, et se rassurer que les choses se passe bien 
qui explique comment parser manuellement un message type CONFIG , 

qui explique comment se rassure que les differens server , port , ip  sont fonctionnel , donc comment faire ces verification en bonne et dure forme ,

qui explique commenet un se rassure que on utilise la bonne config , les bon port ..etc 

qui explique comment faire que , les systeme utilise pour la config de l'ecrant des controlleur , comment faire que il utilise la config dans le fichier config.json comment le verifier ,





- on doit faire une APIREST

qui doit 
 - recuperer la liste des patching enregistrer
 - executer la lecture d'un patching ,precis
 - qui doit activer ou deactiver  le reocord patch 

 ----- plustard ---> executer un patching 


 qui doit 
  - permettre l'exportation de la config en exel "advanced_config" , et recuperer cela en reponse 


qui doit 
  - permettre la reception de l'objet de la config de l'ecran initial sous forme d'objet en requete, et ensuite tout renitialiser ( jouer les asset de test de chaque controlleur en jouant des sequence d'animation de tout les led de chaque controlleur , pour s'assure qu'il ya une bonne configuration )

  - permettre la reception d'un message "TYPE CONFIG" sous forme de string en format "ehub" en requette pour les test , qui vas recupere le message decoder comme si il avais recue cela en udp ehub , puis appliquer la config ehub, 

     --- par la suite permette l'envoie d'une liste de message TYPE UPDATE , en requette dans l'objet recue , il aura une liste de string , sous format ehub, , que une fois recue , cette liste , receptionner cette liste, decoder chacun comme si on les avais recue en udp, et faire jouer cela en mode tel ,pour voir , si evidemment l'ecran se comporte comme les message ehub de tes recue en requette ont ete specifier , 
     et il nous permettra de s'assurer que le message CONFIG test qui avais ete envoyer avant a etet prise en compte 


  - permettre qu'on puisse encoyer telecharger l'etat actuelle du maping de tout les led physiquer avec leur id , (permettant de telecharger un patch des disposition)
      - et faire que on puisse envoye en requette un map data , pour patcher et changer le disposition et corespondance dans la configuration physique  , apres reception le syste doit se conformer a gerer le patch recue , donc en plus d'envoyer les info dans les led physique avec leur numero , il faut aussi faire il envoie aussi au patch de correspondance 

      le but est de faire appliquer le systeme de patch 







 