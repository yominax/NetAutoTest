"""
Tests d'intégration pour les campagnes de tests.

Note: Ces tests nécessitent Containernet et des privilèges sudo.
Ils sont désactivés par défaut dans les tests unitaires.
"""

import pytest
import yaml
from pathlib import Path


@pytest.mark.integration
class TestCampaignIntegration:
    """Tests d'intégration pour les campagnes."""
    
    @pytest.fixture
    def test_config(self, tmp_path):
        """Crée une configuration de test."""
        config_file = tmp_path / "test_config.yaml"
        config = {
            "network": {
                "topology": "star",
                "hosts": 2,
                "latency_ms": 5,
                "packet_loss": 0.0,
                "bandwidth_mbps": 100
            },
            "tests": {
                "duration_seconds": 10,
                "iterations": 1,
                "protocols": ["tcp"],
                "thresholds": {
                    "max_latency_ms": 100,
                    "max_packet_loss_percent": 5.0,
                    "min_throughput_mbps": 1.0
                }
            },
            "reporting": {
                "formats": ["json"],
                "output_dir": str(tmp_path / "reports")
            }
        }
        
        with open(config_file, "w") as f:
            yaml.dump(config, f)
        
        return str(config_file)
    
    @pytest.mark.skip(reason="Nécessite Containernet et privilèges sudo")
    def test_campaign_run(self, test_config):
        """Test d'exécution complète d'une campagne."""
        from src.tests.run_test_campaign import TestCampaign
        
        campaign = TestCampaign(config_path=test_config)
        result = campaign.run()
        
        assert result is not None
        assert hasattr(result, "campaign_id")
        assert hasattr(result, "passed")
