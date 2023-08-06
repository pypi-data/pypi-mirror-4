===================================
Mise en place d'une instance Apycot
===================================

:Auteurs:
     Alexandre Richardson,
     Charles Hébert,
     Logilab SA

:Version: 1.0 - 2010/01/27

.. contents:: Sommaire
.. section-numbering::

----------
Pré-requis
----------

- Ensemble des dépendances

* Cubicweb et cube apycot (et ses dépendances)
* Serveur pyro
* Apycotbot actif
* extension bfile de mercurial

---------
ApycotBot
---------

Configuration
=============

Apycotbot a besoin de deux fichiers de configuration:

 - `apycotbot.ini` : configuration des paramètres du bot, notamment de pyro
 - `apycotbot-cw-sources.ini`: configuration d'un utilisateur permettant au
   bot d'utiliser l'instance cubicweb-apycot.

Ces fichiers se trouvent dans le répertoire `/etc/`. Lors d'une installation
locale (sans droit), ces fichiers se trouvent dans le répertoire `~/etc/`.
Il faut une installation locale de apycotbot et des outils logilab-common.
Ne pas oublier de mettre à jour le `PYTHONPATH` faute de quoi ces fichiers
ne seront pas chargés.

Structure du fichier `apycotbot-cw-sources.ini`

.. sourcecode:: ini

  [nom_instance_cubicweb]

  user=bot_user
  password=bot_password

Par défaut, lors de la création d'un instance cubicweb-apycot, un utilisateur
`apycot` est créé.

Structure du fichier `apycotbot.ini`
------------------------------------

.. sourcecode:: ini

  [PROCESS-CONTROL]
  threads=1
  max-cpu-time=5 min
  max-time=10 min
  max-memory=500MB
  max-reprieve=60s
  [MAIN]
  cw-inst-id=:cubicweb.myapycot
  test-dir=/tmp/myapycot/
  [PYRO-NAME-SERVER]
  pyro-ns-host=cepheus.logilab.fr:9090
  [PYRO-SERVER]
  log-file=/tmp/myapycotbot.log
  log-threshold=INFO
  #host=
  pid-file=/tmp/myapycot.pid
  pyro-id=:cubicweb.myapycot

Quelques explications :

- `pyro-ns-host`, le serveur pyro,
- `cw-inst-id`, l'identifiant pyro de l'instance cubicweb-apycot,
- `pyro-id`, l'identidiant pyro du bot.

Les identifiants sont de la forme `:groupe.instance`.

Quelques commandes Pyro
-----------------------

Pyro pour Python Remote Object permet de partager des objets python entre le
bot et l'instance cubicweb-apycot. Le bot et l'instance cubicweb doivent être
enregistrés dans le Pyro Name Server.

On obtient la liste des clients avec la commande suivante :

.. class:: commande

  pyro-nsc listall

Il est possible que la suppression d'un client dans le pyro name server ne se
déroule pas correctement. Pour pouvoir relancer le bot, il faut supprimer ce
référencement avec la commande :

.. class:: commande

  pyro-nsc remove


Configuration
=============

La mise en place du bot en mode debug :

.. class:: commande

  apycotbot -D

---------------
Cubicweb-apycot
---------------

Créer une instance apycot
=========================

.. class:: commande

  cubicweb-ctl create apycot myapycot

(mise à jour si besoin du fichier source : db-host=mydbhost)

.. class:: commande

  cubicweb-ctl db-create myapycot

Configurer la communication de l'instance avec le bot
=====================================================

Modifier le fichier `all-in-one.conf`, section `[APYCOT]`
(`~/etc/cubicweb.d/myapycot` ou `/etc/cubicweb.d/myapycot`) pour être en
accord avec la configuration du bot:

.. sourcecode:: ini

  [APYCOT]

  bot-pyro-id=:cubicweb.myapycot
  bot-pyro-ns=myhost.mydomain.com:9090

- lancer l'instance cubicweb

.. class:: commande

  cubicweb-ctl start -D myapycot

- vérifier que le bot est correctement configuré :
  http://[moninstance]/view?vid=botstatus

Préparer les tests !
====================

Création d'un environnement de projet
-------------------------------------

- Spécifierle nom du projet,
- Choisir le type, nom et url du dépôt, (uniquement à titre informatif car
  ce n'est pas ce champ qui est utilisé pour connaître les branches du
  dépôt mais l'instance de l'entité dépôt),
- si le bot est correctement configuré, des indications sont précisées sous
  les boîtes `préprocesseurs`, `environnement`, `configuration`.

Créer une entité dépôt
-----------------------

Cette entité contient les informations du dépôt de l'outil de gestion de
configuration.

Les champs devant être saisies sont :
- le type (mercurial ou subversion)
- le chemin d'accès au dépôt

L'onglet révision permet de visualiser les différentes révisions.
Attention : la mise à jour de cet onglet peut-être longue pour nos
6000 changesets.

Créer une configuration de test
-------------------------------

1. Mise en place d'un environnement de projet

- créer un entrepôt mercurial pointant vers le dépôt de code,
- lier ce dépot à un nouvel environnement de projet,
- définir une variable d'environnement (environnement) :

`HGRCPATH=${TESTDIR}/[moninstance]/hgrc`

2. Créer un groupe de configuration de test

- définir un outil de vérification (vérifications) : `pytest`,
- définir les préprocesseurs (préprocesseurs) : `install=python_setup`,
- définir une variable d'environnement : `HGRCPATH=${TESTDIR}/[moninstance]/hgrc`,

3. Créer une configuration de test et la faire dépendre du groupe défini ci-dessus,

- définir une option pour `pytest` (configuration) : `pytest_argument=-m Corp`
- l'option `-m` lance une catégorie de tests

voir la documentation de pytest pour les détails.
