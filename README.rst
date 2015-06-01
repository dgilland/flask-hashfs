************
Flask-HashFS
************

|version| |travis| |coveralls| |license|


Flask extension for `HashFS <https://github.com/dgilland/hashfs>`_, a content-addressable file management system.


What is HashFS?
===============

HashFS is a content-addressable file management system. What does that mean? Simply, that HashFS manages a directory where files are saved based on the file's hash.

Typical use cases for this kind of system are ones where:

- Files are written once and never change (e.g. image storage).
- It's desirable to have no duplicate files (e.g. user uploads).
- File metadata is stored elsewhere (e.g. in a database).


What is Flask-HashFS?
=====================

Flask-HashFS is a Flask extension that integrates HashFS into the Flask ecosystem.


Links
=====

- Project: https://github.com/dgilland/flask-hashfs
- Documentation: http://flask-hashfs.readthedocs.org
- PyPI: https://pypi.python.org/pypi/flask-hashfs/
- TravisCI: https://travis-ci.org/dgilland/flask-hashfs


Quickstart
==========

Install using pip:


::

    pip install Flask-HashFS


Initialization
--------------

.. code-block:: python

    from flask import Flask
    from flask_hashfs import FlaskHashFS

    app = Flask(__name__)
    fs = FlaskHashFS()


Configure ``Flask-HashFS`` to store files in ``/var/www/data/uploads`` and give them a route prefix at ``/uploads``.


.. code-block:: python

    app.config.update({
        'HASHFS_HOST': None,
        'HASHFS_PATH_PREFIX': '/uploads',
        'HASHFS_ROOT_FOLDER': '/var/www/data/uploads',
        'HASHFS_DEPTH': 4,
        'HASHFS_WIDTH': 1,
        'HASHFS_ALGORITHM': 'sha256'
    })

    fs.init_app(app)


Usage
-----

Use Flask-HashFS to manage files using HashFS.


.. code-block:: python

    with app.app_context():
        # Store readable objects or file paths
        address = fs.put(io_obj, extension='.jpg')


        # Get a file's hash address
        assert fs.get(address.id) == address
        assert fs.get(address.relpath) == address
        assert fs.get(address.abspath) == address
        assert fs.get('invalid') is None


        # Get a BufferedReader handler
        fileio = fs.open(address.id)

        # Or using the full path...
        fileio = fs.open(address.abspath)

        # Or using a path relative to fs.root
        fileio = fs.open(address.relpath)


        # Delete a file by address ID or path
        fs.delete(address.id)
        fs.delete(address.abspath)
        fs.delete(address.relpath)


For direct access to the HashFS instance, use the ``client`` attribute.


.. code-block:: python

    fs.client
    assert isinstance(fs.client, flask_hashfs.HashFS)


Generate URLs for HashFS content.


.. code-block:: python

    with app.test_request_context():
        fs.url_for('relative/file/path')


For more details, please see the full documentation at http://flask-hashfs.readthedocs.org and http://hashfs.readthedocs.org.



.. |version| image:: http://img.shields.io/pypi/v/flask-hashfs.svg?style=flat-square
    :target: https://pypi.python.org/pypi/flask-hashfs/

.. |travis| image:: http://img.shields.io/travis/dgilland/flask-hashfs/master.svg?style=flat-square
    :target: https://travis-ci.org/dgilland/flask-hashfs

.. |coveralls| image:: http://img.shields.io/coveralls/dgilland/flask-hashfs/master.svg?style=flat-square
    :target: https://coveralls.io/r/dgilland/flask-hashfs

.. |license| image:: http://img.shields.io/pypi/l/flask-hashfs.svg?style=flat-square
    :target: https://pypi.python.org/pypi/flask-hashfs/
