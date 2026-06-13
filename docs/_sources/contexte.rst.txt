.. _contexte:

Contexte et Formulation
=======================

Contexte applicatif
-------------------

Dans de nombreux scénarios de **cyberdéfense**, il est nécessaire de déployer
un nombre limité de ressources de surveillance afin de couvrir un ensemble de
cibles critiques :

- **Sondes IDS** — détection d'intrusions sur segments réseau
- **Règles de filtrage** — pare-feux et ACL sur flux entrants/sortants
- **Outils d'analyse de vulnérabilités** — scanners, agents d'audit

Le déploiement est contraint par un **budget** : il est impossible d'activer
toutes les ressources disponibles simultanément.

Ce problème appartient à la famille des **problèmes de couverture maximale**
(*Maximum Coverage Problem*), connu pour être NP-difficile, ce qui justifie
le recours aux heuristiques et métaheuristiques.

Formulation mathématique
------------------------

**Données du problème**

Étant donné :

* :math:`U = \{u_1, \dots, u_m\}` — un ensemble de **m cibles** à couvrir
* :math:`S = \{S_1, \dots, S_n\}` — un ensemble de **n ressources**,
  chacune couvrant un sous-ensemble de cibles :math:`S_i \subseteq U`
* :math:`c_i > 0` — le coût d'activation de la ressource :math:`S_i`
* :math:`B > 0` — le budget total disponible

**Variables de décision**

.. math::

   x_i \in \{0, 1\},\quad i = 1, \dots, n \qquad \text{(ressource i sélectionnée ?)}

   y_j \in \{0, 1\},\quad j = 1, \dots, m \qquad \text{(cible j couverte ?)}

**Objectif lexicographique**

.. math::

   \max \left( \sum_{j=1}^{m} y_j,\ -\sum_{i=1}^{n} c_i x_i \right)

1. **Critère principal** : maximiser le nombre de cibles couvertes :math:`\sum_{j} y_j`
2. **Critère secondaire** : à égalité, minimiser le coût total :math:`\sum_{i} c_i x_i`

**Contraintes**

.. math::

   \sum_{i=1}^{n} c_i x_i \leq B \qquad \text{(contrainte de budget)}

   y_j \leq \sum_{i \,:\, u_j \in S_i} x_i \qquad \forall j \in \{1,\dots,m\}

**Complexité**

Le problème est NP-difficile par réduction depuis le *Set Cover Problem*. Pour
:math:`m` cibles et :math:`n` ressources, l'espace de solutions feasibles est
de taille :math:`O(2^n)`, rendant toute énumération exhaustive impossible au-delà
de quelques dizaines de ressources.

Format des instances
--------------------

Les fichiers d'instance suivent le format texte suivant :

.. code-block:: text

   n m B
   c_1 c_2 ... c_n
   k_1 u_11 u_12 ...
   k_2 u_21 u_22 ...
   ...

.. list-table:: Description des champs
   :header-rows: 1
   :widths: 15 55

   * - Symbole
     - Signification
   * - ``n``
     - Nombre de ressources disponibles
   * - ``m``
     - Nombre de cibles à couvrir
   * - ``B``
     - Budget total
   * - ``c_i``
     - Coût d'activation de la ressource i
   * - ``k_i``
     - Nombre de cibles couvertes par la ressource i
   * - ``u_ij``
     - Indice (base 0) de la j-ième cible couverte par i

Instances de test
-----------------

Le jeu de 12 instances fourni couvre une large gamme de tailles :

.. list-table::
   :header-rows: 1
   :widths: 25 10 10 10

   * - Instance
     - n (ressources)
     - m (cibles)
     - B (budget)
   * - ``inst10_20_0``
     - 10
     - 20
     - 80
   * - ``inst15_30_0``
     - 15
     - 30
     - 120
   * - ``inst20_30_1``
     - 20
     - 30
     - 150
   * - ``inst20_40_0``
     - 20
     - 40
     - 140
   * - ``inst30_50_1``
     - 30
     - 50
     - 150
   * - ``inst30_80_0``
     - 30
     - 80
     - 240
   * - ``inst50_30_2``
     - 50
     - 30
     - 200
   * - ``inst50_80_1``
     - 50
     - 80
     - 250
   * - ``inst60_90_1``
     - 60
     - 90
     - 250
   * - ``inst70_40_2``
     - 70
     - 40
     - 200
   * - ``inst90_50_2``
     - 90
     - 50
     - 270
   * - ``inst150_120_2``
     - 150
     - 120
     - 450
