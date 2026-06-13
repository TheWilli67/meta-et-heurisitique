# Problème de Couverture Maximale sous Contrainte de Budget

> Master Cyber-défense et Sécurité de l'Information — Semestre 10  
> Université Polytechnique Hauts-de-France · INSA Hauts-de-France  
> Module : Complexité, Heuristiques & Métaheuristiques

**[Documentation complète (Sphinx)](https://thewilli67.github.io/meta-et-heurisitique/docs/index.html)**

---

## Contexte

Dans de nombreux scénarios de cyberdéfense, il est nécessaire de déployer un nombre limité de ressources de surveillance — sondes IDS, règles de filtrage, outils d'analyse de vulnérabilités — afin de couvrir un ensemble de cibles critiques (serveurs, ports, segments réseau). Le déploiement est contraint par un **budget** : il est impossible d'activer toutes les ressources disponibles.

Ce projet implémente et compare plusieurs algorithmes pour résoudre ce problème d'optimisation combinatoire, connu pour être **NP-difficile**.

---

## Formulation du problème

Étant donné :
- $U = \{u_1, \dots, u_m\}$ — un ensemble de **m cibles** à couvrir
- $S = \{S_1, \dots, S_n\}$ — un ensemble de **n ressources**, chacune couvrant un sous-ensemble de cibles
- $c_i > 0$ — le coût d'activation de la ressource $S_i$
- $B > 0$ — le budget total disponible

On cherche à sélectionner un sous-ensemble de ressources qui **maximise la couverture** tout en respectant le budget, avec un **objectif lexicographique** :

$$\max\left(\sum_{j=1}^{m} y_j,\ -\sum_{i=1}^{n} c_i x_i\right)$$

1. **Critère principal** : maximiser le nombre de cibles couvertes
2. **Critère secondaire** : à égalité, minimiser le coût total

---

## Algorithmes implémentés

### 1. Heuristique constructive gloutonne
Construction itérative d'une solution en sélectionnant à chaque étape la ressource admissible maximisant le ratio **couverture marginale / coût**. Utilise l'index inverse `covered_by` pour ne considérer que les ressources couvrant au moins une cible manquante.

### 2. Recherche locale
Amélioration par exploration de voisinage avec trois types de mouvements, dans l'ordre de priorité :
- **ADD** — ajouter la meilleure ressource admissible qui augmente la couverture
- **SWAP** — remplacer une ressource par une autre avec un meilleur delta (best-improve)
- **REMOVE** — retirer une ressource redondante (`coverage_loss == 0`) pour réduire le coût

### 3. Recuit simulé *(métaheuristique)*
Acceptation probabiliste de solutions dégradantes pour échapper aux optima locaux. La température décroît géométriquement de $T_{start} = 50$ à $T_{end} = 0.05$. Lancé **3 fois** avec des seeds fixes (42, 43, 44) pour garantir la reproductibilité. La moyenne et l'écart-type des runs sont affichés.

### 4. GRASP *(métaheuristique)*
*Greedy Randomized Adaptive Search Procedure* — 20 redémarrages combinant un glouton randomisé (sélection aléatoire dans les meilleurs $\alpha = 30\%$ candidats) et une recherche locale. Permet d'explorer des régions de l'espace de solutions inaccessibles au glouton déterministe.

Le pipeline complet s'exécute dans l'ordre : **Glouton → Recherche locale → Recuit simulé → GRASP**, et sauvegarde la meilleure solution toutes méthodes confondues.

---

## Structure du projet

```
.
├── solution.py              # Code source principal
├── instances/               # Fichiers d'instances (.txt)
│   ├── inst10_20_0.txt
│   ├── inst15_30_0.txt
│   └── ...
├── sol_instances/           # Solutions générées (créé automatiquement)
│   ├── sol_inst10_20_0.txt
│   └── ...
├── docs/                    # Documentation Sphinx (GitHub Pages)
│   ├── index.html           # Page d'accueil
│   ├── algorithmes.html
│   ├── api.html
│   ├── resultats.html
│   ├── utilisation.html
│   └── source/              # Sources RST
├── indel.html               # Redirection vers docs/index.html
├── benchmark_results.txt    # Résultats du dernier benchmark (écrasé à chaque run)
├── inst_test_budget.txt     # Instance de test : couverture totale impossible
└── README.md
```

---

## Installation

Aucune dépendance externe. Python 3.8+ suffit.

```bash
git clone https://github.com/OUTILS-AVANCES-POUR-LA-SECURITE
cd OUTILS-AVANCES-POUR-LA-SECURITE
python3 solution.py --help
```

---

## Utilisation

```bash
# Afficher l'aide
python3 solution.py -h

# Résoudre une instance → solution dans sol_instances/
python3 solution.py instances/inst30_50_1.txt

# Résoudre toutes les instances d'un dossier
python3 solution.py --all instances/

# Benchmark comparatif — affiche le tableau et écrit benchmark_results.txt
python3 solution.py --benchmark instances/

# GRASP uniquement sur une instance
python3 solution.py --grasp instances/inst90_50_2.txt

# Supprimer le dossier sol_instances/ et son contenu
python3 solution.py --reset-all
```

> **Note :** `--reset-all` supprime uniquement `sol_instances/`. Le fichier `benchmark_results.txt` est conservé.

### Format d'entrée

```
n m B
c_1 c_2 ... c_n
k_1 u_11 u_12 ...
k_2 u_21 u_22 ...
...
```

| Symbole | Signification |
|---------|--------------|
| `n` | Nombre de ressources |
| `m` | Nombre de cibles |
| `B` | Budget total |
| `c_i` | Coût de la ressource i |
| `k_i` | Nombre de cibles couvertes par i |
| `u_ij` | Indice (base 0) d'une cible couverte par i |

### Format de sortie

```
p
xi1 xi2 ... xip
```

Ligne 1 : nombre de ressources sélectionnées  
Ligne 2 : indices des ressources sélectionnées (séparés par espaces)  
Nom du fichier : `sol_instances/sol_<nom_instance>.txt`

### Fichier benchmark

Chaque exécution de `--benchmark` écrase `benchmark_results.txt` avec :
- Le tableau comparatif (Glouton / Recherche locale / Recuit simulé / GRASP)
- Les temps d'exécution détaillés par instance et par algorithme
- L'horodatage du run et les chemins utilisés

---

## Résultats expérimentaux

Résultats obtenus sur les 12 instances fournies — seeds fixes, écart-type = 0.00 sur toutes les instances.

| Instance | n | m | B | Glouton | Rech. locale | Rec. simulé | GRASP | **Meilleur** | Coût |
|---|---|---|---|---|---|---|---|---|---|
| inst10_20_0 | 10 | 20 | 80 | 20/20 | 20/20 | 20/20 | 20/20 | **20/20** | 62.0 |
| inst15_30_0 | 15 | 30 | 120 | 30/30 | 30/30 | 30/30 | 30/30 | **30/30** | 95.0 |
| inst20_30_1 | 20 | 30 | 150 | 30/30 | 30/30 | 30/30 | 30/30 | **30/30** | 106.0 |
| inst20_40_0 | 20 | 40 | 140 | 40/40 | 40/40 | 40/40 | 40/40 | **40/40** | 104.0 |
| inst30_50_1 | 30 | 50 | 150 | 50/50 | 50/50 | 50/50 | 50/50 | **50/50** | 92.0 |
| inst30_80_0 | 30 | 80 | 240 | 80/80 | 80/80 | 80/80 | 80/80 | **80/80** | 168.0 |
| inst50_30_2 | 50 | 30 | 200 | 29/30 | 29/30 | 29/30 | 29/30 | **29/30** | 175.0 |
| inst50_80_1 | 50 | 80 | 250 | 80/80 | 80/80 | 80/80 | 80/80 | **80/80** | 133.0 |
| inst60_90_1 | 60 | 90 | 250 | 90/90 | 90/90 | 90/90 | 90/90 | **90/90** | 99.0 |
| inst70_40_2 | 70 | 40 | 200 | 40/40 | 40/40 | 40/40 | 40/40 | **40/40** | 187.0 |
| inst90_50_2 | 90 | 50 | 270 | 49/50 | 50/50 | 50/50 | 50/50 | **50/50** | 244.0 |
| inst150_120_2 | 150 | 120 | 450 | 120/120 | 120/120 | 120/120 | 120/120 | **120/120** | 228.0 |

> **11/12 instances couvertes à 100%.** L'instance `inst50_30_2` atteint 29/30 (96.7%) — la cible manquante est mathématiquement inatteignable avec le budget disponible, quelle que soit la combinaison de ressources choisie.

> **Stabilité :** le recuit simulé est lancé 3 fois par instance (seeds 42, 43, 44). L'écart-type observé est 0.00 sur toutes les instances, ce qui confirme la stabilité des résultats.

> **Apport de GRASP :** sur les grandes instances, GRASP obtient systématiquement des coûts inférieurs au recuit simulé (ex. : 228 vs 252 sur `inst150_120_2`, 168 vs 175 sur `inst30_80_0`), au prix d'un temps de calcul comparable.

---

## Reproductibilité

Tous les algorithmes aléatoires utilisent des seeds fixes. Les résultats sont identiques à chaque exécution sur la même machine.

| Algorithme | Seed(s) utilisée(s) |
|---|---|
| Recuit simulé | 42, 43, 44 (3 runs indépendants) |
| GRASP | 42 |

```bash
# Résultats identiques à chaque appel
python3 solution.py --benchmark instances/
# → écrase benchmark_results.txt avec les nouveaux résultats
```

---

## Choix techniques notables

**Mises à jour incrémentales** — le compteur `cover_count[j]` est maintenu en temps réel. Ajouter ou retirer une ressource coûte O(k_i) au lieu de O(n×m), ce qui rend les algorithmes d'amélioration viables sur les grandes instances.

**Index inverse `covered_by`** — utilisé dans le glouton pour restreindre la recherche aux seules ressources couvrant au moins une cible manquante, via `covered_by[t]` sur chaque cible non couverte.

**Objectif lexicographique via tuple** — `evaluate()` retourne `(num_covered, -total_cost)`. Python compare les tuples élément par élément, ce qui implémente naturellement la priorité couverture > coût sans condition supplémentaire.

**Sauvegarde automatique du benchmark** — chaque appel à `--benchmark` écrase `benchmark_results.txt` avec le tableau et les temps d'exécution, facilitant la traçabilité des expérimentations pour le rapport.

---

## Auteurs

| Nom | Rôle |
|-----|------|
| William HERTRICH | Lead Developer — Architecture du code, implémentation des structures de données, heuristiques et métaheuristiques |
| Théo PLUVINAGE | Code Reviewer & Quality Engineer — Validation algorithmique, tests sur instances, analyse des performances et correction des bugs |
| Christophe GRILLET-AUBERT | Research & Documentation Lead — Rédaction du rapport, formalisation mathématique des algorithmes en pseudo-code et analyse expérimentale |
| Ludovic URBES | Presentation Architect & Slide Engineer — Conception du support de soutenance, mise en forme des résultats et synthèse orale |

---

*Master CDSI · UPHF / INSA HdF · 2025-2026*