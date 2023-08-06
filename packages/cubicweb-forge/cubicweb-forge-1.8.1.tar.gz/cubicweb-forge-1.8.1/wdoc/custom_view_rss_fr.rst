.. -*- coding: utf-8 -*-
 
Flux RSS
--------

N'importe quel résultat de requête peut-être présenté
comme un flux RSS qu'il vous suffit d'enregistrer dans votre lecteur pour suivre l'activité de ce site.

Il n'existe pour l'instant qu'une seule ressource RSS visible liée aux prochaines versions de l'application.

    *<base url>*/project/*<nom du projet>*/versions

La vue par défaut peut être améliorée pour obtenir un flux des versions en mouvement:

    /view?rql=Any+X+WHERE+X+version_of+P%2C+P+name+"*<nom du projet>*"%2C+X+is+Version&vid=rss

Il peut être également utile de suivre les tickets relatifs à un projet. Pour cela, la requête RQL suivante peut être utilisée:

    /view?rql=Any+X+WHERE+X+concerns+P%2C+P+name+%22*<nom du projet>*%22%2C+X+is+Ticket&vid=rss

Il est important de noter que le paramètre **vid** disponible partout sur le site accepte dans ce cas la valeur rss.
La chaîne "?vid=rss" peut donc vous être assez utile pour la découverte des flux disponibles.

Pour avoir la liste des derniers commentaires postés dans l'application, vous pouvez utiliser la requête suivante:

    /view?vid=rss&amp;rql=Any%20X%20WHERE%20X%20is%20Comment%2C%20X%20creation_date%20M%20ORDERBY%20M%20DESC%20LIMIT%2010
