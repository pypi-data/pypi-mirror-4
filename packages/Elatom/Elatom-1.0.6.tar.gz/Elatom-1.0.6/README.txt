Esperanto and French translations above.

Podcast downloader in Python3
=============================

A podcast downloader developed in Python 3 with Curses and Tkinter interfaces.

It can also be used in crontab to grab automatically the new media.
It reads RSS 2.0 and Atom 1.0. All files are downloaded simultaneously to speed up total download.
It aims to be a single file for basic features, to facilitate the install.
Additional files provide translations (Esperanto, French, German, Russian an Turkish), or unit tests.

Installation
------------

1/ Get the sources
   - From bazaar:
      bzr lp:elatom
   - From the website
      https://launchpad.net/elatom
   - From PyPI
      http://pypi.python.org/pypi/Elatom/
2/ Extract the sources, if you downloaded an archive
3/ Optionally, you can install
    python setup.py install

You can use pip (http://www.pip-installer.org/) to install:
   pip install Elatom

Usage
-----

Crontab
~~~~~~~

0 * * * * elatom.py --quiet

Command line
~~~~~~~~~~~~

Simply run `elatom.py -h` to get help or `elatom.py -c` to display the Curses interface (not available on Windows).
You can add, delete, activate, inactivate or list feeds.

Graphical interface
~~~~~~~~~~~~~~~~~~~

Simply run `elatom.py`.
To start downloading, click on "Start".
The interface will quit automatically after downloading.

Podkast-elŝutilo en Pitono3
============================

Podkast-elŝutilo programita en Pitono3 kun Curses kaj TkInter interfacoj.

Ĝi povas esti uzita en crontab por akiri auxtomate la novajn plurmediajn dosierojn.
Ĝi legas RSS 2.0 kaj Atom 1.0. Ĉiuj dosieroj estas elŝutitaj samtempe por plirapidigi la tutan elŝutadon.
Ĝi celas esti unu nuran dosieron por la bazaj eblecoj, por faciligi la instaladon.
Kromaj dosieroj provizas tradukadon (en esperanto, en la franca, germana, turka kaj rusa), aux unuecajn testojn.
   
Gestionnaire de téléchargement de balados en Python 3
=====================================================

Un gestionnaire de téléchargement de balados (podcast) développé en Python 3 avec des interfaces Curses et TkInter.

Il peut être utilisé dans un crontab pour récupérer automatiquement les nouveaux fichiers multimédias.
Il lit les flux RSS 2.0 et Atom 1.0. Tous les dossiers sont téléchargés en même temps pour accélérer le téléchargement total.
Le projet vise à fournir un seul dossier pour les fonctionnalités de base pour faciliter l'installation.
Des fichiers supplémentaires fournissent la traduction (Espéranto, français, allemand, turc et russe) ou les tests unitaires.

