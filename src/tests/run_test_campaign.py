"""
Orchestrateur principal des campagnes de tests de performance.

Ce module coordonne l'exécution de plusieurs types de tests (iperf3, latence)
et génère des rapports consolidés.
"""

import yaml
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger
from dataclasses import dataclass, asdict

from ..simulator.network_simulator import NetworkSimulator
from .iperf_wrapper import IperfTest, IperfResult
from .latency_test import LatencyTest, LatencyResult
from ..monitoring.report_generator import ReportGenerator


@dataclass
class TestCampaignResult:
    """Résultat complet d'une campagne de tests."""
    campaign_id: str
    start_time: str
    end_time: str
    duration_seconds: float
    iperf_results: List[IperfResult]
    latency_results: List[LatencyResult]
    thresholds: Dict
    passed: bool
    errors: List[str]


class TestCampaign:
    """
    Classe principale pour orchestrer les campagnes de tests.
    
    Cette classe gère le cycle de vie complet d'une campagne :
    - Démarrage de la simulation réseau
    - Exécution des tests (iperf3, latence)
    - Validation des seuils
    - Génération des rapports
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialise une campagne de tests.
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config_path = config_path
        self.config: Dict = {}
        self.simulator: Optional[NetworkSimulator] = None
        self._load_config()
        
        # Configuration des logs
        logger.add(
            "logs/test_campaign.log",
            rotation="10 MB",
            retention="7 days",
            level=self.config.get("logging", {}).get("level", "INFO")
        )
    
    def _load_config(self):
        """Charge la configuration depuis le fichier YAML."""
        config_file = Path(self.config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Fichier de configuration non trouvé: {self.config_path}")
        
        with open(config_file, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
    
    def start_network(self):
        """Démarre la simulation réseau."""
        logger.info("Démarrage de la simulation réseau...")
        self.simulator = NetworkSimulator(config_path=self.config_path)
        self.simulator.start()
        time.sleep(3)  # Attendre que le réseau soit stable
        
        # Test de connectivité
        logger.info("Vérification de la connectivité...")
        self.simulator.ping_all()
    
    def stop_network(self):
        """Arrête la simulation réseau."""
        if self.simulator:
            logger.info("Arrêt de la simulation réseau...")
            self.simulator.stop()
            self.simulator = None
    
    def run_iperf_tests(self) -> List[IperfResult]:
        """
        Exécute les tests iperf3.
        
        Returns:
            Liste des résultats iperf3
        """
        if not self.simulator:
            raise RuntimeError("Le réseau n'est pas démarré")
        
        hosts = self.simulator.get_all_hosts()
        if len(hosts) < 2:
            raise RuntimeError("Au moins 2 hôtes sont nécessaires pour les tests")
        
        # Utiliser les deux premiers hôtes comme client/serveur
        server_host = hosts[0]
        client_host = hosts[1]
        
        test_config = self.config.get("tests", {})
        protocols = test_config.get("protocols", ["tcp"])
        duration = test_config.get("duration_seconds", 60)
        iterations = test_config.get("iterations", 5)
        delay = test_config.get("delay_between_iterations", 10)
        
        all_results = []
        
        for protocol in protocols:
            logger.info(f"Exécution des tests iperf3 ({protocol.upper()})...")
            
            iperf_test = IperfTest(
                server_host=server_host,
                client_host=client_host,
                port=test_config.get("ports", {}).get(protocol, 5001)
            )
            
            try:
                results = iperf_test.run_multiple_tests(
                    protocol=protocol,
                    duration=duration,
                    iterations=iterations,
                    delay=delay
                )
                all_results.extend(results)
            
            finally:
                iperf_test.stop_server()
        
        return all_results
    
    def run_latency_tests(self) -> List[LatencyResult]:
        """
        Exécute les tests de latence.
        
        Returns:
            Liste des résultats de latence
        """
        if not self.simulator:
            raise RuntimeError("Le réseau n'est pas démarré")
        
        hosts = self.simulator.get_all_hosts()
        if len(hosts) < 2:
            raise RuntimeError("Au moins 2 hôtes sont nécessaires pour les tests")
        
        server_host = hosts[0]
        client_host = hosts[1]
        
        test_config = self.config.get("tests", {})
        duration = test_config.get("duration_seconds", 60)
        
        logger.info("Exécution des tests de latence...")
        
        latency_test = LatencyTest(
            server_host=server_host,
            client_host=client_host,
            port=5003
        )
        
        try:
            result = latency_test.run_test(duration=duration, interval=1.0)
            return [result]
        
        finally:
            latency_test.stop_server()
    
    def validate_thresholds(
        self,
        iperf_results: List[IperfResult],
        latency_results: List[LatencyResult]
    ) -> tuple[bool, List[str]]:
        """
        Valide les résultats par rapport aux seuils configurés.
        
        Args:
            iperf_results: Résultats iperf3
            latency_results: Résultats de latence
            
        Returns:
            Tuple (passed, errors)
        """
        thresholds = self.config.get("tests", {}).get("thresholds", {})
        errors = []
        
        # Valider la latence
        if latency_results:
            max_latency = thresholds.get("max_latency_ms", 50)
            for result in latency_results:
                if result.rtt_mean_ms > max_latency:
                    errors.append(
                        f"Latence moyenne ({result.rtt_mean_ms:.2f}ms) "
                        f"dépasse le seuil ({max_latency}ms)"
                    )
                
                max_loss = thresholds.get("max_packet_loss_percent", 1.0)
                if result.packet_loss_percent > max_loss:
                    errors.append(
                        f"Perte de paquets ({result.packet_loss_percent:.2f}%) "
                        f"dépasse le seuil ({max_loss}%)"
                    )
        
        # Valider le débit
        if iperf_results:
            min_throughput = thresholds.get("min_throughput_mbps", 10)
            for result in iperf_results:
                if result.throughput_mbps < min_throughput:
                    errors.append(
                        f"Débit ({result.throughput_mbps:.2f}Mbps) "
                        f"inférieur au seuil ({min_throughput}Mbps)"
                    )
        
        passed = len(errors) == 0
        return passed, errors
    
    def run(self) -> TestCampaignResult:
        """
        Exécute une campagne complète de tests.
        
        Returns:
            Résultat de la campagne
        """
        campaign_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        start_time = datetime.now().isoformat()
        
        logger.info(f"Démarrage de la campagne de tests {campaign_id}")
        
        errors = []
        iperf_results = []
        latency_results = []
        
        try:
            # Démarrer le réseau
            self.start_network()
            
            # Exécuter les tests iperf3
            try:
                iperf_results = self.run_iperf_tests()
            except Exception as e:
                error_msg = f"Erreur lors des tests iperf3: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
            
            # Exécuter les tests de latence
            try:
                latency_results = self.run_latency_tests()
            except Exception as e:
                error_msg = f"Erreur lors des tests de latence: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
            
            # Valider les seuils
            passed, threshold_errors = self.validate_thresholds(iperf_results, latency_results)
            errors.extend(threshold_errors)
            
            if not passed:
                logger.warning("⚠️  La campagne a échoué les validations de seuils")
            else:
                logger.info("✅ La campagne a réussi toutes les validations")
        
        finally:
            # Arrêter le réseau
            self.stop_network()
        
        end_time = datetime.now().isoformat()
        duration = (datetime.fromisoformat(end_time) - datetime.fromisoformat(start_time)).total_seconds()
        
        result = TestCampaignResult(
            campaign_id=campaign_id,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            iperf_results=iperf_results,
            latency_results=latency_results,
            thresholds=self.config.get("tests", {}).get("thresholds", {}),
            passed=passed and len(errors) == 0,
            errors=errors
        )
        
        # Générer les rapports
        self._generate_reports(result)
        
        return result
    
    def _generate_reports(self, result: TestCampaignResult):
        """Génère les rapports de la campagne."""
        report_config = self.config.get("reporting", {})
        formats = report_config.get("formats", ["json", "html"])
        output_dir = Path(report_config.get("output_dir", "reports"))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        generator = ReportGenerator()
        
        for fmt in formats:
            if fmt == "json":
                json_path = output_dir / f"campaign_{result.campaign_id}.json"
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(asdict(result), f, indent=2, default=str)
                logger.info(f"Rapport JSON généré: {json_path}")
            
            elif fmt == "html":
                html_path = output_dir / f"campaign_{result.campaign_id}.html"
                generator.generate_html_report(result, html_path)
                logger.info(f"Rapport HTML généré: {html_path}")


def main():
    """Point d'entrée principal pour le script CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Campagne de tests de performance NetAutoTest")
    parser.add_argument(
        "--config",
        default="config/config.yaml",
        help="Chemin vers le fichier de configuration"
    )
    
    args = parser.parse_args()
    
    campaign = TestCampaign(config_path=args.config)
    result = campaign.run()
    
    # Afficher le résumé
    print("\n" + "="*60)
    print("RÉSUMÉ DE LA CAMPAGNE")
    print("="*60)
    print(f"Campagne ID: {result.campaign_id}")
    print(f"Durée: {result.duration_seconds:.2f}s")
    print(f"Statut: {'✅ RÉUSSI' if result.passed else '❌ ÉCHOUÉ'}")
    print(f"Tests iperf3: {len(result.iperf_results)}")
    print(f"Tests de latence: {len(result.latency_results)}")
    
    if result.errors:
        print("\nErreurs:")
        for error in result.errors:
            print(f"  - {error}")
    
    print("="*60)
    
    # Exit code pour CI/CD
    exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
