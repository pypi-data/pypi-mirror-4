# XXX only for all-in-one or repository config
options = (
    ('test-master',
     {'type' : 'yn',
      'default' : True,
      'help': ('Is the repository responsible to automatically start test? '
               'You should say yes unless you use a multiple repositories '
               'setup, in which case you should say yes on one repository, '
               'no on others'),
      'group': 'apycot', 'level': 1,
      }),
    )
