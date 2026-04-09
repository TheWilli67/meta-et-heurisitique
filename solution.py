"""
Problème de couverture maximale sous contrainte de budget
Master CDSI - Semestre 10

Auteurs : William HERTRICH - Théo PLUVINAGE - Christophe GRILLET-AUBERT - Ludovic URBES

Usage :
    python solution.py <fichier_instance>
    python solution.py --all <dossier>
    python solution.py --benchmark <dossier>
    python solution.py --grasp <fichier_instance>
    python solution.py --reset-all
    python solution.py -h|--help
"""

import sys
import os
import random
import math
import time
import glob


# ==============================================================================
# STRUCTURES DE DONNÉES
# ==============================================================================

class Problem:
    """
    Représente une instance du problème de couverture maximale.

    Attributs :
        n          : nombre de ressources
        m          : nombre de cibles
        B          : budget total
        costs      : liste des coûts (costs[i] = coût de la ressource i)
        covers     : liste de sets (covers[i] = ensemble des cibles couvertes par i)
        covered_by : liste de sets (covered_by[j] = ensemble des ressources qui couvrent j)
        instance_name : nom du fichier (sans extension), utilisé pour le fichier de sortie
    """

    def __init__(self, filename):
        self.filename = filename
        self.instance_name = os.path.splitext(os.path.basename(filename))[0]
        self._load(filename)

    def _load(self, filename):
        with open(filename, 'r') as f:
            # split() gère \r\n et les espaces multiples
            tokens = f.read().split()

        idx = 0
        self.n = int(tokens[idx]);   idx += 1
        self.m = int(tokens[idx]);   idx += 1
        self.B = float(tokens[idx]); idx += 1

        # Coûts des ressources
        self.costs = []
        for _ in range(self.n):
            self.costs.append(float(tokens[idx])); idx += 1

        # Couverture : covers[i] = set des indices de cibles couvertes par i
        self.covers = []
        # Index inverse : covered_by[j] = set des ressources qui couvrent j
        self.covered_by = [set() for _ in range(self.m)]

        for i in range(self.n):
            k = int(tokens[idx]); idx += 1
            targets = set()
            for _ in range(k):
                t = int(tokens[idx]); idx += 1
                targets.add(t)
            self.covers.append(targets)
            for t in targets:
                self.covered_by[t].add(i)

    def __repr__(self):
        return f"Problem(n={self.n}, m={self.m}, B={self.B})"


class Solution:
    """
    Représente une solution (sous-ensemble de ressources sélectionnées).

    Attributs :
        selected    : set des indices de ressources sélectionnées
        cover_count : cover_count[j] = nb de ressources sélectionnées qui couvrent j
                      (mis à jour de façon incrémentale — O(k_i) par opération)
        total_cost  : somme des coûts des ressources sélectionnées
        num_covered : nb de cibles j telles que cover_count[j] > 0
    """

    def __init__(self, problem):
        self.problem = problem
        self.selected    = set()
        self.cover_count = [0] * problem.m
        self.total_cost  = 0.0
        self.num_covered = 0

    def copy(self):
        s = Solution(self.problem)
        s.selected    = self.selected.copy()
        s.cover_count = self.cover_count.copy()
        s.total_cost  = self.total_cost
        s.num_covered = self.num_covered
        return s

    # --- Prédicats ---

    def is_feasible(self):
        """Vérifie que la contrainte budgétaire est respectée."""
        return self.total_cost <= self.problem.B + 1e-9

    def evaluate(self):
        """
        Retourne (num_covered, -total_cost) pour la maximisation lexicographique :
        1er critère : maximiser le nb de cibles couvertes
        2ème critère : à égalité, minimiser le coût (donc maximiser -coût)
        """
        return (self.num_covered, -self.total_cost)

    # --- Opérations élémentaires (mises à jour incrémentales) ---

    def add_resource(self, i):
        """Ajoute la ressource i. Ne vérifie pas la faisabilité (à faire en amont)."""
        if i in self.selected:
            return
        self.selected.add(i)
        self.total_cost += self.problem.costs[i]
        for t in self.problem.covers[i]:
            if self.cover_count[t] == 0:
                self.num_covered += 1
            self.cover_count[t] += 1

    def remove_resource(self, i):
        """Retire la ressource i."""
        if i not in self.selected:
            return
        self.selected.discard(i)
        self.total_cost -= self.problem.costs[i]
        for t in self.problem.covers[i]:
            self.cover_count[t] -= 1
            if self.cover_count[t] == 0:
                self.num_covered -= 1

    # --- Calculs utilitaires ---

    def marginal_coverage(self, i):
        """
        Nombre de nouvelles cibles couvertes si on ajoute la ressource i.
        On parcourt covers[i] et on compte les cibles dont cover_count == 0.
        Complexité : O(k_i)
        """
        return sum(1 for t in self.problem.covers[i] if self.cover_count[t] == 0)

    def coverage_loss(self, i):
        """
        Nombre de cibles perdues si on retire la ressource i.
        Une cible est perdue uniquement si cover_count[t] == 1
        (i est la seule ressource sélectionnée qui la couvre).
        Complexité : O(k_i)
        """
        return sum(1 for t in self.problem.covers[i] if self.cover_count[t] == 1)

    def uncovered_targets(self):
        """
        Retourne l'ensemble des indices de cibles pas encore couvertes.
        Utilisé dans le glouton via covered_by pour ne considérer
        que les ressources pertinentes (celles qui couvrent une cible manquante).
        Complexité : O(m)
        """
        return {t for t in range(self.problem.m) if self.cover_count[t] == 0}

    def can_add(self, i):
        """Vérifie qu'on peut ajouter i sans dépasser le budget."""
        return (i not in self.selected and
                self.total_cost + self.problem.costs[i] <= self.problem.B + 1e-9)

    # --- Sauvegarde ---

    def save(self, output_dir=None):
        """
        Sauvegarde la solution dans sol_<nom_instance>.txt
        Format :
            p
            xi1 xi2 ... xip
        """
        name = f"sol_{self.problem.instance_name}.txt"
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            path = os.path.join(output_dir, name)
        else:
            path = name

        sorted_sel = sorted(self.selected)
        with open(path, 'w') as f:
            f.write(f"{len(sorted_sel)}\n")
            f.write(" ".join(map(str, sorted_sel)) + "\n")
        return path

    def __repr__(self):
        return (f"Solution(covered={self.num_covered}/{self.problem.m}, "
                f"cost={self.total_cost:.2f}/{self.problem.B}, "
                f"feasible={self.is_feasible()})")


# ==============================================================================
# HEURISTIQUE CONSTRUCTIVE GLOUTONNE
# ==============================================================================

def greedy_constructive(problem, randomized=False, alpha=0.3):
    """
    Construit une solution initiale faisable par approche gloutonne.

    Critère de sélection : ratio couverture_marginale / coût.
    Si randomized=True (pour GRASP) : sélection dans les meilleurs alpha%.

    Utilisation de covered_by :
      À chaque étape, on identifie les cibles non couvertes, puis on remonte
      via covered_by[t] pour ne considérer QUE les ressources qui couvrent
      au moins une cible manquante. Cela évite de calculer marginal_coverage
      sur des ressources qui n'apporteraient rien.

    Complexité : O(n * k_max) par étape au lieu de O(n² * k_max).
    """
    sol        = Solution(problem)
    candidates = set(range(problem.n))

    while True:
        # --- Étape 1 : trouver les cibles non encore couvertes ---
        uncovered = sol.uncovered_targets()
        if not uncovered:
            break  # toutes les cibles sont couvertes

        # --- Étape 2 : via covered_by, trouver les ressources pertinentes ---
        # On ne calcule le score QUE pour les ressources qui couvrent
        # au moins une cible manquante (les autres ont marginal_coverage == 0)
        relevant = set()
        for t in uncovered:
            relevant |= problem.covered_by[t]  # union des ressources utiles
        relevant &= candidates                  # parmi celles pas encore ajoutées

        # --- Étape 3 : filtrer par budget et calculer les scores ---
        improving = []
        for i in relevant:
            if not sol.can_add(i):
                continue
            mc = sol.marginal_coverage(i)  # nb de nouvelles cibles couvertes
            if mc > 0:
                improving.append((i, mc, problem.costs[i]))

        if not improving:
            break

        # --- Étape 4 : trier par ratio couverture marginale / coût ---
        improving.sort(key=lambda x: x[1] / x[2], reverse=True)

        if randomized:
            # GRASP : choisir aléatoirement parmi les meilleurs alpha%
            limit  = max(1, int(len(improving) * alpha))
            chosen = random.choice(improving[:limit])
        else:
            chosen = improving[0]

        sol.add_resource(chosen[0])
        candidates.discard(chosen[0])

    return sol


# ==============================================================================
# RECHERCHE LOCALE
# ==============================================================================

def local_search(problem, initial_sol, max_iter=2000):
    """
    Améliore une solution par recherche locale.

    Voisinage exploré à chaque itération (dans l'ordre) :
      1. ADD   : ajouter une ressource qui augmente la couverture
      2. SWAP  : remplacer une ressource par une autre (meilleur delta)
      3. REMOVE: retirer une ressource redondante (coverage_loss == 0)
                 pour libérer du budget → permet des swaps futurs

    Stratégie : first-improve pour ADD/REMOVE, best-improve pour SWAP.
    S'arrête quand aucun mouvement n'améliore la solution.

    Complexité par itération : O(n²) pour SWAP.
    """
    sol = best_sol = initial_sol.copy()

    for _ in range(max_iter):
        improved = False

        # --- 1. ADD : ajouter la meilleure ressource admissible ---
        best_add = None
        best_add_score = (0, 0.0)  # (couverture marginale, -coût)

        for i in range(problem.n):
            if not sol.can_add(i):
                continue
            mc = sol.marginal_coverage(i)
            if mc == 0:
                continue
            score = (mc, -problem.costs[i])
            if score > best_add_score:
                best_add_score = score
                best_add = i

        if best_add is not None:
            sol.add_resource(best_add)
            if sol.evaluate() > best_sol.evaluate():
                best_sol = sol.copy()
            improved = True
            continue

        # --- 2. SWAP : remplacer une ressource par une autre ---
        best_swap      = None
        best_swap_gain = (0, 0.0)   # (delta_couverture, delta_coût_négatif)

        selected_list  = list(sol.selected)
        not_selected   = [i for i in range(problem.n) if i not in sol.selected]

        for r in selected_list:
            loss = sol.coverage_loss(r)
            for a in not_selected:
                new_cost = sol.total_cost - problem.costs[r] + problem.costs[a]
                if new_cost > problem.B + 1e-9:
                    continue
                # Gain net en couverture
                gain = sum(1 for t in problem.covers[a]
                           if sol.cover_count[t] == 0)
                # Perte nette : cibles de r uniquement couvertes par r
                # et pas dans covers[a]
                net_loss = sum(1 for t in problem.covers[r]
                               if sol.cover_count[t] == 1
                               and t not in problem.covers[a])
                delta_cov  = gain - net_loss
                delta_cost = problem.costs[r] - problem.costs[a]  # >0 si on économise

                swap_score = (delta_cov, delta_cost)
                if swap_score > best_swap_gain:
                    best_swap_gain = swap_score
                    best_swap = (r, a)

        if best_swap is not None and best_swap_gain > (0, 0.0):
            r, a = best_swap
            sol.remove_resource(r)
            sol.add_resource(a)
            if sol.evaluate() > best_sol.evaluate():
                best_sol = sol.copy()
            improved = True
            continue

        # --- 3. REMOVE : retirer une ressource redondante ---
        for r in list(sol.selected):
            if sol.coverage_loss(r) == 0:
                sol.remove_resource(r)
                # Améliore le critère secondaire (moins cher)
                if sol.evaluate() > best_sol.evaluate():
                    best_sol = sol.copy()
                improved = True
                break

        if not improved:
            break

    return best_sol


# ==============================================================================
# MÉTAHEURISTIQUE : RECUIT SIMULÉ
# ==============================================================================

def simulated_annealing(problem, initial_sol,
                        max_iter=15000,
                        T_start=50.0,
                        T_end=0.05,
                        seed=None):
    """
    Recuit simulé (Simulated Annealing).

    Principe :
      - Génère aléatoirement un voisin (add / remove / swap)
      - Accepte toujours une amélioration
      - Accepte une dégradation avec probabilité exp(Δ / T)
      - La température T décroît géométriquement de T_start à T_end

    Paramètres :
        max_iter : nombre d'itérations total
        T_start  : température initiale (contrôle l'exploration initiale)
        T_end    : température finale (quasi aucune acceptation dégradante)
        seed     : graine pour reproductibilité

    Complexité : O(max_iter * k_max)
    """
    if seed is not None:
        random.seed(seed)

    sol      = initial_sol.copy()
    best_sol = sol.copy()

    all_idx = list(range(problem.n))

    for it in range(max_iter):
        # Décroissance géométrique de la température
        T = T_start * (T_end / T_start) ** (it / max_iter)

        # --- Choisir un mouvement aléatoire ---
        move = random.randint(0, 2)

        new_sol = sol.copy()
        valid   = False

        if move == 0:  # ADD
            candidates = [i for i in all_idx if new_sol.can_add(i)]
            if candidates:
                i = random.choice(candidates)
                new_sol.add_resource(i)
                valid = True

        elif move == 1:  # REMOVE
            if sol.selected:
                i = random.choice(list(sol.selected))
                new_sol.remove_resource(i)
                valid = True

        else:  # SWAP
            if sol.selected:
                not_sel = [i for i in all_idx if i not in sol.selected]
                if not_sel:
                    r = random.choice(list(sol.selected))
                    a = random.choice(not_sel)
                    new_cost = sol.total_cost - problem.costs[r] + problem.costs[a]
                    if new_cost <= problem.B + 1e-9:
                        new_sol.remove_resource(r)
                        new_sol.add_resource(a)
                        valid = True

        if not valid:
            continue

        # --- Critère d'acceptation ---
        cur_cov,  cur_neg_cost  = sol.evaluate()
        new_cov,  new_neg_cost  = new_sol.evaluate()

        # Delta normalisé sur [−1, +1] (couverture prioritaire)
        delta = (new_cov - cur_cov) + (new_neg_cost - cur_neg_cost) * 1e-4

        if delta >= 0 or random.random() < math.exp(delta / (T + 1e-12)):
            sol = new_sol

        if sol.evaluate() > best_sol.evaluate():
            best_sol = sol.copy()

    return best_sol


# ==============================================================================
# GRASP (bonus : multidémarrage avec glouton randomisé)
# ==============================================================================

def grasp(problem, n_iter=30, alpha=0.3, ls_iter=500, seed=None):
    """
    GRASP : Greedy Randomized Adaptive Search Procedure.

    À chaque itération :
      1. Construit une solution initiale avec le glouton randomisé
      2. Améliore avec une recherche locale légère
      3. Garde la meilleure solution globale

    Paramètres :
        n_iter  : nombre de redémarrages
        alpha   : degré de randomisation (0 = glouton pur, 1 = aléatoire pur)
        ls_iter : nb max d'itérations de recherche locale par redémarrage
    """
    if seed is not None:
        random.seed(seed)

    best_sol = None

    for _ in range(n_iter):
        sol = greedy_constructive(problem, randomized=True, alpha=alpha)
        sol = local_search(problem, sol, max_iter=ls_iter)
        if best_sol is None or sol.evaluate() > best_sol.evaluate():
            best_sol = sol.copy()

    return best_sol


# ==============================================================================
# PIPELINE DE RÉSOLUTION
# ==============================================================================

def solve(filename, output_dir=None, verbose=True, n_runs=3, base_seed=42):
    """
    Pipeline complet pour une instance.

    Étapes :
      1. Chargement de l'instance
      2. Heuristique gloutonne (déterministe)
      3. Recherche locale (déterministe)
      4. Recuit simulé — lancé n_runs fois avec des seeds différentes
         pour la reproductibilité et la mesure de stabilité
      5. GRASP — lancé en parallèle des runs SA
      6. Sauvegarde de la meilleure solution toutes méthodes confondues

    Paramètres :
        n_runs    : nombre de runs du recuit simulé (pour stats de stabilité)
        base_seed : seed de base ; le run k utilise la seed base_seed + k
    """
    t_total = time.time()

    prob = Problem(filename)
    if verbose:
        print(f"\n{'─'*55}")
        print(f"  Instance : {prob.instance_name}")
        print(f"  n={prob.n} ressources | m={prob.m} cibles | B={prob.B}")
        print(f"{'─'*55}")

    results = {}
    max_it  = max(10000, prob.n * prob.m * 3)

    # ── 1. Glouton ────────────────────────────────────────────
    t0         = time.time()
    sol_greedy = greedy_constructive(prob)
    results['greedy'] = {
        'sol': sol_greedy, 'time': time.time() - t0,
        'covered': sol_greedy.num_covered, 'cost': sol_greedy.total_cost,
    }
    if verbose:
        pct = 100 * sol_greedy.num_covered / prob.m
        print(f"  Glouton      : {sol_greedy.num_covered:4d}/{prob.m} cibles "
              f"({pct:5.1f}%)  coût={sol_greedy.total_cost:7.1f}  "
              f"[{results['greedy']['time']:.3f}s]")

    # ── 2. Recherche locale ───────────────────────────────────
    t0     = time.time()
    sol_ls = local_search(prob, sol_greedy)
    results['local_search'] = {
        'sol': sol_ls, 'time': time.time() - t0,
        'covered': sol_ls.num_covered, 'cost': sol_ls.total_cost,
    }
    if verbose:
        pct = 100 * sol_ls.num_covered / prob.m
        print(f"  Rech. locale : {sol_ls.num_covered:4d}/{prob.m} cibles "
              f"({pct:5.1f}%)  coût={sol_ls.total_cost:7.1f}  "
              f"[{results['local_search']['time']:.3f}s]")

    # ── 3. Recuit simulé (n_runs fois, seeds fixes) ───────────
    sa_covered_list = []
    sa_cost_list    = []
    best_sa         = None
    t0              = time.time()

    for k in range(n_runs):
        seed_k = base_seed + k
        sol_k  = simulated_annealing(prob, sol_ls, max_iter=max_it, seed=seed_k)
        sa_covered_list.append(sol_k.num_covered)
        sa_cost_list.append(sol_k.total_cost)
        if best_sa is None or sol_k.evaluate() > best_sa.evaluate():
            best_sa = sol_k

    t_sa = time.time() - t0
    sa_mean_cov  = sum(sa_covered_list) / n_runs
    sa_std_cov   = (sum((x - sa_mean_cov)**2 for x in sa_covered_list) / n_runs) ** 0.5
    sa_mean_cost = sum(sa_cost_list) / n_runs

    results['simulated_annealing'] = {
        'sol': best_sa, 'time': t_sa,
        'covered': best_sa.num_covered, 'cost': best_sa.total_cost,
        'mean_covered': sa_mean_cov, 'std_covered': sa_std_cov,
        'mean_cost': sa_mean_cost, 'n_runs': n_runs,
    }
    if verbose:
        pct = 100 * best_sa.num_covered / prob.m
        print(f"  Recuit simulé: {best_sa.num_covered:4d}/{prob.m} cibles "
              f"({pct:5.1f}%)  coût={best_sa.total_cost:7.1f}  "
              f"[{t_sa:.3f}s × {n_runs} runs]")
        print(f"               moy={sa_mean_cov:.1f} cibles  "
              f"écart-type={sa_std_cov:.2f}  coût moy={sa_mean_cost:.1f}")

    # ── 4. GRASP ──────────────────────────────────────────────
    t0       = time.time()
    sol_gsp  = grasp(prob, n_iter=20, alpha=0.3, ls_iter=500, seed=base_seed)
    t_grasp  = time.time() - t0
    results['grasp'] = {
        'sol': sol_gsp, 'time': t_grasp,
        'covered': sol_gsp.num_covered, 'cost': sol_gsp.total_cost,
    }
    if verbose:
        pct = 100 * sol_gsp.num_covered / prob.m
        print(f"  GRASP        : {sol_gsp.num_covered:4d}/{prob.m} cibles "
              f"({pct:5.1f}%)  coût={sol_gsp.total_cost:7.1f}  "
              f"[{t_grasp:.3f}s]")

    # ── 5. Meilleure solution toutes méthodes ─────────────────
    best = max(
        [sol_greedy, sol_ls, best_sa, sol_gsp],
        key=lambda s: s.evaluate()
    )

    out_path = best.save(output_dir=output_dir)
    elapsed  = time.time() - t_total

    if verbose:
        pct = 100 * best.num_covered / prob.m
        print(f"\n  ✓ Meilleure  : {best.num_covered}/{prob.m} cibles "
              f"({pct:.1f}%)  coût={best.total_cost:.1f}")
        print(f"  ✓ Sauvegardé : {out_path}  [total {elapsed:.3f}s]")

    return best, results


BENCHMARK_FILE = "benchmark_results.txt"


def benchmark(directory, output_dir=None):
    """
    Lance solve() sur toutes les instances d'un dossier,
    affiche le tableau récapitulatif dans le terminal
    ET l'écrit dans benchmark_results.txt (écrasé à chaque run).
    """
    import re

    files = glob.glob(os.path.join(directory, "*.txt"))
    files = [f for f in files if not os.path.basename(f).startswith("sol_")]

    def numeric_sort_key(path):
        # Extrait tous les nombres du nom de fichier et trie par valeurs numériques
        # ex : "inst30_50_1.txt" → (30, 50, 1)  /  "inst150_120_2.txt" → (150, 120, 2)
        return tuple(int(x) for x in re.findall(r'\d+', os.path.basename(path)))

    files = sorted(files, key=numeric_sort_key)

    if not files:
        print(f"Aucune instance trouvée dans {directory}")
        return

    summary = []
    for f in files:
        best, res = solve(f, output_dir=output_dir, verbose=True)
        prob = best.problem
        summary.append({
            'instance': prob.instance_name,
            'n': prob.n, 'm': prob.m, 'B': prob.B,
            'greedy':  res['greedy']['covered'],
            'ls':      res['local_search']['covered'],
            'sa':      res['simulated_annealing']['covered'],
            'grasp':   res['grasp']['covered'],
            'best':    best.num_covered,
            'cost':    best.total_cost,
            'std_cov': res['simulated_annealing']['std_covered'],
            't_greedy': res['greedy']['time'],
            't_ls':     res['local_search']['time'],
            't_sa':     res['simulated_annealing']['time'],
            't_grasp':  res['grasp']['time'],
        })

    # ── Construire les lignes du tableau ─────────────────────
    header = (
        f"  {'Instance':<22} {'n':>4} {'m':>4} {'B':>6}  "
        f"{'Glouton':>8} {'RL':>8} {'RecSim':>8} {'GRASP':>8}  "
        f"{'Meilleur':>8}  {'Coût':>8}  {'σ cov':>6}"
    )
    sep_double = '═' * 92
    sep_single = '─' * 92

    rows = []
    for r in summary:
        g   = f"{r['greedy']}/{r['m']}"
        ls  = f"{r['ls']}/{r['m']}"
        sa  = f"{r['sa']}/{r['m']}"
        gp  = f"{r['grasp']}/{r['m']}"
        bst = f"{r['best']}/{r['m']}"
        rows.append(
            f"  {r['instance']:<22} {r['n']:>4} {r['m']:>4} {r['B']:>6.0f}  "
            f"{g:>8} {ls:>8} {sa:>8} {gp:>8}  "
            f"{bst:>8}  {r['cost']:>8.1f}  {r['std_cov']:>6.2f}"
        )

    # Lignes de temps d'exécution par instance
    time_rows = []
    for r in summary:
        time_rows.append(
            f"  {r['instance']:<22}  "
            f"Glouton={r['t_greedy']:.3f}s  "
            f"RL={r['t_ls']:.3f}s  "
            f"RecSim={r['t_sa']:.3f}s  "
            f"GRASP={r['t_grasp']:.3f}s"
        )

    # ── Affichage terminal ────────────────────────────────────
    print(f"\n{sep_double}")
    print(header)
    print(sep_single)
    for row in rows:
        print(row)
    print(sep_double)

    # ── Écriture fichier (mode 'w' → écrase l'ancien) ────────
    run_time = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(BENCHMARK_FILE, 'w', encoding='utf-8') as f:
        f.write(f"Benchmark — {run_time}\n")
        f.write(f"Instances  : {directory}\n")
        f.write(f"Solutions  : {output_dir or SOL_DIR}/\n\n")

        f.write(f"{sep_double}\n")
        f.write(f"{header}\n")
        f.write(f"{sep_single}\n")
        for row in rows:
            f.write(f"{row}\n")
        f.write(f"{sep_double}\n\n")

        f.write("Temps d'exécution par instance :\n")
        f.write(f"{sep_single}\n")
        for row in time_rows:
            f.write(f"{row}\n")
        f.write(f"{sep_single}\n")

    print(f"\n  ✓ Résultats sauvegardés : {BENCHMARK_FILE}")



# ==============================================================================
# POINT D'ENTRÉE
# ==============================================================================

HELP_TEXT = """
Usage : python3 solution.py [OPTION] [ARGUMENT]

Options :
  <fichier>              Résoudre une instance et sauvegarder la solution
                           Ex : python3 solution.py inst10_20_0.txt

  --all <dossier>        Résoudre toutes les instances d'un dossier
                           Ex : python3 solution.py --all ./instances/

  --benchmark <dossier>  Comme --all, mais affiche un tableau récapitulatif
                         comparant Glouton / Rech. locale / Recuit simulé / GRASP
                           Ex : python3 solution.py --benchmark ./instances/

  --grasp <fichier>      Résoudre une instance avec GRASP uniquement
                         (multidémarrage glouton randomisé + recherche locale)
                           Ex : python3 solution.py --grasp inst50_30_2.txt

  --reset-all            Supprimer le dossier de solutions ({SOL_DIR}/)
                           Ex : python3 solution.py --reset-all

  -h, --help             Afficher ce message d'aide

Dossier de sortie :
  Les fichiers de solution sont créés dans ./{SOL_DIR}/
  Format : sol_<nom_instance>.txt
    Ligne 1 — nombre de ressources sélectionnées
    Ligne 2 — indices des ressources (séparés par espaces)

Reproductibilité :
  Le recuit simulé est lancé 3 fois avec des seeds fixes (42, 43, 44).
  Les résultats sont donc identiques d'un run à l'autre.
"""

SOL_DIR = "sol_instances"


def print_help():
    print(HELP_TEXT.replace("{SOL_DIR}", SOL_DIR))


def reset_solutions():
    import shutil
    if os.path.isdir(SOL_DIR):
        shutil.rmtree(SOL_DIR)
        print(f"  ✓ Dossier '{SOL_DIR}/' supprimé.")
    else:
        print(f"  Rien à supprimer : le dossier '{SOL_DIR}/' n'existe pas.")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print_help()
        sys.exit(0)

    mode = sys.argv[1]

    if mode == "--reset-all":
        reset_solutions()

    elif mode == "--all":
        if len(sys.argv) < 3:
            print("Erreur : --all attend un dossier en argument.")
            print("  Ex : python3 solution.py --all ./instances/")
            sys.exit(1)
        directory = sys.argv[2]
        files = sorted(glob.glob(os.path.join(directory, "*.txt")))
        files = [f for f in files if not os.path.basename(f).startswith("sol_")]
        if not files:
            print(f"Aucune instance trouvée dans '{directory}'")
            sys.exit(1)
        for f in files:
            solve(f, output_dir=SOL_DIR)

    elif mode == "--grasp":
        if len(sys.argv) < 3:
            print("Erreur : --grasp attend un fichier en argument.")
            print("  Ex : python3 solution.py --grasp inst50_30_2.txt")
            sys.exit(1)
        filename = sys.argv[2]
        if not os.path.exists(filename):
            print(f"Erreur : fichier introuvable : '{filename}'")
            sys.exit(1)
        prob    = Problem(filename)
        print(f"\n  GRASP sur {prob.instance_name}  "
              f"(n={prob.n}, m={prob.m}, B={prob.B})")
        t0      = time.time()
        sol     = grasp(prob, n_iter=50, alpha=0.3, ls_iter=800, seed=42)
        elapsed = time.time() - t0
        pct     = 100 * sol.num_covered / prob.m
        print(f"  Résultat : {sol.num_covered}/{prob.m} cibles "
              f"({pct:.1f}%)  coût={sol.total_cost:.1f}  [{elapsed:.3f}s]")
        out = sol.save(output_dir=SOL_DIR)
        print(f"  Sauvegardé : {out}")

    elif mode == "--benchmark":
        if len(sys.argv) < 3:
            print("Erreur : --benchmark attend un dossier en argument.")
            print("  Ex : python3 solution.py --benchmark ./instances/")
            sys.exit(1)
        directory = sys.argv[2]
        benchmark(directory, output_dir=SOL_DIR)

    else:
        # Mode simple : un seul fichier
        filename = sys.argv[1]
        if filename.startswith("--"):
            print(f"Option inconnue : '{filename}'")
            print("  Utilisez -h ou --help pour voir les options disponibles.")
            sys.exit(1)
        if not os.path.exists(filename):
            print(f"Erreur : fichier introuvable : '{filename}'")
            sys.exit(1)
        solve(filename, output_dir=SOL_DIR)