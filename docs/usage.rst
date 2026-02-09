Guide d'utilisation
====================

Démarrer une simulation réseau
-------------------------------

Pour démarrer une simulation réseau simple :

.. code-block:: bash

   make sim

Ou manuellement :

.. code-block:: bash

   python src/simulator/network_simulator.py start

Pour une session interactive :

.. code-block:: bash

   python src/simulator/network_simulator.py start --interactive

Exécuter une campagne de tests
-------------------------------

Campagne complète avec configuration par défaut :

.. code-block:: bash

   make test

Avec configuration personnalisée :

.. code-block:: bash

   python src/tests/run_test_campaign.py --config config/config.yaml

Le script va :

1. Démarrer la simulation réseau
2. Exécuter les tests iperf3 (TCP et UDP)
3. Exécuter les tests de latence
4. Valider les résultats par rapport aux seuils
5. Générer les rapports (JSON et HTML)

Monitoring en temps réel
------------------------

Démarrer Prometheus et Grafana :

.. code-block:: bash

   make monitor

Accéder aux interfaces :

* Prometheus : http://localhost:9090
* Grafana : http://localhost:3000 (admin/admin)

Arrêter le monitoring :

.. code-block:: bash

   make monitor-stop

Générer la documentation
------------------------

.. code-block:: bash

   make docs

La documentation sera disponible dans ``docs/_build/html/index.html``.

Pour servir la documentation localement :

.. code-block:: bash

   make docs-serve

Puis ouvrir http://localhost:8000 dans votre navigateur.

Exemples de configuration
-------------------------

Voir la section :doc:`configuration` pour des exemples détaillés de configuration.
