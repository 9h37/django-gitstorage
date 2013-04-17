# -*- coding: utf-8 -*-

from django.core.files.storage import Storage
from django.core.files import File

from pygit2 import Repository, init_repository, Signature
from pygit2 import GIT_STATUS_INDEX_DELETED, GIT_STATUS_INDEX_MODIFIED, GIT_STATUS_INDEX_NEW
from pygit2 import GIT_STATUS_WT_DELETED, GIT_STATUS_WT_MODIFIED, GIT_STATUS_WT_NEW

import os

class GitStorage(Storage):
    """ Git file storage backend """

    def __init__(self, path):
        """ Initialize repository """

        super(GitStorage, self).__init__()

        self.repo = Repository(path)
        self.index = self.repo.index
        self.index.read()

    @classmethod
    def create_storage(cls, path):
        """ Create repository, and return GitStorage object on it """

        repo = init_repository(path)

        return cls(path)

    def commit(self, user, message):
        """ Create a commit """

        # Check the status of the repository
        status = self.repo.status()
        index = self.repo.index
        index.read()

        for filename, flags in status.items():
            # the file was deleted
            if flags in (GIT_STATUS_INDEX_DELETED, GIT_STATUS_WT_DELETED):
                # remove it from the tree
                del index[filename]

            # or the file was modified/added
            elif flags in (GIT_STATUS_INDEX_MODIFIED, GIT_STATUS_INDEX_NEW,
                           GIT_STATUS_WT_MODIFIED, GIT_STATUS_WT_NEW):
                # add it to the tree
                index.add(filename)

        treeid = index.write_tree()

        # Now make the commit

        author = Signature(u'{0} {1}'.format(
            user.first_name,
            user.last_name).encode('utf-8'),
            user.email.encode('utf-8')
        )
        committer = author

        self.repo.create_commit(
            'HEAD',
            author, committer, message,
            treeid,
            [self.repo.head.oid]
        )

        index.write()
        self.index.read()

    # Storage API

    def exists(self, path):
        """
            Returns True if a file referenced by the given name already exists in
            the storage system, or False if the name is available for a new file.
        """

        return path in self.index

    def listdir(self, path=None):
        """
            Lists the contents of the specified path, returning a 2-tuple of
            lists; the first item being directories, the second item being files. 
        """

        abspath = os.path.join(self.repo.workdir, path) if path else self.repo.workdir

        dirs = []
        files = []

        for e in os.listdir(abspath):
            if os.path.isdir(e) and e != '.git':
                dirs.append(e)

            else:
                files.append(e)

        return (dirs, files)

    def open(self, name, mode='rb'):
        """
            Opens the file given by name. Note that although the returned file is
            guaranteed to be a File object, it might actually be some subclass.
        """

        abspath = os.path.join(self.repo.workdir, name)
        dirname = os.path.dirname(abspath)

        if 'w' in mode and not os.path.exists(dirname):
            os.makedirs(dirname)

        return File(open(abspath, mode))

    def path(self, name):
        """
            The local filesystem path where the file can be opened using
            Python’s standard open().
        """

        if not self.exists(name):
            raise IOError, u"{0}: Not found in repository".format(name)

        e = self.index[name]

        return os.path.join(self.repo.workdir, e.path)

    def save(self, name, content):
        """
            Saves a new file using the storage system, preferably with the name
            specified. If there already exists a file with this name name, the
            storage system may modify the filename as necessary to get a unique
            name. The actual name of the stored file will be returned.

            The content argument must be an instance of django.core.files.File
            or of a subclass of File.
        """

        new_name = self.get_available_name(name)
        abspath = os.path.join(self.repo.workdir, new_name)

        dirname = os.path.dirname(abspath)

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(abspath, 'wb') as f:
            for chunk in content.chunks():
                f.write(chunk)

    def delete(self, name):
        """
            Deletes the file referenced by name.
        """

        if not self.exists(name):
            raise IOError, u"{0}: Not found in repository".format(name)

        abspath = os.path.join(self.repo.workdir, name)
        os.remove(abspath)