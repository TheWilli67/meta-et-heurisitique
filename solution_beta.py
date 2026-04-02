"""
Problème de couverture maximale sous contrainte de budget
Master CDSI - Semestre 10

Auteurs : William HERTRICH - Théo PLUVINAGE - Christophe GRILLET-AUBERT - Ludovic URBES

TODO :
    - ajouter mouvement REMOVE dans la recherche locale
    - passer le glouton en randomisé pour base GRASP
    - implémenter GRASP
    - ajouter seed en paramètre du recuit simulé
    - lancer le recuit plusieurs fois et afficher moyenne / écart-type
    - faire une vraie fonction benchmark avec tableau récap + export fichier
    - ajouter --benchmark, --grasp, --reset-all, --help dans le CLI
"""

import sys
import os
import random
import math
import time


# ==============================================================================
# STRUCTURES DE DONNÉES
# ==============================================================================

class Problem:

    def __init__(self, filename):
        self.filename = filename
        self.instance_name = os.path.splitext(os.path.basename(filename))[0]
        self._load(filename)

    def _load(self, filename):
        with open(filename, 'r') as f:
            tokens = f.read().split()

        idx = 0
        self.n = int(tokens[idx]);   idx += 1
        self.m = int(tokens[idx]);   idx += 1
        self.B = float(tokens[idx]); idx += 1

        self.costs = []
        for _ in range(self.n):
            self.costs.append(float(tokens[idx])); idx += 1

        self.covers = []
        self.covered_by = [set() for _ in range(self.m)]
        # TODO : utiliser covered_by dans le glouton pour ne parcourir
        #        que les ressources qui couvrent au moins une cible manquante

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

    def __init__(self, problem):
        self.problem     = problem
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

    def is_feasible(self):
        return self.total_cost <= self.problem.B + 1e-9

    def evaluate(self):
        return (self.num_covered, -self.total_cost)

    def add_resource(self, i):
        if i in self.selected:
            return
        self.selected.add(i)
        self.total_cost += self.problem.costs[i]
        for t in self.problem.covers[i]:
            if self.cover_count[t] == 0:
                self.num_covered += 1
            self.cover_count[t] += 1

    def remove_resource(self, i):
        if i not in self.selected:
            return
        self.selected.discard(i)
        self.total_cost -= self.problem.costs[i]
        for t in self.problem.covers[i]:
            self.cover_count[t] -= 1
            if self.cover_count[t] == 0:
                self.num_covered -= 1

    def marginal_coverage(self, i):
        return sum(1 for t in self.problem.covers[i] if self.cover_count[t] == 0)

    def coverage_loss(self, i):
        return sum(1 for t in self.problem.covers[i] if self.cover_count[t] == 1)

    # TODO : ajouter uncovered_targets() — retourne le set des cibles non couvertes
    #        utile pour le glouton optimisé avec covered_by

    def can_add(self, i):
        return (i not in self.selected and
                self.total_cost + self.problem.costs[i] <= self.problem.B + 1e-9)

    def save(self, output_dir=None):
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
                f"cost={self.total_cost:.2f}, feasible={self.is_feasible()})")


# ==============================================================================
# HEURISTIQUE CONSTRUCTIVE GLOUTONNE
# ==============================================================================

# TODO : ajouter paramètre randomized=False + alpha pour pouvoir l'utiliser dans GRASP

def greedy_constructive(problem):
    sol        = Solution(problem)
    candidates = list(range(problem.n))

    while True:
        best_i     = None
        best_score = -1

        for i in candidates:
            if not sol.can_add(i):
                continue
            mc = sol.marginal_coverage(i)
            if mc == 0:
                continue
            score = mc / problem.costs[i]
            if score > best_score:
                best_score = score
                best_i     = i

        if best_i is None:
            break

        sol.add_resource(best_i)
        candidates.remove(best_i)

    return sol


# ==============================================================================
# RECHERCHE LOCALE
# ==============================================================================

def local_search(problem, initial_sol, max_iter=1000):
    sol      = initial_sol.copy()
    best_sol = sol.copy()

    for _ in range(max_iter):
        improved = False

        # ADD
        best_add       = None
        best_add_score = (0, 0.0)

        for i in range(problem.n):
            if not sol.can_add(i):
                continue
            mc = sol.marginal_coverage(i)
            if mc == 0:
                continue
            score = (mc, -problem.costs[i])
            if score > best_add_score:
                best_add_score = score
                best_add       = i

        if best_add is not None:
            sol.add_resource(best_add)
            if sol.evaluate() > best_sol.evaluate():
                best_sol = sol.copy()
            improved = True
            continue

        # SWAP
        best_swap      = None
        best_swap_gain = (0, 0.0)

        selected_list = list(sol.selected)
        not_selected  = [i for i in range(problem.n) if i not in sol.selected]

        for r in selected_list:
            for a in not_selected:
                new_cost = sol.total_cost - problem.costs[r] + problem.costs[a]
                if new_cost > problem.B + 1e-9:
                    continue
                gain = sum(1 for t in problem.covers[a] if sol.cover_count[t] == 0)
                net_loss = sum(1 for t in problem.covers[r]
                               if sol.cover_count[t] == 1
                               and t not in problem.covers[a])
                delta_cov  = gain - net_loss
                delta_cost = problem.costs[r] - problem.costs[a]
                if (delta_cov, delta_cost) > best_swap_gain:
                    best_swap_gain = (delta_cov, delta_cost)
                    best_swap      = (r, a)

        if best_swap is not None and best_swap_gain > (0, 0.0):
            r, a = best_swap
            sol.remove_resource(r)
            sol.add_resource(a)
            if sol.evaluate() > best_sol.evaluate():
                best_sol = sol.copy()
            improved = True
            continue

        # TODO : ajouter REMOVE — retirer les ressources redondantes (coverage_loss == 0)
        #        améliore le critère secondaire sans perdre de couverture

        if not improved:
            break

    return best_sol


# ==============================================================================
# MÉTAHEURISTIQUE : RECUIT SIMULÉ
# ==============================================================================

# TODO : ajouter paramètre seed=None
# TODO : lancer n_runs fois, garder le meilleur, afficher moyenne + écart-type

def simulated_annealing(problem, initial_sol, max_iter=10000, T_start=50.0, T_end=0.05):
    sol      = initial_sol.copy()
    best_sol = sol.copy()

    all_idx = list(range(problem.n))

    for it in range(max_iter):
        T = T_start * (T_end / T_start) ** (it / max_iter)

        move    = random.randint(0, 2)
        new_sol = sol.copy()
        valid   = False

        if move == 0:  # ADD
            candidates = [i for i in all_idx if new_sol.can_add(i)]
            if candidates:
                new_sol.add_resource(random.choice(candidates))
                valid = True

        elif move == 1:  # REMOVE
            if sol.selected:
                new_sol.remove_resource(random.choice(list(sol.selected)))
                valid = True

        else:  # SWAP
            if sol.selected:
                not_sel = [i for i in all_idx if i not in sol.selected]
                if not_sel:
                    r = random.choice(list(sol.selected))
                    a = random.choice(not_sel)
                    if sol.total_cost - problem.costs[r] + problem.costs[a] <= problem.B + 1e-9:
                        new_sol.remove_resource(r)
                        new_sol.add_resource(a)
                        valid = True

        if not valid:
            continue

        cur_cov, cur_neg_cost = sol.evaluate()
        new_cov, new_neg_cost = new_sol.evaluate()
        delta = (new_cov - cur_cov) + (new_neg_cost - cur_neg_cost) * 1e-4

        if delta >= 0 or random.random() < math.exp(delta / (T + 1e-12)):
            sol = new_sol

        if sol.evaluate() > best_sol.evaluate():
            best_sol = sol.copy()

    return best_sol


# TODO : implémenter GRASP (multidémarrage glouton randomisé + recherche locale)
# def grasp(problem, n_iter=20, alpha=0.3):
#     ...


# ==============================================================================
# PIPELINE
# ==============================================================================

# TODO : fonction benchmark(directory) — tableau récap sur toutes les instances + export .txt

def solve(filename, output_dir=None, verbose=True):
    t_total = time.time()

    prob = Problem(filename)
    if verbose:
        print(f"\n{'─'*50}")
        print(f"  Instance : {prob.instance_name}")
        print(f"  n={prob.n} | m={prob.m} | B={prob.B}")
        print(f"{'─'*50}")

    t0         = time.time()
    sol_greedy = greedy_constructive(prob)
    t_greedy   = time.time() - t0
    if verbose:
        pct = 100 * sol_greedy.num_covered / prob.m
        print(f"  Glouton      : {sol_greedy.num_covered}/{prob.m} ({pct:.1f}%)"
              f"  coût={sol_greedy.total_cost:.1f}  [{t_greedy:.3f}s]")

    t0     = time.time()
    sol_ls = local_search(prob, sol_greedy)
    t_ls   = time.time() - t0
    if verbose:
        pct = 100 * sol_ls.num_covered / prob.m
        print(f"  Rech. locale : {sol_ls.num_covered}/{prob.m} ({pct:.1f}%)"
              f"  coût={sol_ls.total_cost:.1f}  [{t_ls:.3f}s]")

    t0     = time.time()
    max_it = max(10000, prob.n * prob.m * 3)
    sol_sa = simulated_annealing(prob, sol_ls, max_iter=max_it)
    t_sa   = time.time() - t0
    if verbose:
        pct = 100 * sol_sa.num_covered / prob.m
        print(f"  Recuit simulé: {sol_sa.num_covered}/{prob.m} ({pct:.1f}%)"
              f"  coût={sol_sa.total_cost:.1f}  [{t_sa:.3f}s]")

    # TODO : ajouter GRASP ici une fois implémenté

    best    = max([sol_greedy, sol_ls, sol_sa], key=lambda s: s.evaluate())
    outpath = best.save(output_dir=output_dir)
    elapsed = time.time() - t_total

    if verbose:
        pct = 100 * best.num_covered / prob.m
        print(f"\n  Meilleure : {best.num_covered}/{prob.m} ({pct:.1f}%)"
              f"  coût={best.total_cost:.1f}")
        print(f"  Sauvegardé : {outpath}  [{elapsed:.3f}s]")

    return best


# ==============================================================================
# POINT D'ENTRÉE
# ==============================================================================

SOL_DIR = "sol_instances"

if __name__ == "__main__":
    # TODO : ajouter --help, --benchmark, --grasp, --reset-all
    if len(sys.argv) < 2:
        print("Usage : python3 solution.py <fichier_instance>")
        print("        python3 solution.py --all <dossier>")
        sys.exit(1)

    if sys.argv[1] == "--all":
        if len(sys.argv) < 3:
            print("Erreur : --all attend un dossier.")
            sys.exit(1)
        import glob
        directory = sys.argv[2]
        files = sorted(glob.glob(os.path.join(directory, "*.txt")))
        files = [f for f in files if not os.path.basename(f).startswith("sol_")]
        for f in files:
            solve(f, output_dir=SOL_DIR)
    else:
        filename = sys.argv[1]
        if not os.path.exists(filename):
            print(f"Fichier introuvable : {filename}")
            sys.exit(1)
        solve(filename, output_dir=SOL_DIR)