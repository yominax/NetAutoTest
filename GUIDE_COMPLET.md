# Guide complet — NetAutoTest (tout comprendre et comment run)

Ce document explique **tout** le projet en langage simple, puis comment lancer chaque partie.

---

## En une phrase, c’est quoi ?

**NetAutoTest** = un outil qui **simule un petit réseau** (plusieurs machines virtuelles reliées par un switch), qui **lance des tests de débit et de latence** sur ce réseau, et qui peut **afficher des graphiques** (Prometheus/Grafana) et des **rapports** (HTML/JSON).

---

## Le projet en 3 blocs

```
┌─────────────────────────────────────────────────────────────────┐
│  1. SIMULATION RÉSEAU (Containernet)                             │
│  → Crée un faux réseau : 1 switch + plusieurs "hôtes" (conteneurs)│
│  → Tu peux choisir : étoile, ligne, maillé + latence, perte, etc. │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. TESTS DE PERFORMANCE                                         │
│  → Entre les hôtes : tests iperf3 (débit TCP/UDP) + tests latence │
│  → Résultats comparés à des seuils (ex. latence max 50 ms)        │
│  → Génération de rapports (JSON + HTML avec graphiques)           │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. MONITORING (optionnel)                                       │
│  → Prometheus + Grafana dans Docker                              │
│  → Tableaux de bord pour voir les métriques en temps réel         │
└─────────────────────────────────────────────────────────────────┘
```

- **Bloc 1** : nécessaire pour avoir un “réseau” où lancer les tests.
- **Bloc 2** : c’est le cœur du projet (campagne de tests).
- **Bloc 3** : optionnel, pour regarder les métriques dans un navigateur.

---

## Structure du projet (à quoi sert chaque chose)

| Dossier / Fichier | Rôle |
|-------------------|------|
| **config/config.yaml** | Toute la config : type de réseau, nombre d’hôtes, latence, perte, durée des tests, seuils, rapports, etc. |
| **src/simulator/** | Démarre/arrête le réseau simulé (Containernet) et définit la topologie (star, line, mesh). |
| **src/tests/** | Lance les tests iperf3 et latence, compare aux seuils, génère les rapports. |
| **src/monitoring/** | Sondes et génération de rapports (HTML, etc.). |
| **docker/** | Fichiers pour lancer Prometheus et Grafana avec `docker-compose`. |
| **reports/** | Les rapports générés (JSON, HTML) vont ici. |
| **logs/** | Fichiers de log du simulateur et des tests. |
| **tests/** | Tests unitaires et d’intégration (pytest), pas la “campagne” métier. |
| **docs/** | Documentation Sphinx (générée avec `make docs`). |
| **Makefile** | Raccourcis pour les commandes (install, sim, test, monitor, etc.). |

---

## Fichier de config en bref (config/config.yaml)

- **network** : topologie (star / line / mesh), nombre d’hôtes, latence (ms), perte de paquets (%), bande passante (Mbps).
- **tests** : durée des tests, nombre d’itérations, protocoles (tcp, udp), **seuils** (latence max, perte max, débit min) pour dire si la campagne “réussit” ou “échoue”.
- **reporting** : formats (json, html), dossier de sortie (reports/), style des graphiques.
- **monitoring** : réglages pour Prometheus/Grafana (ports, intervalles, alertes).

Tu peux tout faire tourner avec les valeurs par défaut ; modifier ce fichier change le comportement du réseau et des tests.

---

## Commandes principales (Makefile) — ce que fait chaque chose

| Commande | Ce qu’elle fait |
|----------|------------------|
| **make install** | `pip install -r requirements.txt` → installe les paquets Python du projet. |
| **make install-containernet** | Installe Containernet (et deps système) pour la simulation. À faire une fois sur la machine. |
| **make sim** | Démarre la **simulation réseau** (switch + hôtes). Le processus reste en avant-plan ; pour arrêter : Ctrl+C ou autre terminal avec `make sim-stop`. |
| **make sim-stop** | Arrête la simulation réseau. |
| **make test** | Lance une **campagne de tests** complète : démarre le réseau → lance iperf3 + latence → vérifie les seuils → génère les rapports → arrête le réseau. Tout en une commande. |
| **make monitor** | Démarre **Prometheus + Grafana** en Docker (ports 9090 et 3000). |
| **make monitor-stop** | Arrête les conteneurs Prometheus/Grafana. |
| **make test-all** | Lance les **tests unitaires + intégration** (pytest), pas la campagne métier. |
| **make docs** | Génère la doc Sphinx dans `docs/_build/html/`. |
| **make clean** | Supprime rapports, cache, doc générée, etc. |

---

## Comment run — scénarios pas à pas

### Prérequis (une fois)

- Linux (Ubuntu recommandé), Python 3.11+, Docker si tu veux le monitoring.
- Dépendances Python :  
  `pip install -r requirements.txt`  
  (ou `make install`).
- Pour la simulation :  
  `make install-containernet`  
  (une fois, avec sudo).

Ensuite, **toujours depuis la racine du projet** (où se trouve le Makefile), et de préférence avec le **venv activé** (`source venv/bin/activate`).

---

### Scénario 1 : Lancer uniquement la simulation réseau

Tu veux juste un “réseau” qui tourne (pour tester à la main, ou pour autre outil).

1. Démarrer la simulation :
   ```bash
   make sim
   ```
   Ou :
   ```bash
   python src/simulator/network_simulator.py start
   ```
   Le réseau reste actif dans ce terminal.

2. (Optionnel) Lancer en mode interactif (CLI Mininet) :
   ```bash
   python src/simulator/network_simulator.py start --interactive
   ```
   Tu peux taper des commandes (ping, etc.) puis `exit` pour quitter.

3. Arrêter la simulation (dans un autre terminal, depuis le même dossier) :
   ```bash
   make sim-stop
   ```
   Ou : `python src/simulator/network_simulator.py stop`

---

### Scénario 2 : Lancer une campagne de tests (le cœur du projet)

Tu veux que le projet : démarre le réseau → lance les tests → génère les rapports → arrête le réseau.

Une seule commande :

```bash
make test
```

Équivalent manuel :

```bash
python src/tests/run_test_campaign.py --config config/config.yaml
```

- Le script démarre le réseau (selon `config/config.yaml`).
- Lance les tests iperf3 (TCP/UDP) et les tests de latence.
- Compare les résultats aux seuils (latence max, perte max, débit min).
- Génère les rapports dans **reports/** (JSON + HTML).
- Affiche un résumé (réussi / échoué) et quitte avec un code de sortie 0 (succès) ou 1 (échec), pratique pour la CI/CD.

Tu n’as pas besoin de lancer `make sim` avant : la campagne démarre et arrête le réseau elle-même.

---

### Scénario 3 : Monitoring (Prometheus + Grafana)

Pour avoir des graphiques en temps réel (métriques, tableaux de bord).

1. Démarrer les services :
   ```bash
   make monitor
   ```
   (Docker lance Prometheus et Grafana.)

2. Ouvrir dans le navigateur :
   - Prometheus : http://localhost:9090  
   - Grafana : http://localhost:3000 (login : admin / admin)

3. Arrêter :
   ```bash
   make monitor-stop
   ```

Les sondes du projet (dans `src/monitoring/`) peuvent exposer des métriques ; Prometheus les scrape selon la config dans `docker/prometheus/`.

---

### Scénario 4 : Tout enchaîner (simu + tests + monitoring)

1. Install (une fois) :  
   `make install` puis `make install-containernet`
2. Lancer le monitoring (optionnel) :  
   `make monitor`  
   Puis ouvrir Grafana (http://localhost:3000).
3. Lancer une campagne :  
   `make test`  
   (le réseau est démarré/arrêté par la campagne.)
4. Regarder les rapports dans **reports/** (fichiers HTML/JSON avec la date/heure dans le nom).
5. Arrêter le monitoring :  
   `make monitor-stop`

---

## Résumé “quoi run quand”

- **Comprendre le projet** : lire ce guide + `config/config.yaml`.
- **Installer** : `pip install -r requirements.txt` puis `make install-containernet` (une fois).
- **Simulation seule** : `make sim` → pour arrêter : `make sim-stop`.
- **Tests complets (recommandé)** : `make test` → rapports dans `reports/`.
- **Graphiques temps réel** : `make monitor` → Grafana http://localhost:3000.
- **Tests dev (pytest)** : `make test-all`.

Tout se fait depuis la **racine du projet** (où est le Makefile), avec le **venv activé** si tu en utilises un.

---

## En cas de souci

- **make sim** ou **make test** échoue (Containernet / mininet) : vérifier que `make install-containernet` a bien été fait et que Docker tourne si tu utilises des hôtes Docker.
- **make test** ne génère pas de rapports : vérifier que le dossier `reports/` existe (il est normalement créé automatiquement) et regarder les logs dans `logs/`.
- **make monitor** ne démarre pas : vérifier que Docker (et docker-compose) sont installés et que les ports 9090 et 3000 sont libres.

Pour plus de détails d’installation (Python, venv, erreurs pip), voir le **README.md** (section Installation et Dépannage).
