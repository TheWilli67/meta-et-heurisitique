.. _utilisation:

Guide d'utilisation
===================

Installation
------------

Aucune dépendance externe. Python 3.8+ suffit.

.. code-block:: bash

   git clone <url-du-dépôt>
   cd meta-et-heurisitique
   python3 solution.py --help

Commandes disponibles
---------------------

Résoudre une instance
~~~~~~~~~~~~~~~~~~~~~

Résout une instance et sauvegarde la solution dans ``sol_instances/`` :

.. code-block:: bash

   python3 solution.py instances/inst30_50_1.txt

Sortie typique :

.. code-block:: text

   ───────────────────────────────────────────────────────
     Instance : inst30_50_1
     n=30 ressources | m=50 cibles | B=150
   ───────────────────────────────────────────────────────
     Glouton      :   50/ 50 cibles (100.0%)  coût=   92.0  [0.001s]
     Rech. locale :   50/ 50 cibles (100.0%)  coût=   92.0  [0.012s]
     Recuit simulé:   50/ 50 cibles (100.0%)  coût=   92.0  [2.341s × 3 runs]
     GRASP        :   50/ 50 cibles (100.0%)  coût=   92.0  [0.123s]

     ✓ Meilleure  : 50/50 cibles (100.0%)  coût=92.0
     ✓ Sauvegardé : sol_instances/sol_inst30_50_1.txt

Résoudre toutes les instances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python3 solution.py --all instances/

Benchmark comparatif
~~~~~~~~~~~~~~~~~~~~~

Lance toutes les instances et affiche un tableau comparatif. Écrit également
les résultats dans ``benchmark_results.txt`` :

.. code-block:: bash

   python3 solution.py --benchmark instances/

GRASP seul
~~~~~~~~~~

Résout avec GRASP uniquement (50 itérations, recherche locale intensive) :

.. code-block:: bash

   python3 solution.py --grasp instances/inst90_50_2.txt

Réinitialiser les solutions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Supprime le dossier ``sol_instances/`` et toutes les solutions générées :

.. code-block:: bash

   python3 solution.py --reset-all

Aide
~~~~

.. code-block:: bash

   python3 solution.py -h
   python3 solution.py --help

Formats de fichiers
-------------------

Format d'entrée (instance)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   n m B
   c_1 c_2 ... c_n
   k_1 u_11 u_12 ...
   k_2 u_21 u_22 ...
   ...

Exemple pour 3 ressources, 4 cibles, budget 10 :

.. code-block:: text

   3 4 10
   3.0 5.0 4.0
   2 0 1
   2 1 2
   3 0 2 3

Format de sortie (solution)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   p
   xi1 xi2 ... xip

* Ligne 1 : nombre de ressources sélectionnées
* Ligne 2 : indices (base 0) des ressources sélectionnées, séparés par espaces
* Fichier : ``sol_instances/sol_<nom_instance>.txt``

Exemple :

.. code-block:: text

   2
   0 2

Format du benchmark
~~~~~~~~~~~~~~~~~~~

Le fichier ``benchmark_results.txt`` contient :

* L'horodatage du run
* Le tableau comparatif (Glouton / RL / RecSim / GRASP / Meilleur / Coût / σ)
* Les temps d'exécution détaillés par instance et par algorithme

.. code-block:: text

   Benchmark — 2025-11-20 14:32:01
   Instances  : instances/
   Solutions  : sol_instances/

   ════════════════════════════════════════════════════════
     Instance          n    m      B  Glouton   RL  RecSim ...
   ────────────────────────────────────────────────────────
     inst10_20_0      10   20     80    20/20 20/20   20/20 ...

Reproductibilité
----------------

Tous les algorithmes aléatoires utilisent des **seeds fixes**. Les résultats
sont identiques à chaque exécution sur la même machine :

.. list-table::
   :header-rows: 1
   :widths: 25 40

   * - Algorithme
     - Seed(s)
   * - Recuit simulé
     - 42, 43, 44 (3 runs indépendants)
   * - GRASP (pipeline)
     - 42
   * - GRASP (standalone ``--grasp``)
     - 42

.. code-block:: bash

   # Résultats identiques à chaque appel
   python3 solution.py --benchmark instances/
   python3 solution.py --benchmark instances/
   # → même benchmark_results.txt

Structure du projet
-------------------

.. code-block:: text

   .
   ├── solution.py              # Code source principal (842 lignes)
   ├── instances/               # Fichiers d'instances (.txt)
   │   ├── inst10_20_0.txt
   │   ├── inst15_30_0.txt
   │   └── ...                  # 12 instances au total
   ├── sol_instances/           # Solutions générées (créé automatiquement)
   │   ├── sol_inst10_20_0.txt
   │   └── ...
   ├── benchmark_results.txt    # Résultats du dernier benchmark
   ├── inst_test_budget.txt     # Instance de test (couverture impossible)
   ├── docs/                    # Documentation Sphinx
   └── README.md
