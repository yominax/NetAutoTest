Configuration
==============

Le fichier de configuration principal est ``config/config.yaml``. Il permet de personnaliser tous les aspects du framework.

Structure de configuration
--------------------------

Réseau
~~~~~~

Configuration de la topologie réseau simulée :

.. code-block:: yaml

   network:
     topology: "star"  # "star", "line", ou "mesh"
     hosts: 4
     latency_ms: 10
     packet_loss: 0.1
     bandwidth_mbps: 100
     switch_name: "s1"

Tests
~~~~~

Configuration des tests de performance :

.. code-block:: yaml

   tests:
     duration_seconds: 60
     iterations: 5
     delay_between_iterations: 10
     protocols: ["tcp", "udp"]
     ports:
       tcp: 5001
       udp: 5002
     thresholds:
       max_latency_ms: 50
       max_packet_loss_percent: 1.0
       max_jitter_ms: 5
       min_throughput_mbps: 10

Monitoring
~~~~~~~~~~

Configuration du monitoring :

.. code-block:: yaml

   monitoring:
     scrape_interval: 5
     prometheus_port: 9090
     grafana_port: 3000
     metrics:
       - latency
       - throughput
       - packet_loss
       - jitter
       - cpu_usage
       - memory_usage
       - network_io

Rapports
~~~~~~~~

Configuration de la génération de rapports :

.. code-block:: yaml

   reporting:
     formats: ["json", "html"]
     output_dir: "reports"
     include_graphs: true
     graph_style: "plotly"

Exemples de configurations
--------------------------

Topologie en ligne avec haute latence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   network:
     topology: "line"
     hosts: 6
     latency_ms: 50
     packet_loss: 0.5
     bandwidth_mbps: 50

Tests intensifs
~~~~~~~~~~~~~~~~

.. code-block:: yaml

   tests:
     duration_seconds: 300
     iterations: 10
     protocols: ["tcp"]
     thresholds:
       max_latency_ms: 100
       min_throughput_mbps: 5
