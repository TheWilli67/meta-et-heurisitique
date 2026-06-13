.. _index:

Couverture Maximale sous Contrainte de Budget
=============================================

.. image:: https://img.shields.io/badge/Python-3.8%2B-blue
   :alt: Python 3.8+

.. image:: https://img.shields.io/badge/Statut-Stable-green
   :alt: Statut stable

.. image:: https://img.shields.io/badge/Licence-Académique-orange
   :alt: Académique

----

**Master Cyber-défense et Sécurité de l'Information — Semestre 10**

*Université Polytechnique Hauts-de-France · INSA Hauts-de-France*

*Module : Complexité, Heuristiques & Métaheuristiques*

----

Présentation
------------

Ce projet implémente et compare **quatre algorithmes** pour résoudre le
*Budgeted Maximum Coverage Problem* (BMCP) — un problème NP-difficile
d'optimisation combinatoire appliqué à la cyberdéfense.

L'objectif est de sélectionner un sous-ensemble de ressources de surveillance
(sondes IDS, règles de filtrage, outils d'analyse) pour **maximiser la
couverture de cibles critiques** tout en respectant une **contrainte de budget**.

.. note::
   11 instances sur 12 atteignent **100 % de couverture**. La seule exception
   (``inst50_30_2``) est mathématiquement inatteignable avec le budget disponible.

Algorithmes comparés
~~~~~~~~~~~~~~~~~~~~

+-------------------+------------------------------------------+
| Algorithme        | Type                                     |
+===================+==========================================+
| Glouton           | Heuristique constructive déterministe    |
+-------------------+------------------------------------------+
| Recherche locale  | Amélioration locale (ADD / SWAP / REMOVE)|
+-------------------+------------------------------------------+
| Recuit simulé     | Métaheuristique (3 runs, seeds fixes)    |
+-------------------+------------------------------------------+
| GRASP             | Métaheuristique (multidémarrage)         |
+-------------------+------------------------------------------+

Résultat clé
~~~~~~~~~~~~

.. code-block:: text

   ════════════════════════════════════════════════════════════════════
     Instance               n    m      B   Glouton       RL   RecSim    GRASP   Meilleur      Coût    σ cov
   ────────────────────────────────────────────────────────────────────
     inst10_20_0           10   20     80     20/20    20/20    20/20    20/20      20/20      62.0     0.00
     inst150_120_2        150  120    450   120/120  120/120  120/120  120/120    120/120     228.0     0.00
   ════════════════════════════════════════════════════════════════════

.. toctree::
   :maxdepth: 2
   :caption: Documentation

   contexte
   algorithmes
   utilisation
   api
   resultats

.. toctree::
   :maxdepth: 1
   :caption: Référence

   auteurs

Liens rapides
~~~~~~~~~~~~~

* :ref:`genindex` — Index général
* :ref:`modindex` — Index des modules
* :ref:`search` — Recherche dans la documentation
