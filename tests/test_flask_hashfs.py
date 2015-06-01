# -*- coding: utf-8 -*-

import flask
import mock
import os
import pytest

from flask_hashfs import FlaskHashFS


TEST_DIR = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def testdir(tmpdir):
    return tmpdir.mkdir('flask-hashfs')


@pytest.yield_fixture
def app(testdir):
    """Provide instance for basic Flask app."""
    app = flask.Flask(__name__)
    app.config['TESTING'] = True

    # This config value is required and must be supplied.
    app.config['HASHFS_ROOT_FOLDER'] = str(testdir)

    with app.app_context():
        yield app


@pytest.fixture
def fs(app):
    return FlaskHashFS(app)


@pytest.mark.parametrize('file,extension', [
    ('file', None),
    ('file', '.txt')
])
def test_hashfs_put(fs, file, extension):
    with mock.patch('hashfs.HashFS.put') as mocked:
        fs.put(file, extension=extension)

    mocked.assert_called_once_with(file, extension=extension)


def test_hashfs_get(fs):
    with mock.patch('hashfs.HashFS.get') as mocked:
        fs.get('file')

    mocked.assert_called_once_with('file')


@pytest.mark.parametrize('file,mode', [
    ('file', 'rb'),
    ('file', 'r+'),
])
def test_hashfs_open(fs, file, mode):
    with mock.patch('hashfs.HashFS.open') as mocked:
        fs.open(file, mode=mode)

    mocked.assert_called_once_with(file, mode=mode)


def test_hashfs_delete(fs):
    with mock.patch('hashfs.HashFS.delete') as mocked:
        fs.delete('file')

    mocked.assert_called_once_with('file')


@pytest.mark.parametrize('config', [
   {'HASHFS_HOST': None,
    'HASHFS_PATH_PREFIX': '',
    'HASHFS_DEPTH': 4,
    'HASHFS_WIDTH': 1,
    'HASHFS_ALGORITHM': 'sha256'},
])
def test_config_defaults(testdir, config):
    app = flask.Flask(__name__)
    app.config['HASHFS_ROOT_FOLDER'] = str(testdir)
    fs = FlaskHashFS(app)

    for key in config:
        assert app.config[key] == config[key], \
               'Config value "{0}" not equal to expected'.format(key)


@pytest.mark.parametrize('key,value,exception', [
    ('HASHFS_PATH_PREFIX', None, ValueError),
    ('HASHFS_PATH_PREFIX', 'foo', ValueError),
    ('HASHFS_ROOT_FOLDER', None, ValueError),
])
def test_config_missing(app, key, value, exception):
    app.config[key] = value
    with pytest.raises(exception):
        FlaskHashFS(app)


@pytest.mark.parametrize('config,path,external,expected', [
    ({},
     'foo/bar/baz.txt',
     True,
     'http://localhost/foo/bar/baz.txt'),
    ({},
     'foo/bar/baz.txt',
     False,
     '/foo/bar/baz.txt'),
    ({'HASHFS_HOST': 'https://s3.amazon.com/foobar'},
     'qux',
     True,
     'https://s3.amazon.com/foobar/qux'),
    ({'HASHFS_HOST': 'https://s3.amazon.com/foobar'},
     'qux',
     False,
     '/qux'),
    ({'HASHFS_PATH_PREFIX': '/aaa'},
     'foo/bar/baz.txt',
     True,
     'http://localhost/aaa/foo/bar/baz.txt'),
    ({'HASHFS_PATH_PREFIX': '/aaa'},
     'foo/bar/baz.txt',
     False,
     '/aaa/foo/bar/baz.txt'),
    ({'HASHFS_HOST': 'https://s3.amazon.com/foobar',
      'HASHFS_PATH_PREFIX': '/aaa'},
     'qux',
     True,
     'https://s3.amazon.com/foobar/aaa/qux'),
    ({'HASHFS_HOST': 'https://s3.amazon.com/foobar',
      'HASHFS_PATH_PREFIX': '/aaa'},
     'qux',
     False,
     '/aaa/qux'),
])
def test_url_for(app, config, path, external, expected):
    app.config.update(config)
    fs = FlaskHashFS()
    fs.init_app(app)

    with app.test_request_context():
        assert fs.url_for(path, external=external) == expected
