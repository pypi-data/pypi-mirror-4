Radpress
========
Radpress is a simple blogging application for Djangonauts. It uses
`restructuredtext`_ format for articles and pages.

Installation
------------
You can install **radpress** ``pip`` or ``easy_install``. If you want to
fork and develop the project, create a virtual environment and install it
with::

    python setup.py install


Development
-----------
After you cloned the repository, enter the directory and create a virtual
environment::

    virtualenv -p /usr/local/bin/python venv --no-site-packages
    source venv/bin/activate

Then, install requirements for development with this command::

    pip install -r requirements.txt

Synchronize database and run server::

    cd demo
    python manage.py syncdb --migrate
    python manage.py runserver

Authors
-------
Gökmen Görgen, <gokmen[@]radity.com>

.. _restructuredtext: http://docutils.sourceforge.net/rst.html
