.. _algorithmes:

Algorithmes
===========

Le pipeline complet s'exécute dans l'ordre suivant :

.. code-block:: text

   Glouton → Recherche locale → Recuit simulé (×3) → GRASP
                                        ↓
                               Meilleure solution conservée

.. note::
   L'objectif lexicographique ``(num_covered, -total_cost)`` est implémenté
   via la comparaison naturelle de tuples Python, sans condition supplémentaire.

----

Heuristique constructive gloutonne
------------------------------------

**Principe**

Construction itérative d'une solution faisable en sélectionnant à chaque étape
la ressource admissible maximisant le ratio :

.. math::

   \text{score}(i) = \frac{\text{couverture\_marginale}(i)}{c_i}

À chaque itération, seules les ressources couvrant au moins une cible manquante
sont évaluées (via l'index inverse ``covered_by``).

**Pseudo-code**

.. code-block:: text

   GLOUTON(problème, randomisé=False, alpha=0.3):
     sol ← solution vide
     tant que des cibles sont non couvertes:
       uncovered ← cibles non couvertes
       relevant  ← ∪_{t ∈ uncovered} covered_by[t]   # ressources pertinentes
       scores    ← [(i, mc(i)/c_i) pour i ∈ relevant si budget OK et mc(i)>0]
       si scores vide: stop
       trier scores par ratio décroissant
       si randomisé:
         choisir aléatoirement dans les top alpha% (GRASP)
       sinon:
         choisir le meilleur (déterministe)
       ajouter la ressource choisie
     retourner sol

**Complexité** : :math:`O(n \cdot k_{max})` par étape grâce à l'index ``covered_by``,
contre :math:`O(n^2 \cdot k_{max})` sans.

----

Recherche locale
----------------

**Principe**

Amélioration itérative d'une solution par exploration de voisinage. Trois types
de mouvements sont testés dans l'ordre de priorité à chaque itération :

.. list-table::
   :header-rows: 1
   :widths: 15 50 20

   * - Mouvement
     - Description
     - Stratégie
   * - **ADD**
     - Ajouter la meilleure ressource faisable qui augmente la couverture
     - First-improve
   * - **SWAP**
     - Remplacer une ressource sélectionnée par une autre avec un meilleur delta
     - Best-improve
   * - **REMOVE**
     - Retirer une ressource redondante (``coverage_loss == 0``) pour réduire le coût
     - First-improve

**Pseudo-code**

.. code-block:: text

   RECHERCHE_LOCALE(problème, sol_initiale, max_iter=2000):
     sol ← copie de sol_initiale
     pour iter de 1 à max_iter:
       # 1. ADD
       meilleur_add ← argmax_{i ∉ sol, budget_ok} (mc(i), -c_i)
       si meilleur_add trouvé: ajouter, continuer

       # 2. SWAP
       meilleur_swap ← argmax_{r ∈ sol, a ∉ sol} (Δcov, Δcoût)
       si gain > 0: échanger r ↔ a, continuer

       # 3. REMOVE
       si ∃ r ∈ sol avec coverage_loss(r) = 0: retirer r, continuer

       # Aucun mouvement améliore → arrêt
       break
     retourner meilleure solution vue

**Complexité** : :math:`O(n^2)` par itération pour la phase SWAP.

.. note::
   Le SWAP évalue **toutes** les paires (ressource retirée, ressource ajoutée)
   pour choisir le meilleur échange global (stratégie best-improve).

----

Recuit simulé (Simulated Annealing)
-------------------------------------

**Principe**

Métaheuristique inspirée du recuit métallurgique : acceptation probabiliste de
solutions dégradantes pour échapper aux optima locaux.

**Schéma de décroissance de température**

La température décroît **géométriquement** :

.. math::

   T(t) = T_{start} \cdot \left(\frac{T_{end}}{T_{start}}\right)^{t / \text{max\_iter}}

.. list-table:: Paramètres par défaut
   :header-rows: 1
   :widths: 20 15 40

   * - Paramètre
     - Valeur
     - Rôle
   * - ``T_start``
     - 50.0
     - Température initiale (forte exploration)
   * - ``T_end``
     - 0.05
     - Température finale (quasi-déterministe)
   * - ``max_iter``
     - 15 000
     - Nombre d'itérations
   * - Seeds
     - 42, 43, 44
     - Reproductibilité (3 runs)

**Critère d'acceptation**

.. math::

   \Delta = (\text{cov\_new} - \text{cov\_cur}) + (\text{coût\_neg\_new} - \text{coût\_neg\_cur}) \times 10^{-4}

   P(\text{accepter}) = \begin{cases} 1 & \text{si } \Delta \geq 0 \\ e^{\Delta / T} & \text{sinon} \end{cases}

Le facteur :math:`10^{-4}` normalise la contribution du coût pour préserver la
priorité lexicographique de la couverture.

**Voisinage** (choix aléatoire équiprobable) :

* ``ADD`` — ajouter une ressource admissible aléatoire
* ``REMOVE`` — retirer une ressource sélectionnée aléatoire
* ``SWAP`` — échanger une ressource sélectionnée contre une autre admissible

**Pseudo-code**

.. code-block:: text

   RECUIT_SIMULÉ(problème, sol_init, max_iter, T_start, T_end, seed):
     initialiser random avec seed
     sol ← copie de sol_init ; best ← sol
     pour t de 0 à max_iter:
       T ← T_start × (T_end/T_start)^(t/max_iter)
       move ← ADD / REMOVE / SWAP (aléatoire)
       new_sol ← appliquer move à sol
       Δ ← delta lexicographique normalisé
       si Δ ≥ 0 ou random() < exp(Δ/T): sol ← new_sol
       si sol > best: best ← sol
     retourner best

**Stabilité** : l'écart-type observé sur 3 runs (seeds 42, 43, 44) est
**0.00** sur toutes les instances.

----

GRASP
-----

**Principe**

*Greedy Randomized Adaptive Search Procedure* — combinaison d'un glouton
randomisé et d'une recherche locale, exécutés en multidémarrage.

**Paramètre alpha**

À chaque itération GRASP, la construction randomisée sélectionne aléatoirement
parmi les **top** :math:`\alpha = 30\%` candidats triés par ratio couverture/coût :

.. math::

   \text{RCL} = \{i : \text{score}(i) \geq \text{score}_{max} \cdot (1 - \alpha)\}

* :math:`\alpha = 0` → glouton déterministe pur
* :math:`\alpha = 1` → sélection entièrement aléatoire

**Paramètres**

.. list-table::
   :header-rows: 1
   :widths: 20 15 40

   * - Paramètre
     - Valeur
     - Rôle
   * - ``n_iter``
     - 20 (pipeline) / 30 (standalone)
     - Nombre de redémarrages
   * - ``alpha``
     - 0.3
     - Degré de randomisation (30 % de la RCL)
   * - ``ls_iter``
     - 500 (pipeline) / 800 (standalone)
     - Itérations de recherche locale par restart

**Pseudo-code**

.. code-block:: text

   GRASP(problème, n_iter=20, alpha=0.3, ls_iter=500):
     best ← None
     pour i de 1 à n_iter:
       sol ← GLOUTON(problème, randomisé=True, alpha=alpha)
       sol ← RECHERCHE_LOCALE(problème, sol, max_iter=ls_iter)
       si sol > best: best ← sol
     retourner best

**Apport vs Recuit simulé** : sur les grandes instances, GRASP obtient
systématiquement des **coûts inférieurs** (ex. : 228 vs 252 sur ``inst150_120_2``,
168 vs 175 sur ``inst30_80_0``), pour un temps de calcul comparable.

----

Choix techniques
----------------

Mises à jour incrémentales
~~~~~~~~~~~~~~~~~~~~~~~~~~

Le tableau ``cover_count[j]`` est maintenu en temps réel. Ajouter ou retirer
une ressource *i* coûte :math:`O(k_i)` au lieu de :math:`O(n \times m)`, ce qui rend
les algorithmes d'amélioration viables sur les grandes instances.

Index inverse ``covered_by``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``covered_by[j]`` = ensemble des ressources qui couvrent la cible *j*. Utilisé
dans le glouton pour restreindre la recherche aux seules ressources pertinentes,
réduisant la complexité d'un facteur :math:`n/|\text{relevant}|`.

Objectif lexicographique par tuple
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``evaluate()`` retourne ``(num_covered, -total_cost)``. Python compare les tuples
élément par élément, ce qui implémente naturellement la priorité couverture > coût
sans condition supplémentaire :

.. code-block:: python

   # Comparaison automatique via tuple Python
   (20, -62.0) > (19, -50.0)  # True : 20 cibles > 19 cibles
   (20, -62.0) > (20, -80.0)  # True : même couverture, coût moindre
