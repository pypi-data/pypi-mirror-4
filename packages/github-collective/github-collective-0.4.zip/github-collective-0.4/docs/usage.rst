
Usage
=====

When ``github-collective`` is installed it should create an executable with
same name in your `bin` directory. 
::

    % bin/github-collective --help
    usage: github-collective [-h] -c CONFIG [-M MAILER] [-C CACHE] -o GITHUB_ORG
                             -u GITHUB_USERNAME -P GITHUB_PASSWORD [-v] [-p]
    
    This tool will let you automate tedious tasks of creating teams granting
    permission and creating repositories.
    
    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG, --config CONFIG
                            path to configuration file (could also be remote
                            location). eg.
                            http://collective.github.com/permissions.cfg (default:
                            None)
      -M MAILER, --mailer MAILER
                            TODO (default: None)
      -C CACHE, --cache CACHE
                            path to file where to cache results from github.
                            (default: None)
      -o GITHUB_ORG, --github-org GITHUB_ORG
                            github organisation. (default: None)
      -u GITHUB_USERNAME, --github-username GITHUB_USERNAME
                            github account username. (default: None)
      -P GITHUB_PASSWORD, --github-password GITHUB_PASSWORD
                            github account password. (default: None)
      -v, --verbose
      -p, --pretend

Locally-stored configuration
----------------------------

::

    % bin/github-collective \
        -c example.cfg \ # path to configuration file
        -o vim-addons \  # organization that we are 
        -u garbas \      # account that has management right for organization
        -P PASSWORD      # account password

Remotely-stored configuration (GitHub)
--------------------------------------

::

    % bin/github-collective \
        -c https://raw.github.com/collective/github-collective/master/example.cfg \
                         # url to configuration file
        -o collective \  # organization that we are 
        -u garbas \      # account that has management right for organization
        -P PASSWORD      # account password

Cached configuration
--------------------

::

    % bin/github-collective \
        -c https://raw.github.com/collective/github-collective/master/example.cfg \
                         # url to configuration file
        -C .cache        # file where store and read cached results from github
        -o collective \  # organization that we are 
        -u garbas \      # account that has management right for organization
        -P PASSWORD      # account password
