Installation
=============

Prérequis
---------

* Linux (Ubuntu 22.04/24.04 recommandé)
* Python 3.11+
* Docker & Docker Compose
* Privilèges sudo (pour Containernet)

Installation automatique
-------------------------

.. code-block:: bash

   git clone https://github.com/yominax/NetAutoTest.git
   cd NetAutoTest
   make install

Installation manuelle
---------------------

1. Installer les dépendances système :

.. code-block:: bash

   sudo apt-get update
   sudo apt-get install -y python3-pip python3-venv docker.io docker-compose iperf3

2. Créer un environnement virtuel :

.. code-block:: bash

   python3 -m venv venv
   source venv/bin/activate

3. Installer les dépendances Python :

.. code-block:: bash

   pip install -r requirements.txt

4. Installer Containernet :

.. code-block:: bash

   sudo make install-containernet

Vérification de l'installation
-------------------------------

Pour vérifier que tout est correctement installé :

.. code-block:: bash

   python --version  # Doit afficher Python 3.11+
   iperf3 --version
   docker --version
   docker-compose --version

Test rapide
-----------

Lancer une simulation réseau simple :

.. code-block:: bash

   make sim

Puis dans un autre terminal :

.. code-block:: bash

   make test
