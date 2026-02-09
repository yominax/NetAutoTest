.PHONY: help install install-containernet test test-all sim monitor docs clean

help:
	@echo "NetAutoTest - Makefile Commands"
	@echo "================================"
	@echo "install              - Installer toutes les dépendances"
	@echo "install-containernet - Installer Containernet"
	@echo "test                 - Lancer une campagne de tests"
	@echo "test-all             - Lancer tous les tests (unitaires + intégration)"
	@echo "sim                  - Démarrer la simulation réseau"
	@echo "sim-stop             - Arrêter la simulation réseau"
	@echo "monitor              - Démarrer le monitoring (Prometheus + Grafana)"
	@echo "monitor-stop         - Arrêter le monitoring"
	@echo "docs                 - Générer la documentation Sphinx"
	@echo "docs-serve           - Servir la documentation localement"
	@echo "clean                - Nettoyer les fichiers générés"
	@echo "lint                 - Vérifier le code avec flake8"
	@echo "format               - Formater le code avec black"

install:
	pip install -r requirements.txt
	@echo "✅ Dépendances installées"

install-containernet:
	@echo "📦 Installation de Containernet..."
	sudo apt-get update
	sudo apt-get install -y \
		apt-transport-https \
		ca-certificates \
		curl \
		gnupg \
		lsb-release
	sudo apt-get install -y \
		build-essential \
		git \
		iperf3 \
		iproute2 \
		net-tools \
		openvswitch-switch \
		openvswitch-common \
		python3-dev \
		python3-pip \
		socat \
		tcpdump \
		wireless-tools
	sudo pip3 install -U cffi
	sudo pip3 install -U git+https://github.com/containernet/containernet.git
	@echo "✅ Containernet installé"

test:
	python src/tests/run_test_campaign.py --config config/config.yaml

test-all:
	pytest tests/unit/ tests/integration/ -v --cov=src --cov-report=html

sim:
	python src/simulator/network_simulator.py start

sim-stop:
	python src/simulator/network_simulator.py stop

monitor:
	docker-compose -f docker/docker-compose.monitoring.yml up -d
	@echo "✅ Monitoring démarré"
	@echo "📊 Prometheus: http://localhost:9090"
	@echo "📈 Grafana: http://localhost:3000 (admin/admin)"

monitor-stop:
	docker-compose -f docker/docker-compose.monitoring.yml down

docs:
	cd docs && make html
	@echo "✅ Documentation générée dans docs/_build/html/"

docs-serve:
	cd docs/_build/html && python3 -m http.server 8000
	@echo "📚 Documentation disponible sur http://localhost:8000"

clean:
	rm -rf docs/_build/
	rm -rf reports/*
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	@echo "✅ Nettoyage terminé"

lint:
	flake8 src/ tests/ --max-line-length=120 --exclude=__pycache__

format:
	black src/ tests/ --line-length=120
