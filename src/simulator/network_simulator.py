"""
Gestionnaire principal de simulation réseau.

Ce module fournit une interface pour démarrer et arrêter facilement
la simulation réseau Containernet.
"""

import sys
import signal
import yaml
from pathlib import Path
from typing import Optional
from loguru import logger
from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from .topology import create_topology, load_topology_from_config


class NetworkSimulator:
    """
    Gestionnaire de simulation réseau avec Containernet.
    
    Cette classe encapsule la création et la gestion d'un réseau simulé,
    permettant de démarrer et arrêter facilement la topologie.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialise le simulateur réseau.
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config_path = config_path
        self.net: Optional[Containernet] = None
        self.config: dict = {}
        self._load_config()
        
        # Configuration des logs
        logger.add(
            "logs/network_simulator.log",
            rotation="10 MB",
            retention="7 days",
            level="INFO"
        )
    
    def _load_config(self):
        """Charge la configuration depuis le fichier YAML."""
        try:
            self.config = load_topology_from_config(self.config_path)
        except FileNotFoundError:
            logger.warning(f"Configuration non trouvée: {self.config_path}, utilisation des valeurs par défaut")
            self.config = {
                "topology": "star",
                "hosts": 4,
                "latency_ms": 10,
                "packet_loss": 0.1,
                "bandwidth_mbps": 100,
                "switch_name": "s1"
            }
    
    def start(self, interactive: bool = False):
        """
        Démarre la simulation réseau.
        
        Args:
            interactive: Si True, lance le CLI interactif après démarrage
        """
        if self.net is not None:
            logger.warning("Le réseau est déjà démarré")
            return
        
        logger.info("Démarrage de la simulation réseau...")
        setLogLevel("info")
        
        # Créer le réseau
        self.net = Containernet(controller=Controller)
        
        # Créer la topologie
        create_topology(
            self.net,
            topology_type=self.config.get("topology", "star"),
            hosts=self.config.get("hosts", 4),
            latency_ms=self.config.get("latency_ms", 10),
            packet_loss=self.config.get("packet_loss", 0.1),
            bandwidth_mbps=self.config.get("bandwidth_mbps"),
            switch_name=self.config.get("switch_name", "s1")
        )
        
        # Démarrer le réseau
        self.net.start()
        logger.info("✅ Réseau démarré avec succès")
        
        # Enregistrer le handler pour arrêt propre
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        if interactive:
            info("*** Topologie démarrée. Utilisez 'exit' pour quitter.\n")
            CLI(self.net)
            self.stop()
    
    def stop(self):
        """Arrête la simulation réseau."""
        if self.net is None:
            logger.warning("Aucun réseau n'est démarré")
            return
        
        logger.info("Arrêt de la simulation réseau...")
        self.net.stop()
        self.net = None
        logger.info("✅ Réseau arrêté")
    
    def _signal_handler(self, signum, frame):
        """Handler pour les signaux d'arrêt."""
        logger.info(f"Signal {signum} reçu, arrêt du réseau...")
        self.stop()
        sys.exit(0)
    
    def get_host(self, host_name: str):
        """
        Récupère un hôte par son nom.
        
        Args:
            host_name: Nom de l'hôte (ex: "h1")
            
        Returns:
            Instance de l'hôte ou None si non trouvé
        """
        if self.net is None:
            logger.error("Le réseau n'est pas démarré")
            return None
        
        try:
            return self.net.get(host_name)
        except KeyError:
            logger.error(f"Hôte '{host_name}' non trouvé")
            return None
    
    def get_all_hosts(self):
        """
        Récupère tous les hôtes du réseau.
        
        Returns:
            Liste des hôtes
        """
        if self.net is None:
            logger.error("Le réseau n'est pas démarré")
            return []
        
        return self.net.hosts
    
    def ping_all(self):
        """Teste la connectivité entre tous les hôtes."""
        if self.net is None:
            logger.error("Le réseau n'est pas démarré")
            return
        
        logger.info("Test de connectivité (ping all)...")
        self.net.pingAll()


def main():
    """Point d'entrée principal pour le script CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gestionnaire de simulation réseau NetAutoTest")
    parser.add_argument(
        "action",
        choices=["start", "stop", "restart"],
        help="Action à effectuer"
    )
    parser.add_argument(
        "--config",
        default="config/config.yaml",
        help="Chemin vers le fichier de configuration"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Lancer le CLI interactif après démarrage"
    )
    
    args = parser.parse_args()
    
    simulator = NetworkSimulator(config_path=args.config)
    
    if args.action == "start":
        simulator.start(interactive=args.interactive)
    elif args.action == "stop":
        simulator.stop()
    elif args.action == "restart":
        simulator.stop()
        simulator.start(interactive=args.interactive)


if __name__ == "__main__":
    main()
