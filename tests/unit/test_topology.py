"""
Tests unitaires pour le module topology.
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.simulator.topology import create_topology, load_topology_from_config


class TestTopology:
    """Tests pour les fonctions de topologie."""
    
    def test_load_topology_from_config(self, tmp_path):
        """Test du chargement de configuration."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
network:
  topology: "star"
  hosts: 4
  latency_ms: 10
  packet_loss: 0.1
""")
        
        config = load_topology_from_config(str(config_file))
        
        assert config["topology"] == "star"
        assert config["hosts"] == 4
        assert config["latency_ms"] == 10
    
    def test_load_topology_from_config_not_found(self):
        """Test avec fichier de configuration inexistant."""
        with pytest.raises(FileNotFoundError):
            load_topology_from_config("nonexistent.yaml")
    
    def test_create_topology_star(self):
        """Test de création d'une topologie en étoile."""
        net = Mock()
        net.addController = Mock()
        net.addSwitch = Mock(return_value=Mock())
        net.addDocker = Mock(return_value=Mock())
        net.addLink = Mock()
        
        switch = Mock()
        net.addSwitch.return_value = switch
        
        hosts = [Mock() for _ in range(4)]
        for i, host in enumerate(hosts):
            host.name = f"h{i+1}"
            net.addDocker.return_value = host
        
        create_topology(
            net,
            topology_type="star",
            hosts=4,
            latency_ms=10,
            packet_loss=0.1
        )
        
        assert net.addController.called
        assert net.addSwitch.called
        assert net.addDocker.call_count == 4
    
    def test_create_topology_invalid(self):
        """Test avec un type de topologie invalide."""
        net = Mock()
        
        with pytest.raises(ValueError):
            create_topology(net, topology_type="invalid")
