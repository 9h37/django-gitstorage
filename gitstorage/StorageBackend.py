# -*- coding: utf-8 -*-
"""
.. module:: gitstorage.StorageBackend
    :platform: Unix, Windows
    :synopsis: Django Storage backend built on top of pygit2

.. moduleauthor:: David Delassus <david.delassus@9h37.fr>


"""


from django.core.files.storage import Storage
from django.core.files import File

from pygit2 import Repository, init_repository, Signature, GitError
from pygit2 import GIT_STATUS_INDEX_DELETED, GIT_STATUS_INDEX_MODIFIED, GIT_STATUS_INDEX_NEW
from pygit2 import GIT_STATUS_WT_DELETED, GIT_STATUS_WT_MODIFIED, GIT_STATUS_WT_NEW
from pygit2 import GIT_SORT_TIME

import datetime
import os
import re


class GitFile(File):
    """ Sub-class of File object to handle UTF-8 data. """

    def write(self, data):
        """
            Write UTF-8 data to file.

            :param data: Data to write
            :type data: unicode
        """

        super(GitFile, self).write(data.encode('utf-8'))


class GitStorage(Storage):
    """ Git file storage backend. """

    def __init__(self, path):
        """
            Initialize repository.

            :param path: Absolute path to the existing Git repository.
            :type path: str
        """

        super(GitStorage, self).__init__()

        self.repo = Repository(path)
        self.index = self.repo.index
        self.index.read()

    @classmethod
    def create_storage(cls, path):
        """
            Create repository, and return GitStorage object on it

            :param path: Absolute path to the Git repository to create.
            :type path: str
            :returns: GitStorage
        """

        init_repository(path, False)

        return cls(path)

    def commit(self, user, message):
        """
            Save previous changes in a new commit.

            :param user: The commit author/committer.
            :type user: django.contrib.auth.models.User
            :param message: The commit message.
            :type message: unicode
            :returns: pygit2.Commit
        """

        # Refresh index before committing
        index = self.repo.index
        index.read()

        # Check the status of the repository
        status = self.repo.status()

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

        try:
            parents = [self.repo.head.oid]

        except GitError:
            parents = []

        commit = self.repo.create_commit(
            'refs/heads/master',
            author, committer, message,
            treeid,
            parents
        )

        # Write changes to disk
        index.write()
        # and refresh index.
        self.index.read()

        # Return commit object
        return self.repo[commit]

    def log(self, name=None, limit=10):
        """
            Get history of the repository, or of a file if name is not None.

            :param name: File name within the repository.
            :type name: unicode or None
            :param limit: Maximal number of commits to get (default: 10), use a negative number to get all.
            :type limit: int
            :returns: list of pygit2.Commit
        """

        commits = []

        if not name:
            # Look for `limit` commits
            for commit in self.repo.walk(self.repo.head.oid, GIT_SORT_TIME):
                commits.append(commit)

                limit = limit - 1

                if limit == 0:
                    break

            return commits

        else:
            # For each commits
            for commit in self.repo.walk(self.repo.head.oid, GIT_SORT_TIME):
                # Check the presence of the file in the tree
                try:
                    commit.tree[name]

                    # no error raised, it means the entry exists, so add the
                    # commit to the list
                    commits.append(commit)

                    limit = limit - 1

                    if limit == 0:
                        break

                # If the file is not in the tree, then it raises a KeyError,
                # so, just ignore it.
                except KeyError:
                    pass

        return commits

    def diffs(self, limit=10):
        """
            Get diffs between commits.

            Return the following dict :

                {"diffs": [
                    {
                        "msg": unicode(<commit message>),
                        "date": datetime.fromtimestamp(<commit date>),
                        "author": unicode(<author name>),
                        "sha": unicode(<commit SHA>),
                        "parent_sha": unicode(<parent commit SHA>), # optional
                    },
                    # ...
                ]}

            :param limit: Maximal number of diffs to get (default: 10), use a negative number to get all.
            :type limit: int
            :returns: dict
        """

        commits = self.log(limit=limit)

        diffs = {'diffs': []}

        # For each commit
        for commit in commits:
            # Create a JSON object containing informations about the commit
            diff = {
                'msg': commit.message,
                'date': datetime.datetime.fromtimestamp(commit.commit_time),
                'author': commit.author.name,
                'sha': commit.hex,
            }

            if commit.parents:
                diff['parent_sha'] = commit.parents[0].hex

            # The SHA and parent SHA will be used to get the diff via AJAX.

            diffs['diffs'].append(diff)

        return diffs

    def diff(self, asha, bsha):
        """
            Get diff between two commits.

            :param asha: SHA of commit A.
            :type asha: unicode
            :param bsha: SHA of commit B.
            :type bsha: unicode
            :returns: unicode
        """

        c1 = self.repo[asha]
        c2 = self.repo[bsha]

        d = c1.tree.diff(c2.tree)

        return d.patch.decode('utf-8')

    def search(self, pattern, exclude=None):
        """
            Search pattern in GIT repository.

            :param pattern: Pattern to search.
            :type pattern: unicode
            :param exclude: Exclude some files from the search results
            :type exclude: regex
            :returns: list of tuple containing the filename and the list of matched lines.
        """

        entries = []

        self.index.read()

        # For each files in the index
        for ientry in self.index:
            # If the filename match the exclude_file regex, then ignore it
            if exclude and re.match(exclude, ientry.path.decode('utf-8')):
                continue

            # Get the associated blob
            blob = self.repo[ientry.oid]

            # Create entry
            entry = (ientry.path.decode('utf-8'), [])

            # Add matched lines to the entry
            for line in blob.data.decode('utf-8').splitlines():
                if pattern in line:
                    entry[1].append(line)

            # If the entry has no matched lines, then ignore
            if entry[1]:
                entries.append(entry)

        return entries

    # Storage API

    def accessed_time(self, name):
        """
            Get last accessed time of a file.

            :param name: File name within the repository.
            :type name: unicode
            :returns: datetime
            :raises: IOError
        """

        if not self.exists(name):
            raise IOError(u"{0}: Not found in repository".format(name))

        abspath = os.path.join(self.repo.workdir, name)
        stats = os.stat(abspath)

        return datetime.datetime.fromtimestamp(stats.st_atime)

    def created_time(self, name):
        """
            Get creation time of a file.

            :param name: File name within the repository.
            :type name: unicode
            :returns: datetime
            :raises: IOError
        """

        if not self.exists(name):
            raise IOError(u"{0}: Not found in repository".format(name))

        abspath = os.path.join(self.repo.workdir, name)
        stats = os.stat(abspath)

        return datetime.datetime.fromtimestamp(stats.st_ctime)

    def modified_time(self, name):
        """
            Get last modified time of a file.

            :param name: File name within the repository.
            :type name: unicode
            :returns: datetime
            :raises: IOError
        """

        if not self.exists(name):
            raise IOError(u"{0}: Not found in repository".format(name))

        abspath = os.path.join(self.repo.workdir, name)
        stats = os.stat(abspath)

        return datetime.datetime.fromtimestamp(stats.st_mtime)

    def size(self, name):
        """
            Get file's size.

            :param name: File name within the repository.
            :type name: unicode
            :returns: int
            :raises: IOError
        """

        if not self.exists(name):
            raise IOError(u"{0}: Not found in repository".format(name))

        e = self.index[name]
        blob = self.repo[e.oid]

        return blob.size

    def exists(self, path):
        """
            Check if ``path`` exists in the Git repository.

            :param path: Path within the repository of the file to check.
            :type param: unicode
            :returns: True if the file exists, False if the name is available for a new file.
        """

        return path in self.index

    def listdir(self, path=None):
        """
            Lists the contents of the specified path.

            :param path: Path of the directory to list (or None to list the root).
            :type path: unicode or None
            :returns: a 2-tuple of lists; the first item being directories, the second item being files.
        """

        abspath = os.path.join(self.repo.workdir, path) if path else self.repo.workdir

        dirs = []
        files = []

        for e in os.listdir(abspath):
            entry_fullpath = os.path.join(abspath, e)

            if os.path.isdir(entry_fullpath):
                if e != '.git':
                    dirs.append(e.decode('utf-8'))

            else:
                files.append(e.decode('utf-8'))

        return (dirs, files)

    def open(self, name, mode='rb'):
        """
            Opens the file given by name.

            :param name: Name of the file to open.
            :type name: unicode
            :param mode: Flags for openning the file (see builtin ``open`` function).
            :type mode: str
            :returns: GitFile
        """

        abspath = os.path.join(self.repo.workdir, name)
        dirname = os.path.dirname(abspath)

        if 'w' in mode and not os.path.exists(dirname):
            os.makedirs(dirname)

        return GitFile(open(abspath, mode))

    def path(self, name):
        """
            Return the absolute path of the file ``name`` within the repository.

            :param name: Name of the file within the repository.
            :type name: unicode
            :returns: str
            :raises: IOError
        """

        if not self.exists(name):
            raise IOError(u"{0}: Not found in repository".format(name))

        e = self.index[name]

        return os.path.join(self.repo.workdir, e.path).decode('utf-8')

    def save(self, name, content):
        """
            Saves a new file using the storage system, preferably with the name
            specified. If there already exists a file with this name, the
            storage system may modify the filename as necessary to get a unique
            name. The actual name of the stored file will be returned.

            :param name: Name of the new file within the repository.
            :type name: unicode
            :param content: Content to save.
            :type content: django.core.files.File
            :returns: str
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

            :param name: Name of the file within the repository to delete
            :type name: unicode
            :raises: IOError
        """

        if not self.exists(name):
            raise IOError(u"{0}: Not found in repository".format(name))

        abspath = os.path.join(self.repo.workdir, name)
        os.remove(abspath)
