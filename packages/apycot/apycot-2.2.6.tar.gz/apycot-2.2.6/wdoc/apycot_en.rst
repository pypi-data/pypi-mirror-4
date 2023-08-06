
Apycot is designed to be an extensible test automation tool usable for continuous
integration and continuous testing.

It can fetch source code from version-controlled repositories (like SVN or Hg),
run tests, then store the results and generate various reports from the data
collected. Once the tests are configured, users can be notified in realtime
when the status of a test changes or get a periodic report about the health
of the projects their work on.

.. image:: doc/images/apycot_processes.png

Cubicweb instances contain environment and test configurations, as well as test
execution information that may be used to build useful reports.

Once configured, you can explicitly queue a task (eg run tests for a
configuration) through a test configuration page. To get actual CI you'll have to
`automate this`_.

When a task is queued through `apycotclient` or the web user interface, an
apycot bot will get tasked with it:

* the bot will retrieve the configuration from the instance hosting it

* the bot will execute the task (setup environmenent, run tests) and 
  store the output in the instance from which it got the configuration.

.. winclude:: apycot_links
