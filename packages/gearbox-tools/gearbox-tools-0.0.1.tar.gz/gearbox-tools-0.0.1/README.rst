About gearboxtools
-------------------------

gearboxtools is a bunch of commands for the
`TurboGears GearBox <https://github.com/TurboGears/gearbox>`_ tool.

Installing
-------------------------------

gearboxtools can be installed from pypi::

    easy_install gearboxtools

or::

    pip install gearboxtools

should just work for most of the users

Provided Commands
--------------------------------

pkgdeps
==================

Provided and installed application as argument will return the list of direct and indirect depencies used
by the application::

    $ gearbox pkgdeps turbogears2
    +--------------+
    | Package      |
    +--------------+
    | Beaker       |
    | repoze.lru   |
    | PasteDeploy  |
    | MarkupSafe   |
    | crank>=0.6.2 |
    | WebOb>=1.2   |
    | decorator    |
    +--------------+

tg-bootstrap
==================

When ran inside a newly quickstarted TurboGears2 application will adapt the application to work with
the SCSS version of bootstrap css framework.

This command will add the ``tgext.scss``  dependency loaded through ``tgext.pluggable``, will create
a bootstrap directory inside the project ``public_dir`` with the Twitter bootstrap framework inside and will
patch the ``master template`` to use the SCSS version instead of the plain CSS one provided by default.


tg-hgignore
==================

This will create a ``.hgignore`` file suitable for TurboGears2 applications inside the directory where it
is started.

deploy-circus
==================

When started inside a ``PasteDeploy`` application directory will generate a configuration for
Mozilla Circus to deploy that application under circus supervision.