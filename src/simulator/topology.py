"""
Définition des topologies réseau pour Containernet.

Ce module fournit des fonctions pour créer différentes topologies réseau
simulées utilisant Containernet (Mininet + Docker).
"""

from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.log import info, setLogLevel
from mininet.link import TCLink
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


def create_topology(
    net: Containernet,
    topology_type: str = "star",
    hosts: int = 4,
    latency_ms: int = 10,
    packet_loss: float = 0.1,
    bandwidth_mbps: Optional[int] = None,
    switch_name: str = "s1"
) -> Containernet:
    """
    Crée une topologie réseau selon le type spécifié.
    
    Args:
        net: Instance Containernet
        topology_type: Type de topologie ("star", "line", "mesh")
        hosts: Nombre d'hôtes à créer
        latency_ms: Latence des liens en millisecondes
        packet_loss: Perte de paquets en pourcentage (0.0-100.0)
        bandwidth_mbps: Bande passante en Mbps (None pour illimité)
        switch_name: Nom du switch principal
        
    Returns:
        Réseau Containernet configuré
        
    Raises:
        ValueError: Si le type de topologie n'est pas supporté
    """
    info(f"*** Création de la topologie {topology_type} avec {hosts} hôtes\n")
    
    # Ajouter le contrôleur
    net.addController("c0")
    
    # Créer le switch
    switch = net.addSwitch(switch_name)
    
    # Créer les hôtes Docker
    host_list = []
    for i in range(1, hosts + 1):
        host_name = f"h{i}"
        # Utiliser une image Docker légère avec les outils réseau
        host = net.addDocker(
            host_name,
            dimage="ubuntu:22.04",
            ip=f"10.0.0.{i}/24",
            dcmd="bash",
            cpu_period=50000,
            cpu_quota=25000
        )
        host_list.append(host)
        info(f"*** Hôte {host_name} créé avec IP 10.0.0.{i}\n")
    
    # Configurer les liens selon la topologie
    if topology_type == "star":
        _create_star_topology(net, switch, host_list, latency_ms, packet_loss, bandwidth_mbps)
    elif topology_type == "line":
        _create_line_topology(net, switch, host_list, latency_ms, packet_loss, bandwidth_mbps)
    elif topology_type == "mesh":
        _create_mesh_topology(net, host_list, latency_ms, packet_loss, bandwidth_mbps)
    else:
        raise ValueError(f"Topologie non supportée: {topology_type}")
    
    return net


def _create_star_topology(
    net: Containernet,
    switch: Any,
    hosts: list,
    latency_ms: int,
    packet_loss: float,
    bandwidth_mbps: Optional[int]
):
    """Crée une topologie en étoile (tous les hôtes connectés au switch)."""
    info("*** Configuration topologie STAR\n")
    
    link_params = {
        "delay": f"{latency_ms}ms",
        "loss": packet_loss,
    }
    if bandwidth_mbps:
        link_params["bw"] = bandwidth_mbps
    
    for host in hosts:
        net.addLink(host, switch, cls=TCLink, **link_params)
        info(f"*** Lien créé: {host.name} <-> {switch.name}\n")


def _create_line_topology(
    net: Containernet,
    switch: Any,
    hosts: list,
    latency_ms: int,
    packet_loss: float,
    bandwidth_mbps: Optional[int]
):
    """Crée une topologie linéaire (hôtes connectés en chaîne)."""
    info("*** Configuration topologie LINE\n")
    
    link_params = {
        "delay": f"{latency_ms}ms",
        "loss": packet_loss,
    }
    if bandwidth_mbps:
        link_params["bw"] = bandwidth_mbps
    
    # Connecter le premier hôte au switch
    if hosts:
        net.addLink(hosts[0], switch, cls=TCLink, **link_params)
        
        # Connecter les hôtes entre eux
        for i in range(len(hosts) - 1):
            net.addLink(hosts[i], hosts[i + 1], cls=TCLink, **link_params)
            info(f"*** Lien créé: {hosts[i].name} <-> {hosts[i+1].name}\n")


def _create_mesh_topology(
    net: Containernet,
    hosts: list,
    latency_ms: int,
    packet_loss: float,
    bandwidth_mbps: Optional[int]
):
    """Crée une topologie maillée (tous les hôtes connectés entre eux)."""
    info("*** Configuration topologie MESH\n")
    
    link_params = {
        "delay": f"{latency_ms}ms",
        "loss": packet_loss,
    }
    if bandwidth_mbps:
        link_params["bw"] = bandwidth_mbps
    
    # Connecter chaque hôte à tous les autres
    for i, host1 in enumerate(hosts):
        for host2 in hosts[i + 1:]:
            net.addLink(host1, host2, cls=TCLink, **link_params)
            info(f"*** Lien créé: {host1.name} <-> {host2.name}\n")


def load_topology_from_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Charge la configuration de topologie depuis un fichier YAML.
    
    Args:
        config_path: Chemin vers le fichier de configuration
        
    Returns:
        Dictionnaire de configuration
    """
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Fichier de configuration non trouvé: {config_path}")
    
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    return config.get("network", {})


if __name__ == "__main__":
    # Exemple d'utilisation
    setLogLevel("info")
    
    # Charger la configuration
    try:
        network_config = load_topology_from_config()
    except FileNotFoundError:
        # Configuration par défaut
        network_config = {
            "topology": "star",
            "hosts": 4,
            "latency_ms": 10,
            "packet_loss": 0.1,
            "bandwidth_mbps": 100,
            "switch_name": "s1"
        }
    
    # Créer le réseau
    net = Containernet(controller=Controller)
    
    create_topology(
        net,
        topology_type=network_config.get("topology", "star"),
        hosts=network_config.get("hosts", 4),
        latency_ms=network_config.get("latency_ms", 10),
        packet_loss=network_config.get("packet_loss", 0.1),
        bandwidth_mbps=network_config.get("bandwidth_mbps"),
        switch_name=network_config.get("switch_name", "s1")
    )
    
    # Démarrer le réseau
    net.start()
    
    # Lancer le CLI interactif
    info("*** Topologie démarrée. Utilisez 'exit' pour quitter.\n")
    CLI(net)
    
    # Arrêter le réseau
    net.stop()
