.. -*- coding: utf-8 -*-

Créer un nouveau projet
-----------------------

Tout développeur est encouragé à créer un projet. La bonne pratique est de considérer chaque paquet Debian livré comme un projet potentiel. Notez cependant que le dépôt du code dans mercurial n'est pas créé à la volée mais nécessite certainement une demande auprès de votre administrateur.

Sur la page principale, un lien vous est proposé, seul le nom est obligatoire. Il est ensuite visible depuis cette même page.

Si le projet existe déjà dans votre dépôt de source et qu'il est accessible par HTTP, il peut être intéressant de remplir le champ `url du système de gestion de sources`. Ceci vous permettra de naviguer dans le code source du projet directement à partir de la forge.

Ajouter un ticket
-----------------

Les tickets sont utilisés pour exprimer les demandes puis leur affecter une priorité et les rassembler dans des versions. En attribuant un coût à chaque ticket (en jour.homme le plus souvent), il est possible de prévoir la charge de travail nécessaire à la production d'une version.

Deux types de tickets existent actuellement:

- les histoires utilisateurs permettent d'exprimer les besoins et constituent des demandes d'ajout de nouvelles fonctionnalités,
- les anomalies concernent les versions déjà publiées et constituent des demandes de correction de disfonctionnement ou de régression.

Un ticket se doit d'être concis, posséder une seule problématique et ne doit pas mélanger besoin fonctionnel et choix techniques. La discussion technique liée à la réalisation du ticket doit être tenue sous forme de commentaires, l'expérience montrant que la solution finale diffère très souvent de la première proposition technique.

Pour ajouter un ticket, vous devez, à partir d'une page de projet, cliquer sur le menu déroulant `ajouter` dans la colonne des actions en haut à gauche de la page de projet. L'entrée `ticket` est alors visible. Après avoir créé un ticket, il est possible de le modifier et d'ajouter des relations.

Exemple d'ajout de relation: à partir de la page action `modifier`, vous trouverez en bas de page au dessus du bouton `valider` une boîte déroulante qui permet d'ajouter des relations. Si votre ticket a un lien quelconque avec un autre objet, vous pouvez choisir la relation **voir aussi**. Une liste déroulante vous sera alors proposée pour nouer la nouvelle relation. Vous pouvez faire cela autant de fois que vous souhaitez. Plusieurs relations sont proposées. Les plus utilisées sont: **see also**, **tagged by**, **depends on**. 

Cycle de vie d'un ticket
---------------------------

Les tickets peuvent avoir plusieurs états qui sont atteignables par les transitions disponibles. Ainsi chaque état n'est pas forcément atteignable directement. Pour se familiariser avec les états et transitions par défaut, vous pouvez vous référer à sa page de workflow_.

.. _`workflow`: cwetype/Ticket?tab=cwetype-workflow

Ajouter une fiche de documentation
------------------------------------

Les fiches de documentation sont utiles à un projet lorsque celles-ci sont fréquemment consultées. Elles apparaîtront en bas de la page de projet.


Ajouter une image
--------------------

Il est possible que la création d'entité d'image ne soit pas immédiatement disponible. Il est alors possible de passer par l'`url suivante`__ pour l'ajout d'une image.

__ add/Image

Pour voir l'ensemble des objets de type Image dans la forge, vous pouvez visiter l'`url suivante`__.

__ image

Ajouter une version
-------------------

Une version représente un certain état de l'avancement du projet. Elles permettent de prévoir les prochaines échéances. Il est fortement conseillé de prévoir plusieurs versions à l'avance. Si jamais la réalisation d'un ticket prévu pour une version n'est plus possible, il est préférable de décaler le ticket à la version suivante plutôt que de retarder la version.

Les versions possèdent leurs propres workflow__. Il est important de tenir à jour ces informations car ce sont elles qui permettent la planification du projet.

__  cwetype/Version?tab=cwetype-workflow


