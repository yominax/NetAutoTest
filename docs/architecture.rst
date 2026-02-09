Architecture
=============

Vue d'ensemble
--------------

NetAutoTest est organisé en plusieurs modules principaux qui travaillent ensemble pour fournir un framework complet de tests réseau automatisés.

Modules principaux
-------------------

Simulateur Réseau (simulator)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Le module ``simulator`` gère la création et la gestion de topologies réseau simulées avec Containernet.

* ``topology.py`` : Définit les différentes topologies (star, line, mesh)
* ``network_simulator.py`` : Gestionnaire principal pour démarrer/arrêter les simulations

Tests de Performance (tests)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Le module ``tests`` contient tous les scripts de tests de performance.

* ``iperf_wrapper.py`` : Wrapper Python pour iperf3
* ``latency_test.py`` : Tests de latence personnalisés avec paquets timestampés
* ``run_test_campaign.py`` : Orchestrateur principal des campagnes de tests

Monitoring (monitoring)
~~~~~~~~~~~~~~~~~~~~~~~~

Le module ``monitoring`` gère la collecte de métriques et la génération de rapports.

* ``probe.py`` : Sondes Prometheus pour le monitoring en temps réel
* ``report_generator.py`` : Génération de rapports HTML avec graphiques

Flux de données
---------------

.. mermaid::

   graph TB
       A[Campagne de Tests] --> B[Démarrage Réseau]
       B --> C[Tests iperf3]
       B --> D[Tests Latence]
       C --> E[Collecte Métriques]
       D --> E
       E --> F[Validation Seuils]
       F --> G[Génération Rapports]
       G --> H[HTML/JSON]

Topologie réseau
----------------

Par défaut, NetAutoTest crée une topologie en étoile avec :

* 1 switch central
* 4 hôtes Docker (2 clients, 2 serveurs)
* Liens configurables (latence, perte, bande passante)

La topologie peut être modifiée via le fichier ``config/config.yaml``.

Monitoring en temps réel
-------------------------

Les sondes de monitoring sont déployées dans chaque conteneur Docker et :

* Collectent des métriques système (CPU, mémoire)
* Mesurent la latence réseau
* Exposent les métriques via Prometheus
* Visualisent les données dans Grafana
