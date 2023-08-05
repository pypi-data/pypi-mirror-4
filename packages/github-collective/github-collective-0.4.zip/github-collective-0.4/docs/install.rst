
How to install
==============

This package can be installed in a traditional sense or otherwise deployed
using Buildout.

Installation
------------

:Tested with: `Python2.6`_
:Dependencies: `argparse`_, `requests`_

::

    % pip install github-collective
    (or)
    % easy_install github-collective

Deploy with Buildout
--------------------

An example configuration for deployment with buildout could look like this::

    [buildout]
    parts = github-collective

    [settings]
    config = github.cfg
    organization = my-organization
    admin-user = my-admin-user
    password = SECRET
    cache = my-organization.cache

    [github-collective]
    recipe = zc.recipe.egg
    initialization = sys.argv.extend('--verbose -C ${settings:cache} -c ${settings:config} -o ${settings:organization} -u ${settings:admin-user} -P ${settings:password}'.split(' '))
    eggs =
        github-collective

Deploying in this manner will result in ``bin/github-collective`` being
generated with the relevant options already provided.  This means that
something calling this script need not provide provide arguments, making its
usage easier to manage.

.. _`Python2.6`: http://www.python.org/download/releases/2.6/
.. _`argparse`: http://pypi.python.org/pypi/argparse
.. _`requests`: http://python-requests.org
