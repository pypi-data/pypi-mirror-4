# repository specific stuff ####################################################

try:
    from cubicweb import server
except ImportError: # no server installation
    pass
else:
    options = (
        ('repository-import',
         {'type' : 'yn',
          'default': True,
          'help': 'Is the instance responsible to automatically import new '
                   'revisions from repositories? '
                   'You should say yes unless you don\'t want this behaviour '
                   'or if you use a multiple repositories setup, in which '
                   'case you should say yes on one repository, no on others.',
          'level': 2,
          'group': 'vcsfile',
          }),
        ('check-revision-interval',
         {'type' : 'int',
          'default': 5*60,
          'help': 'interval between checking of new revisions in repositories \
(default to 5 minutes).',
          'level': 2,
          'group': 'vcsfile',
          }),
        ('check-revision-commit-every',
         {'type' : 'int',
          'default': 1,
          'help': 'after how much new imported revisions the transaction \
should be commited (default to 1, e.g. on each revision).',
          'level': 2,
          'group': 'vcsfile',
          }),
        ('import-revision-content',
         {'type' : 'yn',
          'default': True,
          'help': 'This option is now deprecated in favor of the import_revision_content attribute per Repository.',
          'level': 2,
          'group': 'vcsfile',
          }),
        ('local-repo-cache-root',
         {'type':'string',
          'default': 'repo_cache', # XXX /var/lib/cubicweb/<instance>
          'help':'Local repository cache location (if not absolute, will be '
          'relative to instance data home directory).',
          'level': 2,
          'group': 'vcsfile'
          }
         ),
        ('cache-external-repositories',
         {'type':'yn',
          'default': False,
          'help':'Should repositories from external source have a local cache?'
          'This is usually not necessary, beside cases where for instance a '
          'narval bot on the same host as the instance could benefit from them '
          'to run apycot tests.',
          'level': 2,
          'group': 'vcsfile'
          }
         ),
        ('hgrc-path',
         {'type': 'string',
          'default': None,
          'help': 'a list of files or directories to search for mercurial configuration',
          'level': 2,
          'group': 'vcsfile',
          }
         ),
        )
