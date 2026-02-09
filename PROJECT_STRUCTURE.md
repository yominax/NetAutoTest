# Structure du Projet NetAutoTest

Ce document décrit la structure complète du projet NetAutoTest.

## Structure des répertoires

```
NetAutoTest/
├── .github/
│   └── workflows/
│       └── ci.yml                    # Workflow GitHub Actions pour CI/CD
├── config/
│   └── config.yaml                   # Configuration principale
├── docker/
│   ├── Dockerfile.containernet       # Dockerfile pour Containernet
│   ├── docker-compose.monitoring.yml # Compose pour Prometheus/Grafana
│   ├── prometheus/
│   │   ├── prometheus.yml            # Configuration Prometheus
│   │   └── alerts.yml                # Règles d'alerte
│   └── grafana/
│       ├── datasources/
│       │   └── prometheus.yml        # Source de données Grafana
│       └── dashboards/
│           ├── dashboard.yml         # Configuration dashboards
│           └── network-dashboard.json # Dashboard réseau
├── docs/
│   ├── conf.py                       # Configuration Sphinx
│   ├── index.rst                     # Page d'accueil documentation
│   ├── installation.rst              # Guide d'installation
│   ├── architecture.rst              # Architecture du projet
│   ├── usage.rst                     # Guide d'utilisation
│   ├── api.rst                       # Référence API
│   ├── configuration.rst             # Guide de configuration
│   ├── examples.rst                   # Exemples de code
│   ├── contributing.rst             # Guide de contribution
│   ├── Makefile                      # Makefile pour Sphinx
│   └── make.bat                      # Makefile Windows
├── logs/                             # Répertoire des logs
├── reports/                          # Répertoire des rapports générés
├── src/
│   ├── __init__.py
│   ├── simulator/                    # Module de simulation réseau
│   │   ├── __init__.py
│   │   ├── topology.py               # Définition des topologies
│   │   └── network_simulator.py       # Gestionnaire de simulation
│   ├── tests/                        # Module de tests de performance
│   │   ├── __init__.py
│   │   ├── run_test_campaign.py      # Orchestrateur de campagnes
│   │   ├── iperf_wrapper.py          # Wrapper iperf3
│   │   └── latency_test.py           # Tests de latence
│   ├── monitoring/                   # Module de monitoring
│   │   ├── __init__.py
│   │   ├── probe.py                  # Sondes Prometheus
│   │   └── report_generator.py       # Générateur de rapports
│   └── utils/                        # Utilitaires
│       ├── __init__.py
│       └── logger.py                 # Configuration des logs
├── tests/
│   ├── __init__.py
│   ├── unit/                         # Tests unitaires
│   │   ├── __init__.py
│   │   ├── test_topology.py
│   │   └── test_iperf_wrapper.py
│   └── integration/                  # Tests d'intégration
│       ├── __init__.py
│       └── test_campaign.py
├── .gitignore                        # Fichiers ignorés par Git
├── LICENSE                           # Licence MIT
├── Makefile                          # Makefile principal
├── README.md                         # Documentation principale
├── requirements.txt                  # Dépendances Python
├── setup.py                          # Configuration package Python
├── pytest.ini                        # Configuration pytest
└── topology.py                       # Script d'exemple de topologie
```

## Fichiers clés

### Configuration
- `config/config.yaml` : Configuration principale (réseau, tests, monitoring)
- `pytest.ini` : Configuration des tests
- `.github/workflows/ci.yml` : Pipeline CI/CD

### Code source principal
- `src/simulator/` : Simulation réseau avec Containernet
- `src/tests/` : Tests de performance (iperf3, latence)
- `src/monitoring/` : Monitoring Prometheus et génération de rapports

### Documentation
- `README.md` : Documentation principale avec badges et exemples
- `docs/` : Documentation Sphinx complète avec autodoc

### Docker
- `docker/Dockerfile.containernet` : Image Docker pour Containernet
- `docker/docker-compose.monitoring.yml` : Stack Prometheus/Grafana

## Commandes principales

Voir le `Makefile` pour toutes les commandes disponibles :

- `make install` : Installation des dépendances
- `make test` : Lancer une campagne de tests
- `make sim` : Démarrer la simulation réseau
- `make monitor` : Démarrer Prometheus/Grafana
- `make docs` : Générer la documentation
- `make clean` : Nettoyer les fichiers générés

## Prochaines étapes

1. Installer les dépendances : `make install`
2. Lire le README.md pour les instructions détaillées
3. Configurer `config/config.yaml` selon vos besoins
4. Lancer une première campagne : `make test`
