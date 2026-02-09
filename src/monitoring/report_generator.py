"""
Générateur de rapports HTML et JSON pour les campagnes de tests.

Ce module génère des rapports visuels avec graphiques à partir
des résultats de tests.
"""

import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from loguru import logger

from ..tests.run_test_campaign import TestCampaignResult
from ..tests.iperf_wrapper import IperfResult
from ..tests.latency_test import LatencyResult


class ReportGenerator:
    """
    Générateur de rapports pour les campagnes de tests.
    
    Cette classe génère des rapports HTML avec graphiques à partir
    des résultats de tests de performance.
    """
    
    def __init__(self):
        """Initialise le générateur de rapports."""
        plt.style.use("seaborn-v0_8-darkgrid")
    
    def generate_html_report(self, result: TestCampaignResult, output_path: Path):
        """
        Génère un rapport HTML avec graphiques.
        
        Args:
            result: Résultat de la campagne de tests
            output_path: Chemin de sortie pour le fichier HTML
        """
        logger.info(f"Génération du rapport HTML: {output_path}")
        
        # Générer les graphiques
        graphs_dir = output_path.parent / "graphs"
        graphs_dir.mkdir(exist_ok=True)
        
        latency_chart = self._generate_latency_chart(result.latency_results, graphs_dir, output_path)
        throughput_chart = self._generate_throughput_chart(result.iperf_results, graphs_dir, output_path)
        
        # Générer le HTML
        html_content = self._generate_html_content(result, latency_chart, throughput_chart)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
    
    def _generate_latency_chart(self, results: List[LatencyResult], output_dir: Path, output_path: Path) -> Optional[str]:
        """Génère un graphique de latence."""
        if not results:
            return None
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle("Analyse de Latence", fontsize=16, fontweight="bold")
        
        # Graphique 1: RTT moyen, min, max
        ax1 = axes[0, 0]
        rtt_mean = [r.rtt_mean_ms for r in results]
        rtt_min = [r.rtt_min_ms for r in results]
        rtt_max = [r.rtt_max_ms for r in results]
        
        x = range(len(results))
        ax1.plot(x, rtt_mean, "o-", label="RTT Moyen", linewidth=2)
        ax1.fill_between(x, rtt_min, rtt_max, alpha=0.3, label="Min-Max")
        ax1.set_xlabel("Test")
        ax1.set_ylabel("Latence (ms)")
        ax1.set_title("RTT Moyen, Min, Max")
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Graphique 2: Jitter
        ax2 = axes[0, 1]
        jitter = [r.jitter_ms for r in results]
        ax2.bar(x, jitter, color="orange", alpha=0.7)
        ax2.set_xlabel("Test")
        ax2.set_ylabel("Jitter (ms)")
        ax2.set_title("Jitter")
        ax2.grid(True, alpha=0.3, axis="y")
        
        # Graphique 3: Perte de paquets
        ax3 = axes[1, 0]
        packet_loss = [r.packet_loss_percent for r in results]
        ax3.bar(x, packet_loss, color="red", alpha=0.7)
        ax3.set_xlabel("Test")
        ax3.set_ylabel("Perte de paquets (%)")
        ax3.set_title("Perte de Paquets")
        ax3.grid(True, alpha=0.3, axis="y")
        
        # Graphique 4: Distribution des RTT (pour le premier test)
        if results and results[0].rtt_samples:
            ax4 = axes[1, 1]
            ax4.hist(results[0].rtt_samples, bins=30, color="green", alpha=0.7, edgecolor="black")
            ax4.set_xlabel("RTT (ms)")
            ax4.set_ylabel("Fréquence")
            ax4.set_title("Distribution des RTT (Test 1)")
            ax4.grid(True, alpha=0.3, axis="y")
        
        plt.tight_layout()
        
        chart_path = output_dir / "latency_chart.png"
        plt.savefig(chart_path, dpi=150, bbox_inches="tight")
        plt.close()
        
        return str(chart_path.relative_to(output_path.parent))
    
    def _generate_throughput_chart(self, results: List[IperfResult], output_dir: Path, output_path: Path) -> Optional[str]:
        """Génère un graphique de débit."""
        if not results:
            return None
        
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle("Analyse de Débit", fontsize=16, fontweight="bold")
        
        # Séparer TCP et UDP
        tcp_results = [r for r in results if r.protocol == "tcp"]
        udp_results = [r for r in results if r.protocol == "udp"]
        
        # Graphique 1: Débit TCP
        if tcp_results:
            ax1 = axes[0]
            throughput = [r.throughput_mbps for r in tcp_results]
            retransmissions = [r.retransmissions or 0 for r in tcp_results]
            
            x = range(len(tcp_results))
            ax1_twin = ax1.twinx()
            
            bars = ax1.bar(x, throughput, color="blue", alpha=0.7, label="Débit")
            line = ax1_twin.plot(x, retransmissions, "ro-", label="Retransmissions", linewidth=2)
            
            ax1.set_xlabel("Test")
            ax1.set_ylabel("Débit (Mbps)", color="blue")
            ax1_twin.set_ylabel("Retransmissions", color="red")
            ax1.set_title("Débit TCP et Retransmissions")
            ax1.grid(True, alpha=0.3, axis="y")
            
            # Légende combinée
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax1_twin.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
        
        # Graphique 2: Débit UDP
        if udp_results:
            ax2 = axes[1]
            throughput = [r.throughput_mbps for r in udp_results]
            packet_loss = [r.packet_loss or 0 for r in udp_results]
            jitter = [r.jitter_ms or 0 for r in udp_results]
            
            x = range(len(udp_results))
            ax2_twin = ax2.twinx()
            
            bars = ax2.bar(x, throughput, color="green", alpha=0.7, label="Débit")
            line1 = ax2_twin.plot(x, packet_loss, "ro-", label="Perte (%)", linewidth=2)
            line2 = ax2_twin.plot(x, jitter, "mo-", label="Jitter (ms)", linewidth=2)
            
            ax2.set_xlabel("Test")
            ax2.set_ylabel("Débit (Mbps)", color="green")
            ax2_twin.set_ylabel("Perte / Jitter", color="red")
            ax2.set_title("Débit UDP, Perte et Jitter")
            ax2.grid(True, alpha=0.3, axis="y")
            
            # Légende combinée
            lines1, labels1 = ax2.get_legend_handles_labels()
            lines2, labels2 = ax2_twin.get_legend_handles_labels()
            ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
        
        plt.tight_layout()
        
        chart_path = output_dir / "throughput_chart.png"
        plt.savefig(chart_path, dpi=150, bbox_inches="tight")
        plt.close()
        
        return str(chart_path.relative_to(output_path.parent))
    
    def _generate_html_content(
        self,
        result: TestCampaignResult,
        latency_chart: Optional[str],
        throughput_chart: Optional[str]
    ) -> str:
        """Génère le contenu HTML du rapport."""
        status_icon = "✅" if result.passed else "❌"
        status_color = "#28a745" if result.passed else "#dc3545"
        
        html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport de Campagne - {result.campaign_id}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid {status_color};
            padding-bottom: 10px;
        }}
        .status {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 4px;
            background-color: {status_color};
            color: white;
            font-weight: bold;
            margin: 10px 0;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            border-left: 4px solid #007bff;
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
        }}
        .summary-card .value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #007bff;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .chart {{
            margin: 30px 0;
            text-align: center;
        }}
        .chart img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .errors {{
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 4px;
            padding: 15px;
            margin: 20px 0;
        }}
        .errors h3 {{
            color: #721c24;
            margin-top: 0;
        }}
        .errors ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .errors li {{
            color: #721c24;
            margin: 5px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{status_icon} Rapport de Campagne de Tests</h1>
        <div class="status">{'RÉUSSI' if result.passed else 'ÉCHOUÉ'}</div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>Campagne ID</h3>
                <div class="value">{result.campaign_id}</div>
            </div>
            <div class="summary-card">
                <h3>Durée</h3>
                <div class="value">{result.duration_seconds:.2f}s</div>
            </div>
            <div class="summary-card">
                <h3>Tests iperf3</h3>
                <div class="value">{len(result.iperf_results)}</div>
            </div>
            <div class="summary-card">
                <h3>Tests de latence</h3>
                <div class="value">{len(result.latency_results)}</div>
            </div>
        </div>
        
        <h2>Informations Générales</h2>
        <table>
            <tr>
                <th>Propriété</th>
                <th>Valeur</th>
            </tr>
            <tr>
                <td>Date de début</td>
                <td>{result.start_time}</td>
            </tr>
            <tr>
                <td>Date de fin</td>
                <td>{result.end_time}</td>
            </tr>
            <tr>
                <td>Durée totale</td>
                <td>{result.duration_seconds:.2f} secondes</td>
            </tr>
        </table>
"""
        
        if result.errors:
            html += """
        <div class="errors">
            <h3>Erreurs et Avertissements</h3>
            <ul>
"""
            for error in result.errors:
                html += f"                <li>{error}</li>\n"
            html += """
            </ul>
        </div>
"""
        
        if latency_chart:
            html += f"""
        <div class="chart">
            <h2>Analyse de Latence</h2>
            <img src="{latency_chart}" alt="Graphique de latence">
        </div>
"""
        
        if throughput_chart:
            html += f"""
        <div class="chart">
            <h2>Analyse de Débit</h2>
            <img src="{throughput_chart}" alt="Graphique de débit">
        </div>
"""
        
        if result.iperf_results:
            html += """
        <h2>Résultats iperf3</h2>
        <table>
            <tr>
                <th>Protocole</th>
                <th>Durée (s)</th>
                <th>Débit (Mbps)</th>
                <th>Retransmissions</th>
                <th>Perte (%)</th>
                <th>Jitter (ms)</th>
            </tr>
"""
            for r in result.iperf_results:
                html += f"""
            <tr>
                <td>{r.protocol.upper()}</td>
                <td>{r.duration}</td>
                <td>{r.throughput_mbps:.2f}</td>
                <td>{r.retransmissions or 'N/A'}</td>
                <td>{r.packet_loss or 'N/A'}</td>
                <td>{r.jitter_ms or 'N/A'}</td>
            </tr>
"""
            html += """
        </table>
"""
        
        if result.latency_results:
            html += """
        <h2>Résultats de Latence</h2>
        <table>
            <tr>
                <th>RTT Min (ms)</th>
                <th>RTT Max (ms)</th>
                <th>RTT Moyen (ms)</th>
                <th>Écart-type (ms)</th>
                <th>Jitter (ms)</th>
                <th>Perte (%)</th>
                <th>Paquets envoyés</th>
                <th>Paquets reçus</th>
            </tr>
"""
            for r in result.latency_results:
                html += f"""
            <tr>
                <td>{r.rtt_min_ms:.2f}</td>
                <td>{r.rtt_max_ms:.2f}</td>
                <td>{r.rtt_mean_ms:.2f}</td>
                <td>{r.rtt_std_ms:.2f}</td>
                <td>{r.jitter_ms:.2f}</td>
                <td>{r.packet_loss_percent:.2f}</td>
                <td>{r.packets_sent}</td>
                <td>{r.packets_received}</td>
            </tr>
"""
            html += """
        </table>
"""
        
        html += """
        <h2>Seuils Configurés</h2>
        <table>
            <tr>
                <th>Seuil</th>
                <th>Valeur</th>
            </tr>
"""
        for key, value in result.thresholds.items():
            html += f"""
            <tr>
                <td>{key}</td>
                <td>{value}</td>
            </tr>
"""
        
        html += """
        </table>
    </div>
</body>
</html>
"""
        
        return html
