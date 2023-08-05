Installation
------------

You may list ``dy.fi`` to ``buildout.cfg`` or ``setup.py`` of your own package.

zc.buildout
===========

Use ``zc.buildout`` by adding ``dy.fi`` to the list of eggs::

    [buildout]
    ...
    eggs =
        ...
        dy.fi

Dependency to your own package
==============================

You may also list to ``install_requires`` to ``setup.py`` within your package::

    setup(
        ...
        install_requires=[
            ...
            'dy.fi',
            ...
        ],
        ...
    )