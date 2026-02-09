"""
Wrapper Python pour iperf3 - Tests de débit TCP/UDP.

Ce module fournit une interface Python pour exécuter des tests iperf3
et parser les résultats.
"""

import subprocess
import json
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from loguru import logger


@dataclass
class IperfResult:
    """Résultat d'un test iperf3."""
    protocol: str  # "tcp" ou "udp"
    duration: float  # Durée du test en secondes
    throughput_mbps: float  # Débit en Mbps
    retransmissions: Optional[int] = None  # Nombre de retransmissions (TCP)
    packet_loss: Optional[float] = None  # Perte de paquets en % (UDP)
    jitter_ms: Optional[float] = None  # Jitter en ms (UDP)
    bytes_sent: Optional[int] = None
    bytes_received: Optional[int] = None


class IperfTest:
    """
    Classe pour exécuter des tests iperf3 entre deux hôtes.
    
    Cette classe permet de lancer des tests de débit TCP et UDP
    et de récupérer les résultats structurés.
    """
    
    def __init__(self, server_host, client_host, port: int = 5001):
        """
        Initialise un test iperf3.
        
        Args:
            server_host: Hôte serveur (objet Mininet host)
            client_host: Hôte client (objet Mininet host)
            port: Port à utiliser pour le test
        """
        self.server_host = server_host
        self.client_host = client_host
        self.port = port
        self.server_process: Optional[subprocess.Popen] = None
    
    def start_server(self, protocol: str = "tcp"):
        """
        Démarre le serveur iperf3.
        
        Args:
            protocol: "tcp" ou "udp"
        """
        if self.server_process is not None:
            logger.warning("Le serveur iperf3 est déjà démarré")
            return
        
        # Construire la commande iperf3
        cmd = ["iperf3", "-s", "-p", str(self.port), "-1"]
        if protocol == "udp":
            cmd.append("-u")
        
        logger.info(f"Démarrage du serveur iperf3 sur {self.server_host.name}:{self.port}")
        
        # Exécuter sur l'hôte serveur
        self.server_process = self.server_host.popen(cmd)
        time.sleep(1)  # Attendre que le serveur démarre
    
    def stop_server(self):
        """Arrête le serveur iperf3."""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            self.server_process = None
            logger.info("Serveur iperf3 arrêté")
    
    def run_test(
        self,
        protocol: str = "tcp",
        duration: int = 60,
        bitrate: Optional[str] = None,
        json_output: bool = True
    ) -> IperfResult:
        """
        Exécute un test iperf3.
        
        Args:
            protocol: "tcp" ou "udp"
            duration: Durée du test en secondes
            bitrate: Débit cible (ex: "10M" pour 10 Mbps, None pour illimité)
            json_output: Utiliser le format JSON pour la sortie
            
        Returns:
            Résultat du test
            
        Raises:
            RuntimeError: Si le test échoue
        """
        if self.server_process is None:
            self.start_server(protocol)
        
        # Construire la commande client
        cmd = [
            "iperf3",
            "-c", self.server_host.IP(),
            "-p", str(self.port),
            "-t", str(duration),
        ]
        
        if protocol == "udp":
            cmd.append("-u")
            if bitrate:
                cmd.extend(["-b", bitrate])
        
        if json_output:
            cmd.append("-J")
        
        logger.info(f"Exécution du test iperf3 ({protocol}) de {duration}s...")
        
        try:
            # Exécuter sur l'hôte client
            result = self.client_host.cmd(cmd)
            
            if json_output:
                return self._parse_json_result(result, protocol, duration)
            else:
                return self._parse_text_result(result, protocol, duration)
        
        except Exception as e:
            logger.error(f"Erreur lors du test iperf3: {e}")
            raise RuntimeError(f"Test iperf3 échoué: {e}")
    
    def _parse_json_result(self, output: str, protocol: str, duration: int) -> IperfResult:
        """Parse le résultat JSON d'iperf3."""
        try:
            data = json.loads(output)
            
            # Extraire les informations selon le protocole
            if protocol == "tcp":
                end_data = data.get("end", {})
                sum_sent = end_data.get("sum_sent", {})
                sum_received = end_data.get("sum_received", {})
                
                throughput_mbps = sum_received.get("bits_per_second", 0) / 1e6
                retransmissions = sum_sent.get("retransmits", 0)
                bytes_sent = sum_sent.get("bytes", 0)
                bytes_received = sum_received.get("bytes", 0)
                
                return IperfResult(
                    protocol=protocol,
                    duration=duration,
                    throughput_mbps=throughput_mbps,
                    retransmissions=retransmissions,
                    bytes_sent=bytes_sent,
                    bytes_received=bytes_received
                )
            
            else:  # UDP
                end_data = data.get("end", {})
                sum_data = end_data.get("sum", {})
                
                throughput_mbps = sum_data.get("bits_per_second", 0) / 1e6
                packet_loss = sum_data.get("lost_percent", 0)
                jitter_ms = sum_data.get("jitter_ms", 0)
                bytes_sent = sum_data.get("bytes", 0)
                bytes_received = sum_data.get("bytes", 0)
                
                return IperfResult(
                    protocol=protocol,
                    duration=duration,
                    throughput_mbps=throughput_mbps,
                    packet_loss=packet_loss,
                    jitter_ms=jitter_ms,
                    bytes_sent=bytes_sent,
                    bytes_received=bytes_received
                )
        
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Erreur lors du parsing JSON: {e}")
            raise RuntimeError(f"Impossible de parser le résultat iperf3: {e}")
    
    def _parse_text_result(self, output: str, protocol: str, duration: int) -> IperfResult:
        """Parse le résultat texte d'iperf3 (fallback)."""
        # Parsing basique du format texte
        lines = output.split("\n")
        throughput_mbps = 0.0
        
        for line in lines:
            if "bits/sec" in line.lower():
                # Extraire le débit
                parts = line.split()
                for i, part in enumerate(parts):
                    if "bits/sec" in part.lower():
                        try:
                            value = float(parts[i - 1])
                            unit = parts[i].lower()
                            if "g" in unit:
                                throughput_mbps = value * 1000
                            elif "m" in unit:
                                throughput_mbps = value
                            elif "k" in unit:
                                throughput_mbps = value / 1000
                            break
                        except (ValueError, IndexError):
                            pass
        
        return IperfResult(
            protocol=protocol,
            duration=duration,
            throughput_mbps=throughput_mbps
        )
    
    def run_multiple_tests(
        self,
        protocol: str = "tcp",
        duration: int = 60,
        iterations: int = 5,
        delay: int = 10
    ) -> List[IperfResult]:
        """
        Exécute plusieurs tests consécutifs.
        
        Args:
            protocol: "tcp" ou "udp"
            duration: Durée de chaque test
            iterations: Nombre d'itérations
            delay: Délai entre les tests (secondes)
            
        Returns:
            Liste des résultats
        """
        results = []
        
        for i in range(iterations):
            logger.info(f"Itération {i+1}/{iterations}")
            result = self.run_test(protocol=protocol, duration=duration)
            results.append(result)
            
            if i < iterations - 1:
                logger.info(f"Attente de {delay}s avant le prochain test...")
                time.sleep(delay)
        
        return results
