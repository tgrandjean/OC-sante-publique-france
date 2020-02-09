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

  make create_environment

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

  py -m virtualenv env
  ...
  .\env\Scripts\activate
  (env) pip install -r requirements.txt


Installer le Kernel Jupyter dans l'environnement virtuel.
------------------------------------------------------------

Linux
^^^^^
::

  (env)$ python -m ipykernel install --user --name=nutriscore
  Installed kernelspec myenv in /home/user/.local/share/jupyter/kernels/nutriscore

Windows
^^^^^^^^
::

  (env) pip install ipykernel --user --name=nutriscore
  Installed kernelspec myenv in ...
