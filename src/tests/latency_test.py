"""
Tests de latence personnalisés avec paquets timestampés.

Ce module implémente des tests de latence en envoyant des paquets
timestampés et en mesurant le RTT (Round-Trip Time).
"""

import time
import socket
import struct
import threading
from typing import List, Dict, Optional
from dataclasses import dataclass
from statistics import mean, stdev
from loguru import logger


@dataclass
class LatencyResult:
    """Résultat d'un test de latence."""
    rtt_min_ms: float
    rtt_max_ms: float
    rtt_mean_ms: float
    rtt_std_ms: float
    jitter_ms: float
    packet_loss_percent: float
    packets_sent: int
    packets_received: int
    rtt_samples: List[float]


class LatencyTest:
    """
    Classe pour mesurer la latence réseau entre deux hôtes.
    
    Utilise des paquets timestampés pour mesurer précisément
    le RTT et calculer le jitter.
    """
    
    def __init__(self, server_host, client_host, port: int = 5003):
        """
        Initialise un test de latence.
        
        Args:
            server_host: Hôte serveur (objet Mininet host)
            client_host: Hôte client (objet Mininet host)
            port: Port à utiliser pour le test
        """
        self.server_host = server_host
        self.client_host = client_host
        self.port = port
        self.server_socket: Optional[socket.socket] = None
        self.server_thread: Optional[threading.Thread] = None
        self.running = False
        self.received_timestamps: List[float] = []
    
    def start_server(self):
        """Démarre le serveur d'écho pour les tests de latence."""
        if self.server_socket is not None:
            logger.warning("Le serveur de latence est déjà démarré")
            return
        
        self.running = True
        self.received_timestamps = []
        
        def server_loop():
            """Boucle serveur qui renvoie les paquets avec timestamp."""
            try:
                # Créer un socket UDP
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.bind(("0.0.0.0", self.port))
                sock.settimeout(1.0)
                self.server_socket = sock
                
                logger.info(f"Serveur de latence démarré sur le port {self.port}")
                
                while self.running:
                    try:
                        data, addr = sock.recvfrom(1024)
                        if len(data) >= 8:  # Au moins un timestamp (8 bytes)
                            # Extraire le timestamp client
                            client_timestamp = struct.unpack("d", data[:8])[0]
                            
                            # Créer la réponse avec timestamp serveur
                            server_timestamp = time.time()
                            response = struct.pack("dd", client_timestamp, server_timestamp)
                            
                            sock.sendto(response, addr)
                            self.received_timestamps.append(server_timestamp)
                    except socket.timeout:
                        continue
                    except Exception as e:
                        if self.running:
                            logger.error(f"Erreur serveur: {e}")
                        break
                
                sock.close()
                logger.info("Serveur de latence arrêté")
            
            except Exception as e:
                logger.error(f"Erreur lors du démarrage du serveur: {e}")
        
        self.server_thread = threading.Thread(target=server_loop, daemon=True)
        self.server_thread.start()
        time.sleep(0.5)  # Attendre que le serveur démarre
    
    def stop_server(self):
        """Arrête le serveur de latence."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        if self.server_thread:
            self.server_thread.join(timeout=2)
        self.server_socket = None
        logger.info("Serveur de latence arrêté")
    
    def run_test(
        self,
        duration: int = 60,
        interval: float = 1.0,
        packet_size: int = 64
    ) -> LatencyResult:
        """
        Exécute un test de latence.
        
        Args:
            duration: Durée du test en secondes
            interval: Intervalle entre les paquets en secondes
            packet_size: Taille des paquets en bytes
            
        Returns:
            Résultat du test
        """
        if self.server_socket is None:
            self.start_server()
        
        server_ip = self.server_host.IP()
        rtt_samples = []
        packets_sent = 0
        packets_received = 0
        
        # Créer le socket client
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.0)
        
        logger.info(f"Démarrage du test de latence ({duration}s, intervalle {interval}s)")
        
        start_time = time.time()
        end_time = start_time + duration
        
        try:
            while time.time() < end_time:
                # Envoyer un paquet avec timestamp
                client_timestamp = time.time()
                packet_data = struct.pack("d", client_timestamp) + b"x" * (packet_size - 8)
                
                try:
                    sock.sendto(packet_data, (server_ip, self.port))
                    packets_sent += 1
                    
                    # Recevoir la réponse
                    response, _ = sock.recvfrom(1024)
                    server_receive_time = time.time()
                    
                    if len(response) >= 16:  # Deux timestamps (16 bytes)
                        client_ts, server_ts = struct.unpack("dd", response[:16])
                        
                        # Calculer le RTT
                        rtt = (server_receive_time - client_ts) * 1000  # en ms
                        rtt_samples.append(rtt)
                        packets_received += 1
                
                except socket.timeout:
                    logger.warning("Timeout lors de la réception de la réponse")
                except Exception as e:
                    logger.error(f"Erreur lors de l'envoi/réception: {e}")
                
                # Attendre avant le prochain paquet
                time.sleep(interval)
        
        finally:
            sock.close()
        
        # Calculer les statistiques
        if not rtt_samples:
            logger.warning("Aucun échantillon de latence reçu")
            return LatencyResult(
                rtt_min_ms=0.0,
                rtt_max_ms=0.0,
                rtt_mean_ms=0.0,
                rtt_std_ms=0.0,
                jitter_ms=0.0,
                packet_loss_percent=100.0,
                packets_sent=packets_sent,
                packets_received=packets_received,
                rtt_samples=[]
            )
        
        rtt_min = min(rtt_samples)
        rtt_max = max(rtt_samples)
        rtt_mean = mean(rtt_samples)
        rtt_std = stdev(rtt_samples) if len(rtt_samples) > 1 else 0.0
        
        # Calculer le jitter (écart type des différences de RTT)
        if len(rtt_samples) > 1:
            rtt_diffs = [abs(rtt_samples[i] - rtt_samples[i-1]) 
                         for i in range(1, len(rtt_samples))]
            jitter = mean(rtt_diffs)
        else:
            jitter = 0.0
        
        packet_loss = ((packets_sent - packets_received) / packets_sent * 100) if packets_sent > 0 else 0.0
        
        logger.info(
            f"Test terminé: RTT moyen={rtt_mean:.2f}ms, "
            f"Perte={packet_loss:.2f}%, Jitter={jitter:.2f}ms"
        )
        
        return LatencyResult(
            rtt_min_ms=rtt_min,
            rtt_max_ms=rtt_max,
            rtt_mean_ms=rtt_mean,
            rtt_std_ms=rtt_std,
            jitter_ms=jitter,
            packet_loss_percent=packet_loss,
            packets_sent=packets_sent,
            packets_received=packets_received,
            rtt_samples=rtt_samples
        )
