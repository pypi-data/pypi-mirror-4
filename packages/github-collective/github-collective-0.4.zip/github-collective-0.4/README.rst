Introduction
============

`GitHub organizations`_ are great way for organizations to manage their Git
repositories. This tool will let you automate the tedious tasks of creating
teams, granting permissions, and creating repositories or modifying their
settings.

The approach that the ``github-collective`` tool takes is that you edit a
central configuration (currently an ini-like file) from where options are
read and synchronized to GitHub respectively.

Initially, the purpose of this script was to manage Plone's collective
organization on GitHub: http://collective.github.com. It is currently in use
in several other locations.


.. contents

Documentation
=============

Read the full documentation at http://github-collective.rtfd.org.

Features
========

* Create one central configuration that you can sync to GitHub to configure
  your organisation's settings, repositories, teams, and more.

  * Combine this with GitHub's fork-and-pull request model to easily
    allow non-administrative users to create and manage repositories
    with minimal overhead.

* Repositories: create and modify repositories within an organization

  * Configure all repository properties as per the `GitHub Repos API`_,
    including privacy (public/private), description, and other metadata. 
  * After the initial repository creation happens, updated values in your
    configuration will replace those on GitHub.

* Service hooks: add and modify service hooks for repositories.

  * GitHub repositories have support for sending information upon
    certain events taking place (for instance, pushes being made to a 
    repository or a fork being taken).
  * After the initial repo creation process takes place, updated values in your
    hook configuration will `replace` those on GitHub. 
  * Hooks not present in your configuration (such as those manually added
    on GitHub or those removed from local configuration) will *not* be
    deleted.

* Teams: automatically create teams and modify members

  * Control permissions for teams (for example: push, pull or admin)

* Automatically syncs all of the above with GitHub when the tool is run.

* Buildout-style variable substitution in the form ``${section:option}``.


.. _`GitHub organizations`: https://github.com/blog/674-introducing-organizations
.. _`GitHub Repos API`: http://developer.github.com/v3/repos/#create

