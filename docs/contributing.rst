Contribuer
===========

Nous sommes ravis que vous souhaitiez contribuer à NetAutoTest !

Comment contribuer
-------------------

1. Fork le projet
2. Créer une branche pour votre fonctionnalité (``git checkout -b feature/AmazingFeature``)
3. Commit vos changements (``git commit -m 'Add AmazingFeature'``)
4. Push vers la branche (``git push origin feature/AmazingFeature``)
5. Ouvrir une Pull Request

Standards de code
------------------

* Suivre PEP 8 pour le style Python
* Ajouter des docstrings pour toutes les fonctions et classes
* Écrire des tests pour les nouvelles fonctionnalités
* Mettre à jour la documentation si nécessaire

Tests
-----

Avant de soumettre une PR, assurez-vous que tous les tests passent :

.. code-block:: bash

   pytest tests/unit/ -v
   pytest tests/integration/ -v

Linting
-------

Vérifier le code avec flake8 :

.. code-block:: bash

   make lint

Formatage
---------

Formater le code avec black :

.. code-block:: bash

   make format

Documentation
-------------

Si vous ajoutez de nouvelles fonctionnalités, mettez à jour la documentation :

.. code-block:: bash

   make docs
