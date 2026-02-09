"""
Sonde de monitoring réseau en temps réel.

Cette sonde collecte des métriques réseau et système et les expose
via Prometheus pour le monitoring en temps réel.
"""

import time
import threading
import socket
import json
from typing import Dict, Optional
from prometheus_client import start_http_server, Gauge, Counter, Histogram
import psutil
from loguru import logger


class NetworkProbe:
    """
    Sonde de monitoring qui collecte et expose des métriques.
    
    Cette classe déploie une sonde légère dans chaque conteneur Docker
    pour mesurer en continu :
    - Latence des échanges
    - Robustesse (perte de paquets, reconnexions)
    - Métriques système (CPU, mémoire, réseau)
    """
    
    def __init__(self, hostname: str, port: int = 8080):
        """
        Initialise la sonde de monitoring.
        
        Args:
            hostname: Nom de l'hôte pour identifier la sonde
            port: Port d'exposition des métriques Prometheus
        """
        self.hostname = hostname
        self.port = port
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        # Métriques Prometheus
        self.latency_gauge = Gauge(
            "network_latency_ms",
            "Latence réseau en millisecondes",
            ["hostname", "target"]
        )
        
        self.packet_loss_gauge = Gauge(
            "network_packet_loss_percent",
            "Perte de paquets en pourcentage",
            ["hostname"]
        )
        
        self.throughput_gauge = Gauge(
            "network_throughput_mbps",
            "Débit réseau en Mbps",
            ["hostname", "direction"]
        )
        
        self.jitter_gauge = Gauge(
            "network_jitter_ms",
            "Jitter réseau en millisecondes",
            ["hostname"]
        )
        
        self.cpu_usage_gauge = Gauge(
            "system_cpu_usage_percent",
            "Utilisation CPU en pourcentage",
            ["hostname"]
        )
        
        self.memory_usage_gauge = Gauge(
            "system_memory_usage_percent",
            "Utilisation mémoire en pourcentage",
            ["hostname"]
        )
        
        self.network_io_counter = Counter(
            "network_bytes_total",
            "Total d'octets réseau",
            ["hostname", "direction"]
        )
        
        self.reconnection_counter = Counter(
            "network_reconnections_total",
            "Nombre total de reconnexions",
            ["hostname"]
        )
        
        # Données internes
        self.last_packet_time = {}
        self.packet_times = []
        self.latency_samples = []
        self.test_targets = []
    
    def start(self):
        """Démarre la sonde et le serveur HTTP Prometheus."""
        if self.running:
            logger.warning("La sonde est déjà démarrée")
            return
        
        self.running = True
        
        # Démarrer le serveur Prometheus
        start_http_server(self.port)
        logger.info(f"Sonde démarrée sur le port {self.port} pour {self.hostname}")
        
        # Démarrer le thread de collecte
        self.thread = threading.Thread(target=self._collect_metrics_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Arrête la sonde."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info(f"Sonde arrêtée pour {self.hostname}")
    
    def _collect_metrics_loop(self):
        """Boucle principale de collecte des métriques."""
        while self.running:
            try:
                # Collecter les métriques système
                self._collect_system_metrics()
                
                # Collecter les métriques réseau
                self._collect_network_metrics()
                
                # Attendre avant la prochaine collecte
                time.sleep(5)  # Intervalle de 5 secondes
            
            except Exception as e:
                logger.error(f"Erreur lors de la collecte des métriques: {e}")
                time.sleep(5)
    
    def _collect_system_metrics(self):
        """Collecte les métriques système (CPU, mémoire)."""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_usage_gauge.labels(hostname=self.hostname).set(cpu_percent)
            
            # Mémoire
            memory = psutil.virtual_memory()
            self.memory_usage_gauge.labels(hostname=self.hostname).set(memory.percent)
        
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des métriques système: {e}")
    
    def _collect_network_metrics(self):
        """Collecte les métriques réseau."""
        try:
            # Statistiques réseau
            net_io = psutil.net_io_counters()
            
            # Mettre à jour les compteurs
            self.network_io_counter.labels(
                hostname=self.hostname,
                direction="sent"
            )._value._value = net_io.bytes_sent
            
            self.network_io_counter.labels(
                hostname=self.hostname,
                direction="received"
            )._value._value = net_io.bytes_recv
            
            # Calculer le débit (approximatif)
            # Note: Pour une mesure précise, il faudrait comparer avec les valeurs précédentes
            # Ici on utilise une approximation basée sur les statistiques système
            
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des métriques réseau: {e}")
    
    def record_latency(self, target: str, latency_ms: float):
        """
        Enregistre une mesure de latence.
        
        Args:
            target: Cible de la mesure
            latency_ms: Latence en millisecondes
        """
        self.latency_gauge.labels(
            hostname=self.hostname,
            target=target
        ).set(latency_ms)
        
        # Garder un historique pour le calcul du jitter
        self.latency_samples.append((time.time(), latency_ms))
        if len(self.latency_samples) > 100:
            self.latency_samples.pop(0)
        
        # Calculer le jitter
        if len(self.latency_samples) > 1:
            jitter = abs(self.latency_samples[-1][1] - self.latency_samples[-2][1])
            self.jitter_gauge.labels(hostname=self.hostname).set(jitter)
    
    def record_packet_loss(self, loss_percent: float):
        """
        Enregistre une mesure de perte de paquets.
        
        Args:
            loss_percent: Perte de paquets en pourcentage
        """
        self.packet_loss_gauge.labels(hostname=self.hostname).set(loss_percent)
    
    def record_throughput(self, direction: str, throughput_mbps: float):
        """
        Enregistre une mesure de débit.
        
        Args:
            direction: "sent" ou "received"
            throughput_mbps: Débit en Mbps
        """
        self.throughput_gauge.labels(
            hostname=self.hostname,
            direction=direction
        ).set(throughput_mbps)
    
    def record_reconnection(self):
        """Enregistre une reconnexion."""
        self.reconnection_counter.labels(hostname=self.hostname).inc()
    
    def send_test_message(self, target_ip: str, target_port: int = 5004):
        """
        Envoie un message de test timestampé pour mesurer la latence.
        
        Args:
            target_ip: IP de la cible
            target_port: Port de la cible
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(1.0)
            
            # Créer un message avec timestamp
            message = {
                "hostname": self.hostname,
                "timestamp": time.time(),
                "type": "test_message"
            }
            
            data = json.dumps(message).encode()
            start_time = time.time()
            
            sock.sendto(data, (target_ip, target_port))
            
            # Essayer de recevoir une réponse
            try:
                response, _ = sock.recvfrom(1024)
                response_time = time.time()
                latency_ms = (response_time - start_time) * 1000
                
                self.record_latency(target_ip, latency_ms)
            
            except socket.timeout:
                logger.warning(f"Timeout lors de l'envoi du message de test à {target_ip}")
            
            sock.close()
        
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du message de test: {e}")


def main():
    """Point d'entrée pour exécuter la sonde en standalone."""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="Sonde de monitoring NetAutoTest")
    parser.add_argument(
        "--hostname",
        default=os.getenv("HOSTNAME", "unknown"),
        help="Nom de l'hôte"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port d'exposition des métriques"
    )
    
    args = parser.parse_args()
    
    probe = NetworkProbe(hostname=args.hostname, port=args.port)
    
    try:
        probe.start()
        logger.info("Sonde démarrée. Appuyez sur Ctrl+C pour arrêter.")
        
        # Boucle principale
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Arrêt de la sonde...")
        probe.stop()


if __name__ == "__main__":
    main()
