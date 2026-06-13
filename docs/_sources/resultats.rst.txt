.. _resultats:

Résultats expérimentaux
========================

Conditions d'expérimentation
------------------------------

* **Machine** : exécution locale, Python 3.8+
* **Seeds** : fixes (42, 43, 44 pour le recuit simulé ; 42 pour GRASP)
* **Reproductibilité** : résultats identiques à chaque exécution

.. note::
   L'écart-type de couverture (σ cov) est **0.00** sur toutes les instances
   pour les 3 runs du recuit simulé, confirmant la stabilité des algorithmes.

Tableau de synthèse
-------------------

.. list-table::
   :header-rows: 1
   :widths: 22 5 5 6 9 9 9 9 9 8

   * - Instance
     - n
     - m
     - B
     - Glouton
     - Rech. locale
     - Rec. simulé
     - GRASP
     - **Meilleur**
     - Coût
   * - ``inst10_20_0``
     - 10
     - 20
     - 80
     - 20/20
     - 20/20
     - 20/20
     - 20/20
     - **20/20**
     - 62.0
   * - ``inst15_30_0``
     - 15
     - 30
     - 120
     - 30/30
     - 30/30
     - 30/30
     - 30/30
     - **30/30**
     - 95.0
   * - ``inst20_30_1``
     - 20
     - 30
     - 150
     - 30/30
     - 30/30
     - 30/30
     - 30/30
     - **30/30**
     - 106.0
   * - ``inst20_40_0``
     - 20
     - 40
     - 140
     - 40/40
     - 40/40
     - 40/40
     - 40/40
     - **40/40**
     - 104.0
   * - ``inst30_50_1``
     - 30
     - 50
     - 150
     - 50/50
     - 50/50
     - 50/50
     - 50/50
     - **50/50**
     - 92.0
   * - ``inst30_80_0``
     - 30
     - 80
     - 240
     - 80/80
     - 80/80
     - 80/80
     - 80/80
     - **80/80**
     - 168.0
   * - ``inst50_30_2`` ⚠️
     - 50
     - 30
     - 200
     - 29/30
     - 29/30
     - 29/30
     - 29/30
     - **29/30**
     - 175.0
   * - ``inst50_80_1``
     - 50
     - 80
     - 250
     - 80/80
     - 80/80
     - 80/80
     - 80/80
     - **80/80**
     - 133.0
   * - ``inst60_90_1``
     - 60
     - 90
     - 250
     - 90/90
     - 90/90
     - 90/90
     - 90/90
     - **90/90**
     - 99.0
   * - ``inst70_40_2``
     - 70
     - 40
     - 200
     - 40/40
     - 40/40
     - 40/40
     - 40/40
     - **40/40**
     - 187.0
   * - ``inst90_50_2``
     - 90
     - 50
     - 270
     - 49/50
     - 50/50
     - 50/50
     - 50/50
     - **50/50**
     - 244.0
   * - ``inst150_120_2``
     - 150
     - 120
     - 450
     - 120/120
     - 120/120
     - 120/120
     - 120/120
     - **120/120**
     - 228.0

⚠️ ``inst50_30_2`` : la cible manquante est mathématiquement inatteignable avec
le budget disponible, quelle que soit la combinaison de ressources choisie.
29/30 est donc l'**optimum global** pour cette instance.

Analyse par algorithme
-----------------------

Heuristique gloutonne
~~~~~~~~~~~~~~~~~~~~~

* **10/12 instances** couvertes à 100 % dès la phase gloutonne.
* Échec partiel sur ``inst50_30_2`` (29/30) et ``inst90_50_2`` (49/50).
* Temps de calcul : < 10 ms par instance.
* Avantage : très rapide, sert de base aux autres algorithmes.

Recherche locale
~~~~~~~~~~~~~~~~

* Corrige l'échec du glouton sur ``inst90_50_2`` : passe de 49/50 à **50/50**.
* N'apporte aucune amélioration sur les instances déjà résolues à 100 %.
* Améliore systématiquement le coût (critère secondaire) via les mouvements REMOVE.

Recuit simulé
~~~~~~~~~~~~~

* Résultats identiques à la recherche locale sur toutes les instances de ce jeu.
* Écart-type **0.00** sur les 3 runs (seeds 42, 43, 44) : grande stabilité.
* Apport potentiel sur des instances plus difficiles où la RL reste bloquée
  dans un optimum local.

GRASP
~~~~~

* Égale les meilleurs résultats sur toutes les instances.
* **Apport principal : réduction du coût** (critère secondaire) sur les grandes instances :

  - ``inst150_120_2`` : coût GRASP = 228 vs RecSim = 252 (économie de 24 unités)
  - ``inst30_80_0`` : coût GRASP = 168 vs RecSim = 175 (économie de 7 unités)

* Temps de calcul comparable au recuit simulé.

Conclusions
-----------

1. **Le glouton seul** est suffisant pour 10/12 instances — ce qui reflète la
   structure favorable du jeu de données (couvertures larges, budgets généreux).

2. **La recherche locale** apporte un correctif décisif sur ``inst90_50_2``
   et améliore systématiquement le coût via l'élimination des redondances.

3. **Les métaheuristiques** (RecSim et GRASP) n'améliorent pas la couverture
   sur ce jeu, mais GRASP réduit le coût sur les grandes instances,
   démontrant la valeur du multidémarrage pour le critère secondaire.

4. **inst50_30_2** est mathématiquement non-résoluble à 100 %, confirmant que
   le budget B=200 ne permet pas de couvrir les 30 cibles avec les ressources
   disponibles.
