.. -*- coding: utf-8 -*-
 
Dernières modifications
-----------------------

* la table des `derniers changements`_ fournit un exemple d'utilisation de RQL
  pour récupérer les derniers changements ayant eu lieu sur ce site.
* un autre exemple: la table des `dernières versions publiées`_

.. _`derniers changements`: view?rql=Any+M%2CX+WHERE+X+modification_date+M+ORDERBY+M+DESC+LIMIT+30
.. _`dernières versions publiées`:  view?rql=Any+M%2CP%2CE+WHERE+E+is+Version%2C+E+publication_date+M%2C+E+in_state+S%2C+S+name+%27published%27%2C+E+version_of+P+ORDERBY+M+DESC 


