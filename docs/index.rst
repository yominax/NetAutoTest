NetAutoTest Documentation
==========================

**NetAutoTest** est un framework DevOps complet pour l'automatisation de tests de performance et le monitoring réseau sur un réseau local simulé.

.. toctree::
   :maxdepth: 2
   :caption: Contenu:

   installation
   architecture
   usage
   api
   configuration
   examples
   contributing

Introduction
------------

NetAutoTest permet de :

* ✅ Automatiser des campagnes de tests de performance (latence, débit, jitter, perte de paquets)
* ✅ Simuler des réseaux TCP/IP réalistes avec Containernet
* ✅ Déployer des sondes de supervision en temps réel
* ✅ Intégrer tout dans un pipeline CI/CD avec GitHub Actions
* ✅ Générer automatiquement une documentation technique complète

Installation rapide
-------------------

.. code-block:: bash

   git clone https://github.com/yourusername/NetAutoTest.git
   cd NetAutoTest
   make install
   make test

Architecture
------------

Le framework est organisé en plusieurs modules :

* **simulator** : Simulation réseau avec Containernet
* **tests** : Tests de performance (iperf3, latence)
* **monitoring** : Sondes Prometheus et génération de rapports
* **utils** : Utilitaires et helpers

Pour plus de détails, consultez la section :doc:`architecture`.

Indices et tables
-----------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
