# -*- coding: utf-8 -*-
"""The flask-hashfs module.

Flask extension for HashFS, a content-addressable file management system.
"""

from flask import current_app, request
from hashfs import HashFS, HashAddress

from .__meta__ import (
    __title__,
    __summary__,
    __url__,
    __version__,
    __author__,
    __email__,
    __license__
)

__all__ = (
    'FlaskHashFS',
    'HashAddress',
)


class FlaskHashFS(object):
    """Flask extension for storing files on file system using hashfs.

    Configuration values:

    ======================  ===================================================
    ``HASHFS_HOST``         Host where files are served.

                            Set if files are served from a different host than
                            application.

                            Defaults to ``None`` which uses
                            ``flask.request.host_url``.
    ``HASHFS_PATH_PREFIX``  URL path prefix where files are served.

                            Defaults to ``''``.
    ``HASHFS_ROOT_FOLDER``  Root folder to save files.

                            Must be set.
    ``HASHFS_DEPTH``        Number of nested folders to use when saving files.

                            Defaults to ``4``.
    ``HASHFS_WIDTH``        Width of each nested subfolder.

                            Defaults to ``1``.
    ``HASHFS_ALGORITHM``    Hashing algorithm to use when computing content
                            hash.

                            Defaults to ``'sha256'``.
    ======================  ===================================================
    """
    _extension_name = 'hashfs'

    def __init__(self, app=None):
        if app is not None:
            self.app = app
            self.init_app(app)
        else:
            self.app = None

    def init_app(self, app):
        # Flask specific config values.
        app.config.setdefault('HASHFS_HOST', None)
        app.config.setdefault('HASHFS_PATH_PREFIX', '')

        # HashFS specific config values.
        app.config.setdefault('HASHFS_ROOT_FOLDER', None)
        app.config.setdefault('HASHFS_DEPTH', 4)
        app.config.setdefault('HASHFS_WIDTH', 1)
        app.config.setdefault('HASHFS_ALGORITHM', 'sha256')

        if app.config['HASHFS_PATH_PREFIX'] is None:
            raise ValueError(
                'Missing configuration value for Flask-HashFS: '
                '"HASHFS_PATH_PREFIX" must be set')

        if (app.config['HASHFS_PATH_PREFIX'] and
                not app.config['HASHFS_PATH_PREFIX'].startswith('/')):
            raise ValueError(
                'Invalid configuration value for Flask-HashFS: '
                '"HASHFS_PATH_PREFIX" must start with a leading slash')

        if not app.config['HASHFS_ROOT_FOLDER']:
            raise ValueError(
                'Missing configuration value for Flask-HashFS: '
                '"HASHFS_ROOT_FOLDER" must be set')

        client = HashFS(app.config['HASHFS_ROOT_FOLDER'],
                        depth=app.config['HASHFS_DEPTH'],
                        width=app.config['HASHFS_WIDTH'],
                        algorithm=app.config['HASHFS_ALGORITHM'])

        app.extensions[self._extension_name] = {
            'client': client
        }

    @property
    def config(self):
        return current_app.config

    @property
    def client(self):
        """Underlying :class:`HashFS` instance."""
        return current_app.extensions[self._extension_name]['client']

    def url_for(self, relpath, external=True):
        """Return URL for path relative to ``HASHFS_ROOT_FOLDER``.

        Args:
            relpath (str): Relative path to ``HASHFS_ROOT_FOLDER`` where file
                is located.
            external (bool): Whether to include host in URL.

        Returns:
            str: URL for path.

        Note:
            This function builds the URL with the assumption that `relpath` is
            a valid file path. It does not check for file existence.
        """
        paths = ['/', self.config['HASHFS_PATH_PREFIX'], relpath]

        if external:
            paths.insert(0, self.config['HASHFS_HOST'] or request.host_url)

        return urljoin(*paths)

    def put(self, file, extension=None):
        """Store contents of `file` on disk using its content hash for the
        address.

        Args:
            file (mixed): Readable object or path to file.
            extension (str, optional): Optional extension to append to file
                when saving.

        Returns:
            HashAddress: File's hash address.
        """
        return self.client.put(file, extension=extension)

    def get(self, file):
        """Return :class:`HashAdress` from given id or path. If `file` does not
        refer to a valid file, then ``None`` is returned.

        Args:
            file (str): Address ID or path of file.

        Returns:
            HashAddress: File's hash address.
        """
        return self.client.get(file)

    def open(self, file, mode='rb'):
        """Return open buffer object from given id or path.

        Args:
            file (str): Address ID or path of file.
            mode (str, optional): Mode to open file in. Defaults to ``'rb'``.

        Returns:
            Buffer: An ``io`` buffer dependent on the `mode`.

        Raises:
            IOError: If file doesn't exist.
        """
        return self.client.open(file, mode=mode)

    def delete(self, file):
        """Delete file using id or path. Remove any empty directories after
        deleting. No exception is raised if file doesn't exist.

        Args:
            file (str): Address ID or path of file.
        """
        self.client.delete(file)


def urljoin(*paths):
    """Join delimited path using specified delimiter.

    >>> assert urljoin('') == ''
    >>> assert urljoin('/') == '/'
    >>> assert urljoin('', '/a') == '/a'
    >>> assert urljoin('a', '/') == 'a/'
    >>> assert urljoin('', '/a', '', '', 'b') == '/a/b'
    >>> ret = '/a/b/c/d/e/'
    >>> assert urljoin('/a/', 'b/', '/c', 'd', 'e/') == ret
    >>> assert urljoin('a', 'b', 'c') == 'a/b/c'
    >>> ret = 'a/b/c/d/e/f'
    >>> assert urljoin('a/b', '/c/d/', '/e/f') == ret
    >>> ret = '/a/b/c/1/'
    >>> assert urljoin('/', 'a', 'b', 'c', '1', '/') == ret
    >>> assert urljoin([]) == ''
    """
    paths = [path for path in paths if path]

    if len(paths) == 1:
        # Special case where there's no need to join anything.
        # Doing this because if paths==['/'], then an extra '/'
        # would be added if the else clause ran instead.
        path = paths[0]
    else:
        leading = '/' if paths and paths[0].startswith('/') else ''
        trailing = '/' if paths and paths[-1].endswith('/') else ''
        middle = '/'.join([path.strip('/')
                           for path in paths if path.strip('/')])
        path = ''.join([leading, middle, trailing])

    return path
