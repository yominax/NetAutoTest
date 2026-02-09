"""
Tests unitaires pour le wrapper iperf3.
"""

import pytest
from unittest.mock import Mock, patch
from src.tests.iperf_wrapper import IperfTest, IperfResult


class TestIperfTest:
    """Tests pour la classe IperfTest."""
    
    def test_init(self):
        """Test de l'initialisation."""
        server = Mock()
        client = Mock()
        test = IperfTest(server, client, port=5001)
        
        assert test.server_host == server
        assert test.client_host == client
        assert test.port == 5001
        assert test.server_process is None
    
    def test_start_server_tcp(self):
        """Test du démarrage du serveur TCP."""
        server = Mock()
        client = Mock()
        test = IperfTest(server, client)
        
        server.popen = Mock(return_value=Mock())
        
        test.start_server(protocol="tcp")
        
        assert test.server_process is not None
        server.popen.assert_called_once()
    
    def test_start_server_udp(self):
        """Test du démarrage du serveur UDP."""
        server = Mock()
        client = Mock()
        test = IperfTest(server, client)
        
        server.popen = Mock(return_value=Mock())
        
        test.start_server(protocol="udp")
        
        assert test.server_process is not None
    
    def test_stop_server(self):
        """Test de l'arrêt du serveur."""
        server = Mock()
        client = Mock()
        test = IperfTest(server, client)
        
        mock_process = Mock()
        mock_process.wait = Mock()
        test.server_process = mock_process
        
        test.stop_server()
        
        assert test.server_process is None
        mock_process.terminate.assert_called_once()
    
    def test_parse_json_result_tcp(self):
        """Test du parsing JSON pour TCP."""
        server = Mock()
        client = Mock()
        test = IperfTest(server, client)
        
        json_output = """
        {
            "end": {
                "sum_sent": {
                    "bits_per_second": 1000000000,
                    "bytes": 1000000,
                    "retransmits": 5
                },
                "sum_received": {
                    "bits_per_second": 1000000000,
                    "bytes": 1000000
                }
            }
        }
        """
        
        result = test._parse_json_result(json_output, "tcp", 60)
        
        assert result.protocol == "tcp"
        assert result.throughput_mbps == 1000.0
        assert result.retransmissions == 5
    
    def test_parse_json_result_udp(self):
        """Test du parsing JSON pour UDP."""
        server = Mock()
        client = Mock()
        test = IperfTest(server, client)
        
        json_output = """
        {
            "end": {
                "sum": {
                    "bits_per_second": 500000000,
                    "bytes": 500000,
                    "lost_percent": 0.5,
                    "jitter_ms": 2.5
                }
            }
        }
        """
        
        result = test._parse_json_result(json_output, "udp", 60)
        
        assert result.protocol == "udp"
        assert result.throughput_mbps == 500.0
        assert result.packet_loss == 0.5
        assert result.jitter_ms == 2.5
