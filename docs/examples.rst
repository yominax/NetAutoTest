Exemples
=========

Exemple 1 : Campagne de tests simple
-------------------------------------

.. code-block:: python

   from src.tests.run_test_campaign import TestCampaign
   
   campaign = TestCampaign(config_path="config/config.yaml")
   result = campaign.run()
   
   print(f"Campagne {'réussie' if result.passed else 'échouée'}")
   print(f"Tests iperf3: {len(result.iperf_results)}")
   print(f"Tests de latence: {len(result.latency_results)}")

Exemple 2 : Test iperf3 personnalisé
-------------------------------------

.. code-block:: python

   from src.simulator.network_simulator import NetworkSimulator
   from src.tests.iperf_wrapper import IperfTest
   
   simulator = NetworkSimulator()
   simulator.start()
   
   hosts = simulator.get_all_hosts()
   server = hosts[0]
   client = hosts[1]
   
   iperf_test = IperfTest(server, client, port=5001)
   result = iperf_test.run_test(protocol="tcp", duration=60)
   
   print(f"Débit: {result.throughput_mbps:.2f} Mbps")
   print(f"Retransmissions: {result.retransmissions}")
   
   simulator.stop()

Exemple 3 : Test de latence
----------------------------

.. code-block:: python

   from src.simulator.network_simulator import NetworkSimulator
   from src.tests.latency_test import LatencyTest
   
   simulator = NetworkSimulator()
   simulator.start()
   
   hosts = simulator.get_all_hosts()
   server = hosts[0]
   client = hosts[1]
   
   latency_test = LatencyTest(server, client)
   result = latency_test.run_test(duration=60, interval=1.0)
   
   print(f"RTT moyen: {result.rtt_mean_ms:.2f} ms")
   print(f"Jitter: {result.jitter_ms:.2f} ms")
   print(f"Perte: {result.packet_loss_percent:.2f}%")
   
   simulator.stop()

Exemple 4 : Monitoring avec sondes
-----------------------------------

.. code-block:: python

   from src.monitoring.probe import NetworkProbe
   import time
   
   probe = NetworkProbe(hostname="h1", port=8080)
   probe.start()
   
   # Enregistrer des métriques
   probe.record_latency("10.0.0.2", 25.5)
   probe.record_packet_loss(0.5)
   probe.record_throughput("sent", 100.0)
   
   time.sleep(60)  # Laisser tourner pendant 1 minute
   
   probe.stop()
