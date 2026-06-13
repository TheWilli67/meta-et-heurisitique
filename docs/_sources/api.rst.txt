.. _api:

Référence de l'API
==================

.. currentmodule:: solution

Ce module implémente la résolution du problème de couverture maximale sous
contrainte de budget. Il est conçu comme un script autonome mais ses classes
et fonctions sont utilisables par import.

.. code-block:: python

   from solution import Problem, Solution, greedy_constructive, local_search
   from solution import simulated_annealing, grasp, solve

Structures de données
----------------------

.. autoclass:: Problem
   :members:
   :special-members: __init__, __repr__
   :member-order: bysource

   **Exemple d'utilisation :**

   .. code-block:: python

      prob = Problem("instances/inst30_50_1.txt")
      print(prob)          # Problem(n=30, m=50, B=150.0)
      print(prob.costs)    # [c_0, c_1, ..., c_29]
      print(prob.covers[0])    # {t : ressource 0 couvre t}
      print(prob.covered_by[5])  # {i : ressource i couvre cible 5}

.. autoclass:: Solution
   :members:
   :special-members: __init__, __repr__
   :member-order: bysource

   **Exemple d'utilisation :**

   .. code-block:: python

      prob = Problem("instances/inst10_20_0.txt")
      sol  = Solution(prob)
      sol.add_resource(0)
      sol.add_resource(3)
      print(sol.num_covered)   # nombre de cibles couvertes
      print(sol.total_cost)    # coût total
      print(sol.evaluate())    # (num_covered, -total_cost)
      print(sol.is_feasible()) # True si coût ≤ budget

Algorithmes
-----------

.. autofunction:: greedy_constructive

   **Exemple :**

   .. code-block:: python

      # Glouton déterministe
      sol = greedy_constructive(prob)

      # Glouton randomisé (pour GRASP)
      sol = greedy_constructive(prob, randomized=True, alpha=0.3)

.. autofunction:: local_search

   **Exemple :**

   .. code-block:: python

      sol_init = greedy_constructive(prob)
      sol_améliorée = local_search(prob, sol_init, max_iter=2000)

.. autofunction:: simulated_annealing

   **Exemple :**

   .. code-block:: python

      sol_init = local_search(prob, greedy_constructive(prob))
      # Run avec seed fixe pour reproductibilité
      sol_sa = simulated_annealing(prob, sol_init, seed=42)
      # Run avec paramètres personnalisés
      sol_sa = simulated_annealing(
          prob, sol_init,
          max_iter=20000, T_start=100.0, T_end=0.01, seed=42
      )

.. autofunction:: grasp

   **Exemple :**

   .. code-block:: python

      # GRASP standalone (50 itérations)
      sol = grasp(prob, n_iter=50, alpha=0.3, ls_iter=800, seed=42)

      # GRASP léger pour pipeline
      sol = grasp(prob, n_iter=20, alpha=0.3, ls_iter=500, seed=42)

Pipeline principal
------------------

.. autofunction:: solve

   **Exemple :**

   .. code-block:: python

      best, results = solve("instances/inst30_50_1.txt", output_dir="sol_instances")

      # Accès aux résultats détaillés
      print(results['greedy']['covered'])
      print(results['simulated_annealing']['std_covered'])
      print(results['grasp']['time'])

.. autofunction:: benchmark

   **Exemple :**

   .. code-block:: python

      benchmark("instances/", output_dir="sol_instances")
      # → Affiche le tableau et écrit benchmark_results.txt

Utilitaires CLI
---------------

.. autofunction:: print_help

.. autofunction:: reset_solutions

Résumé des complexités
----------------------

.. list-table::
   :header-rows: 1
   :widths: 25 20 40

   * - Opération
     - Complexité
     - Commentaire
   * - ``add_resource(i)``
     - :math:`O(k_i)`
     - Mise à jour incrémentale de ``cover_count``
   * - ``remove_resource(i)``
     - :math:`O(k_i)`
     - Mise à jour incrémentale de ``cover_count``
   * - ``marginal_coverage(i)``
     - :math:`O(k_i)`
     - Parcours de ``covers[i]``
   * - ``coverage_loss(i)``
     - :math:`O(k_i)`
     - Parcours de ``covers[i]``
   * - ``greedy_constructive``
     - :math:`O(n \cdot k_{max})`
     - Par étape, avec index ``covered_by``
   * - ``local_search`` (par iter)
     - :math:`O(n^2)`
     - Phase SWAP, best-improve
   * - ``simulated_annealing``
     - :math:`O(\text{max\_iter} \cdot k_{max})`
     - Mouvements aléatoires unitaires
   * - ``grasp``
     - :math:`O(n\_iter \cdot (n \cdot k_{max} + n^2 \cdot ls\_iter))`
     - Glouton + RL par restart
