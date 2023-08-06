========
Kanedama
========

|SekienKanedama| Kanedama uses Ghost.py to save Heroku invoices as images and will also email them to you.

Why? Because Heroku doesn't provide any "hard copy" of your invoices, and logging in to the web UI just to screenshot them is boring.

.. |SekienKanedama| image:: http://upload.wikimedia.org/wikipedia/commons/2/2a/SekienKanedama.jpg
    :height: 200px


Installation
============

In order for Ghost.py to work, you'll need to install either PySide or PyQt. For me, that's::

    % sudo apt-get install python-pyside

Then you can ``sudo pip install kanedama``.


Configuration
=============

You need to create a ``config.ini`` file that contains your Heroku API key (see
config.example.ini_ to get started).

.. _config.example.ini: https://github.com/jimr/Kanedama/blob/master/config.example.ini

By default, we check for ``$HOME/.config/kanedama/config.ini``, so it's best to
keep your config there.

Alternatively, you can just provide the API key via the ``--key`` argument.


Automation
==========

Stick something like this in your crontab::

    01 1    25 * *  your_username /usr/bin/python /usr/local/bin/kanedama.py --email=you@example.com
