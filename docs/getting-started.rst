Getting started - Faire tourner le projet
==========================================

Cloner le projet
------------------

La première chose à faire est de cloner le répertoire de code.
Ce dernier est disponible à l’adresse:

https://github.com/tgrandjean/OC-sante-publique-france/

Avec git
^^^^^^^^^
::

 git clone https://github.com/tgrandjean/OC-sante-publique-france
 cd OC-sante-publique-france

Sans git
^^^^^^^^^

Allez sur github, cliquez sur "Clone or download" et cliquez sur "download zip".
Une fois l'archive décompressée, ouvrez un terminal (powershell sous windows ou
shell sous linux/macOS) et placez vous dans le répertoire:
::

  cd ~\Téléchargements\OC-sante-publique-france

Pour la suite (sauf indication contraire), toute les commandes devront être
lancées depuis le répertoire de base.

Sous Linux - macOS (non testé)
------------------------------
Installez un environnement virtuel. Si vous n'avez pas virtualenv installé,
consultez https://gist.github.com/Geoyi/d9fab4f609e9f75941946be45000632b

.. note::
  Le projet est prévu pour fonctionner sur python 3.5+, vérifiez bien que
  toute les commandes sont lancées avec le bon interpréteur python !

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
    Seul les notebooks ayant un numéro de version type X.0- (exemple 1.0-tg-XXX.ipynb ) sont nécessaires
    pour générer les fichiers annexes.

.. note::
    Le traitement des données se fait séquentiellement, si vous essayez de lancer
    le notebook 3.0-tg-... avant le 2.0-tg-... vous allez rencontrer l'erreur
    FileNotFoundError ou OSError.

.. warning::
    le notebook 1.1-tg-fetch-images.ipynb télécharge une quantité conséquente
    de données (images) **100-200 Go** et peut donc mettre du temps...
    Voir **carrément bloquer** votre ordinateur... Vous êtes prévenu!
    Il est donc déconseillé de lancer se dernier si ce n'est pas nécessaire.

Lancer l'application de démo
------------------------------
::

  (env) streamlit run ./src/demo_app/demo.py


Une fois lancer l'application se lance lance dans le navigateur internet.

.. note::
    Les données nécessaires à l'application sont générées à la fin du notebook
    `2.0-tg-data-cleaning.ipynb`
