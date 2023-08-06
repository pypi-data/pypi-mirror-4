osome
=====

The bucket of python shell wrappers around os library, no dependencies, simple API.

* Python2.6
* Python2.7
* Python3.3
* PyPy1.9

- osome: (python os module wrappers)

  - path - path wraper around all methods related to path manipulation
  - run - subprocess wrapper


Documentation
-------------
https://osome.readthedocs.org/


Code
----
https://github.com/xando/osome


Install
-------

.. code-block:: bash

   pip install osome



osome.path
---------------

.. code-block:: python

   >>> from osome import path

   >>> path('/var/log')
   /var/log

   >>> path('/var', 'log')
   /var/log

   >>> path('/var/log').own
   '766'

   >>> path('/var/log').is_dir()
   True

   >>> for e in path('/var/log'):
   ...     print e
   /var/log/boot.log
   /var/log/dmesg
   /var/log/faillog
   /var/log/kern.log
   /var/log/gdm

   >>> path('/var/log/').ls('*log')
   [/var/log/boot.log, /var/log/faillog, /var/log/kern.log]

   >>> path('/var/log') / 'syslog'
   /var/log/syslog

   >>> (path('/var/log') / 'syslog').exists

   >>> path('/var/log','syslog').open('r')
   <open file '/var/log/syslog', mode 'r' at 0x294c5d0>

   >>> path('/var/log').cp('copy', r=True)
   copy

   >>> path('/home/user/test_tmp_directory').replace('_', '-')
   '/home/user/test-tmp-directory'

   >>> location = path('/home/user/test_tmp_directory')
   >>> location.mv( location.replace('_', '-') )


osome.run
--------------


.. code-block:: python

  >>> from osome import run

  >>> print run('uname -r').stdout
  3.7.0-7-generic

  >>> run('uname -a').status
  0

  >>> print run('rm not_existing_directory').stderr
  rm: cannot remove `not_existing_directory': No such file or directory

  >>> print run('ls -la', 'wc -l', 'wc -c')
  3

  >>> print run('ls -la').stdout.lines
  ['total 20',
   'drwxrwxr-x 3 user user 4096 Dec 20 22:55 .',
   'drwxrwxr-x 5 user user 4096 Dec 20 22:57 ..',
   'drwxrwxr-x 2 user user 4096 Dec 20 22:37 dir',
   '-rw-rw-r-- 1 user user    0 Dec 20 22:52 file']


.. code-block:: python

  from osome import run

  run('grep something', data=run.stdin)

.. code-block:: bash

  $ ps aux | python script.py


tests
-----

.. image:: https://api.travis-ci.org/xando/osome.png?branch=master

Travis CI, https://travis-ci.org/xando/osome


Tests are implemented with `py.tests
<http://pytest.org/>`_, to run:

.. code-block:: bash

   python runtests.py


based on/inspired by
--------------------

* http://www.ruby-doc.org/stdlib-1.9.3/libdoc/fileutils/rdoc/index.html
* https://github.com/kennethreitz/clint
* https://github.com/jaraco/path.py


author
------

* Sebastina Pawluś (sebastian.pawlus@gmail.com)


contributors
------------

* Jakub (kuba.janoszek@gmail.com)
* Angel Ezquerra
