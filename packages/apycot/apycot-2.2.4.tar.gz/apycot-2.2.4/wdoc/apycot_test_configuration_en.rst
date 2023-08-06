Test configuration
------------------

Vocabulary
``````````
* A **repository** is a usually version controlled sources (VCS) database, like
  SVN or Hg.

* A **package** is a generic term for some files related together as a project in
  a source repository.

* A **preprocessor** allow a specific construction / installation step required
  to build a test environment.
  Example preprocessors: 'setup_install' to install a package by using
  `python setup.py install`, 'make' call the `make` command...

* A **check** is a single functional test which may be applied to test a
  package. A **checker** is the object applying this functional test.
  Example checks: 'pyunit' to start python unittest, 'pylint' to start pylint...

- A **test environment** describes how to build the test environment in which
  checks will be executed: fetch source from vcs repository, fetch and install
  sources for dependencies...

All this information is gathered from TestConfig entities.

TestConfig and TestConfigGroup attributes
`````````````````````````````````````````

:VCS access configuration:

:Dependencies:

:Test execution configuration:

_

Repositories
------------

Apycot supports the following repository types. If you don't find the one you're
looking for, you may still write your own repository wrapper, and contribute it
;). The best way to do so for the moment is to look at the existing ones...

cvs
```
This repository type is used to fetch sources from a CVS repository.

svn
```
This repository type is used to fetch sources from a Subversion repository.


hg
``
This repository type is used to fetch sources from a Mercurial repository.


fs
``
This repository type is used to fetch sources from a file system repository (non
versioned). This may be useful to test projects in your working directory
(that's actually whats the --fs option of *runtest* is using instead of the
repository defined in the configuration file).

.. null
````
.. Used for internal and test purpose.

.. mock
..````
.. Used for internal and test purpose.

Configuration tips
------------------

* Once the bot is running, you can see `all available variables`_.

* You can give options to preprocessors and checkers by preceding the option
  name by the preprocessor or checker name. For instance, you can give the
  treshold option to the python_lint checker by adding ::

    python_lint_treshold = 4


* link to repository entity and grant access from the cubicweb instance to the
  apycot bot, so test launch is controlled by cubicweb and you don't have to
  maintain cron jobs to do so (though this solution may gives you finer control
  about which checks should be started at which time)

* vcsfile require local repository access, so those'll have to be available on
  the cubiciweb repository host

* but it's fine to give repository URL to TestConfiguration

* quick checks should be included in full checks (XXX to be fixed)

.. winclude:: apycot_links
