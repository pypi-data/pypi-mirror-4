=====
dy.fi
=====

dy.fi package provides script to keep dynamic IP address fresh for DNS service https://www.dy.fi provides.

Two commands
------------
Two commands will be added to buildout.

- ./bin/dyfi
- ./bin/dyfi-last-updated

Example of dyfi command::

    ./bin/dyfi -u USERACCOUNT -p PASSWORD hostname.com hostname.org

``USERACCOUNT`` and ``PASSWORD`` are same as what you use for https://www.dy.fi/ site log in.

You can pass multiple host names separated with a space,
here they are ``hostname.com`` and ``hostname.org``.

You can check the last updated time of IP address::

    ./bin/dyfi-last-updated
