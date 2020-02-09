Getting started - Faire tourner le projet
==========================================

Cloner le projet
------------------

La première chose à faire de cloner le répertoire de code.
Ce dernier est disponible à l’adresse:

https://github.com/tgrandjean/OC-sante-publique-france/

Avec git
^^^^^^^^^
::

 git clone https://github.com/tgrandjean/OC-sante-publique-france

Sans git
^^^^^^^^^

Allez sur github, cliquez sur "Clone or download" et cliquez sur "download zip".


Sous Linux
---------------
Installez un environnement virtuel
::

  $ make create_environment

en cas de problème, essayez la méthode suivante.
::

  $ virtualenv env
  ...
  $ source env/bin/activate
  (env)$ pip install -r requirements.txt


Sous Windows
---------------
Dans windows powershell
::

  > py -m virtualenv env
  ...
  > .\env\Scripts\activate
  (env)> pip install -r requirements.txt


Installer le Kernel Jupyter dans l'environnement virtuel.
------------------------------------------------------------

Linux
^^^^^
::

  (env)$ python -m ipykernel install --user --name=nutriscore
  Installed kernelspec nutriscore in /home/user/.local/share/jupyter/kernels/nutriscore

Windows
^^^^^^^^
::

  (env)> pip install ipykernel --user --name=nutriscore
  Installed kernelspec nutriscore in ...


Télécharger les données
-------------------------

Linux (Makefile)
^^^^^^^^^^^^^^^^^

Voir :ref:`commands`

Windows
^^^^^^^^
::

  (env)> py -m src.data.make_dataset .\data\raw -f csv


Lancer les notebooks
----------------------

Lancer jupyter notebooks/lab, cela dépend de votre plateforme, sous windows il
suffit de cliquer sur l'icone pour lancer jupyter. Sous Linux, il suffit de
lancer jupyter depuis un terminal `jupyter notebooks`.

Une fois Jupyter lancé, vous devrez naviguer jusqu'au répertoire notebooks puis
il suffit de lancer celui que vous désirez.

.. note::
    Seul les notebooks ayant un numéro type \*.0-tg-\*.ipynb sont nécessaires

.. warning::
    Le traitement des données se fait séquentiellement, si vous essayez de lancer
    le notebook 3.0-tg-... avant le 2.0-tg-... vous allez rencontrer l'erreur
    FileNotFoundError ou OSError.

.. warning::
    le notebook 1.1-tg-fetch-images.ipynb télécharge une quantité conséquente
    de données (images) **100-200 Go** et peut donc mettre du temps...
    Il est donc déconseillé de lancer se dernier si ce n'est pas nécessaire.

Lancer l'application de démo
------------------------------
::

  (env) streamlit run ./src/demo_app/demo.py


Une fois lancer l'application se lance lance dans le navigateur internet.

.. warning::
    Les données nécessaires à l'application sont générées à la fin du notebook
    `2.0-tg-data-cleaning.ipynb`
