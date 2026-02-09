#!/usr/bin/env python3
"""
Script d'exemple pour créer et lancer une topologie Containernet.

Ce script peut être exécuté directement pour tester rapidement
une topologie réseau simulée.
"""

from src.simulator.topology import create_topology, load_topology_from_config
from src.simulator.network_simulator import NetworkSimulator
from mininet.net import Containernet
from mininet.node import Controller
from mininet.log import setLogLevel, info


def main():
    """Point d'entrée principal."""
    setLogLevel("info")
    
    # Charger la configuration
    try:
        simulator = NetworkSimulator(config_path="config/config.yaml")
        simulator.start(interactive=True)
    except FileNotFoundError:
        info("Configuration non trouvée, utilisation des valeurs par défaut\n")
        
        # Créer le réseau avec valeurs par défaut
        net = Containernet(controller=Controller)
        
        create_topology(
            net,
            topology_type="star",
            hosts=4,
            latency_ms=10,
            packet_loss=0.1,
            bandwidth_mbps=100,
            switch_name="s1"
        )
        
        net.start()
        info("*** Topologie démarrée. Utilisez 'exit' pour quitter.\n")
        
        from mininet.cli import CLI
        CLI(net)
        
        net.stop()


if __name__ == "__main__":
    main()
