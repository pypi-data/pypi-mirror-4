Checkers
--------

A checker provides testing functionnalities. Its return status can be a
"success" if the test passed, a "failure" if the test failed or an "error"
if the test could not be run to completion (maybe the environment could not
be set up or the test program was badly written).

Apycot comes with several checkers described below. If you do not find the
checker you are looking for, write your own by deriving an existing one and
contribute it back to the apycot project ;).

Some checkers depend on third-party programs (usually a Python package or
an external command) and may not be available on your system.

Once the bot is running, you can see checker and preprocessors.

General Checkers options
````````````````````````

All checkers support the following options :

+-------------------+-------+--------------------------------------------------+
|   name            |  req. |   description                                    |
+===================+=======+==================================================+
| max_status        |  no   | A maximum result this checker cannot exceed      |
+-------------------+-------+--------------------------------------------------+
| status_cap_reason |  no   | The reason why this checker is capped            |
+-------------------+-------+--------------------------------------------------+

File checkers
``````````````

A file checker acts on files according to their extension. The check succeeds
if each and every file passes the test independantly.

All the file checkers support the following options :

+----------+-------+----------------------------------------------------------+
|   name   |  req. |   description                                            |
+==========+=======+==========================================================+
| ignore   |  no   | comma separated list some files or directories to ignore |
+----------+-------+----------------------------------------------------------+

XXX Generate me

python_syntax
~~~~~~~~~~~~~
:extensions: .py
:description:
  Checks the syntax of Python files using the compile function coming with
  Python.

html_tidy
~~~~~~~~~
:depends on: mxtidy_
:extensions: .html, .htm
:description:
  Checks the syntax of HTML files using the mx Tidy module.

pt_syntax
~~~~~~~~~
:depends on: Zope_
:extensions: .pt, .zpt
:description:
  Checks the syntax of Page Template files using Zope's PageTemplates package.

xml_well_formed
~~~~~~~~~~~~~~~
:depends on: lxml_
:extensions: .xml
:description:
  Checks the well-formness of XML files using the lxml parser.

xml_valid
~~~~~~~~~
:depends on: lxml_
:extensions: .xml
:description:
  Checks the validity of XML files using the lxml validating parser.

rest_syntax
~~~~~~~~~~~
:depends on: docutils_
:extensions: .rst, .txt
:description:
  Checks the syntax of ReST files using the docutils package.

debian_lint
~~~~~~~~~~~
:depends on: lintian
:extensions: .deb, .dsc
:description:
  Checks debian packages by parsing the output of lintian.

debian_piuparts
~~~~~~~~~~~~~~~
:depends on: piuparts (and sudo configuration)
:extensions: .deb
:description:
  Checks debian packages by installing and uninstalling them with piuparts



Package checkers
````````````````

A package checker acts more globally, to locate some data or to make interact
results on each files to finally make the check succeed or failed.

XXX Generate me

python_lint
~~~~~~~~~~~
:depends on: pylint_
:description:
  Use Pylint to check a score for python package. The check fails if the score is
  inferior to a given treshold.
:options:
  +---------------------+--------+-------------------------------------------+
  |        name         |  req.  |   description                             |
  +=====================+========+===========================================+
  | treshold            |   yes  | the minimal note to obtain for the        |
  |                     |        | package from PyLint                       |
  +---------------------+--------+-------------------------------------------+
  | show_categories     |   no   | comma separated list of letter used to    |
  |                     |        | filter the message displayed default to   |
  |                     |        | Error and Fatal                           |
  +---------------------+--------+-------------------------------------------+
  | pylintrc            |   no   | The path to a pylint configuration file   |
  +---------------------+--------+-------------------------------------------+

python_unittest
~~~~~~~~~~~~~~~
:depends on: pyunit
:description:
  Execute tests found in the "test" or "tests" directory of the package. The check
  succeed if no test cases failed. Note each test module is executed by a spawed
  python interpreter and the output is parsed, so tests should use the default
  text output of the unittest framework, and avoid messages on stderr.
  
  +-----------------------------+------+--------------------------------------+
  |   name                      | req. |   description                        |
  +=============================+======+======================================+
  | coverage                    |  no  | Enable or disable coverage test (0   |
  |                             |      | or 1, default to 1 when devtools is  |
  |                             |      | available)                           |
  +-----------------------------+------+--------------------------------------+
  | test_dirs                   |  no  | List of comma separated candidates   |
  |                             |      | of tests directory. default to       |
  |                             |      | "test, tests"                        |
  +-----------------------------+------+--------------------------------------+
  | ignored_python_versions     |  no  | Comma separated version of python to |
  |                             |      | ignore when running the test.        |
  +-----------------------------+------+--------------------------------------+
  | tested_python_versions      |  no  | Comma separated version of python to |
  |                             |      | test when running the test.          |
  +-----------------------------+------+--------------------------------------+
  | use_pkginfo_python_versions |  no  | 0, or 1 (default to 1) run the tests |
  |                             |      | with the python's versions defined   |
  |                             |      | in the pkginfo module.               |
  +-----------------------------+------+--------------------------------------+

    * First, versions defined in the pkginfo module are imported (if enable).
    * Then versions defined into tested_python_versions are added.
    * finally version in ignored_python_versions are removed.

pycoverage
~~~~~~~~~~~~~~~~~~~~
:depends on: devtools_
:description:
  When devtools is available, test will be launched in a coverage mode. This test
  will gather coverage information, and will succeed if the test coverage is
  superior to a given treshold. *This checker must be executed after the
  python_unittest checker.*
:options:
  +----------+-------+---------------------------------------------------------+
  |   name   |  req. |   description                                           |
  +==========+=======+=========================================================+
  | treshold |  yes  | the minimal note to obtain for the test coverage        |
  +----------+-------+---------------------------------------------------------+

pkg_doc
~~~~~~~
:depends on: `rest_syntax`_, `xml_well_formed`_, `html_tidy`_
:description:
  Check some standard package documentation :

  * presence of some required files (README, INSTALL, ChangeLog)
  * plain text files in the "doc" directory are ReST files
  * xml files in the "doc" directory are well formed
  * html files in the "doc" directory are correct
  
  The 3 last tests will be done according to the presence of the respective
  checkers (which depends on external packages).
:options:
  +----------+-------+----------------------------------------------------------+
  |   name   |  req. |   description                                            |
  +==========+=======+==========================================================+
  | ignore   |  no   | comma separated list of files or directories to ignore   |
  +----------+-------+----------------------------------------------------------+

lgp_check
~~~~~~~~~~
:depends on: devtools_
:description:
  Check a package is conform to the `standard source tree` as described in the
  devtools package for a Python package. It'll also check the content of some 
  of the specified files, like __pkginfo__.py, MANIFEST.in...


.. winclude:: apycot_links
