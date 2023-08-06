.. -*- coding: utf-8 -*-

L'état d'avancement d'un projet peut être difficilement quantifiable. Le choix fait par les auteurs de CubicWeb-Forge est de priviligier des livraisons multiples et régulières.

Une livraison de version permet de valider l'itération du cycle de développement et de consolider suffisamment le code de base pour ajouter de nouvelles fonctionnalités.

Ces livrables doivent au minimum pouvoir s'installer, configurer les dépendances requises et se désinstaller sur le système hôte. Il est conseillé d'utiliser la distribution Debian afin de minimiser ces étapes.


Créer une version
-----------------
Sur la page d'un projet, cliquez sur le menu déroulant `ajouter` puis version.
Le numéro de version est obligatoire. Bien que le champ d'entrée accepte des caractères alphanumériques, il vous est demandé d'utiliser le format suivant::

        X[.Y[.Z]]


Ce choix vous permettra un affichage plus pertinent dans le cas de tri de version.

Les dates relatives à cette version (date de lancement du développement, date de prévision et date de publication) pourront être rentrées plus tard si vous le souhaitez.

Il est fortement conseillé d'avoir plusieurs versions en préparation; ce qui permettra de mieux répartir les livraisons et donc d'améliorer leurs qualités.

Après avoir valider la création de cette nouvelle version, vous pouvez allez sur la page de modification `modifier` et à partir du module d'édition des relations, il sera possible de sélectionner les tickets à inclure.

En ajoutant des tickets à une version, celle-ci possède maintenant un coût de développement qui correspond au total des coûts tickets. Si le coût devient trop important et risque de décaler la date de publication retenue; il est alors de la responsabilité du client de déplacer certains tickets vers une version ultérieure.

Le cycle d'une version
----------------------
Plusieurs états et transitions sont actuellement en place et couvre les besoins pour le déploiement de logiciel.

États
~~~~~

- prévue: pour organiser les livraisons dans le temps
- lancer le développement: cette transition est déclenchée automatiquement par la prise en compte d'un ticket
- prête: lorsque le développement et la recette sont terminées
- publier: lorsque le livrable est accessible depuis l'extérieur ou le client
- arrêter le développement: lorsque la sortie d'une version n'est plus pertinente

Cas de la compilation de paquets Debian
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
D'autres états ont été ajoutés récemment concernant la compilation automatique des paquets Debian.

À partir de l'état *prête*, les transitions suivantes sont disponible:

- lancer la compilation

Cette transition place la version en l'état *en compilation*. Les 2 états possibles sont alors:

- compilation réussie: les paquets debian ont été correctement compilés
- compilation en échec: la compilation n'a pu avoir lieu et les
