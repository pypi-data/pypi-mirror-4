
Testing
=======

``nose`` is utilised for testing and configuration for ``nose`` exists
within the ``setup.cfg`` file within this project.  This configuration
automatically examines files for tests within the project, including
this read-me itself. You can initialise and run tests using the Buildout
configuration provided::

    git clone git://github.com/collective/github-collective.git
    cd github-collective
    virtualenv .
    python boostrap.py
    bin/buildout
    bin/nosetests

`tox <http://tox.testrun.org/latest/>`_ is used to ensure this package
installs correctly under each version of Python.  Currently we test 
Python 2.6 and Python 2.7.  Support for running tests under ``tox`` will
come shortly. To test installation::

    git clone git://github.com/collective/github-collective.git
    cd github-collective
    virtualenv .
    pip install tox
    tox
    

Issues and Contributing
=======================

Report issues via this project's GitHub issue tracker at
https://github.com/collective/github-collective/issues.

Contribute by submitting a pull request on GitHub or else by
adding yourself to the `Collective <http://collective.github.com>`_
and contributing directly.

Todo
====
 
- Allow configuration of organisation settings via API
- Add facility to continue if error experienced
- Send emails to owners about removing repos
- Better logging mechanism (eg. logbook)
- Support configuration extensibility (eg ``extends =`` syntax) for
  using multiple configuration files.


Credits
=======

:Author: `Rok Garbas`_ (garbas)
:Contributor: `David Beitey`_ (davidjb)

.. _`Rok Garbas`: http://www.garbas.si
.. _`David Beitey`: http://davidjb.com
