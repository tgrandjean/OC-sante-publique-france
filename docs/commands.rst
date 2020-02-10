.. _commands:

Commandes
==========

Le fichier Makefile contient des commandes pour le projet. (Testé uniquement sous Linux)

Make requirements
^^^^^^^^^^^^^^^^^

Permet d'installer les dépendances du projet.


Make data
^^^^^^^^^^

Télécharge les données au format CSV depuis le site d'Openfoodfacts. Les données
se trouvent alors dans le répertoire data/raw

.. note::
    Il est possible de télécharger les données dans une base de données MongoDB
    avec le même script (c'était la première idée: utiliser le même format
    qu'Openfoodfacts or, le format est beaucoup plus lourd (10Go) et l'idée a
    été abandonnée.)

    Pour recharger la base de donnée d'Openfoodfacts dans une instance MongoDB,
    vous devez avoir docker installé (et démarré). Il suffit alors de modifier
    l'option --format (-f) dans le Makefile ou comme option si vous téléchargez
    les données en utilisant directement le script :ref:`make_dataset`

Make clean
^^^^^^^^^^^

Supprime tout les fichiers python compilés (.pyc)

Make lint
^^^^^^^^^^

Vérifie la structure visuelle du code
