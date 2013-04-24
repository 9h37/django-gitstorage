# -*- coding: utf-8 -*-

import unittest
import os

from gitstorage.StorageBackend import GitStorage
from django.core.files.base import ContentFile


class TestUser(object):
    first_name = u'Gérard'
    last_name = u'Test'
    email = u'gerard.test@example.com'


class TestLog(unittest.TestCase):

    def setUp(self):
        """
            Create repository, and commit test_é.txt file.
        """

        self.st = GitStorage.create_storage('test-log-git')
        self.user = TestUser()

        f = ContentFile(u'héhé'.encode('utf-8'))
        self.st.save(u'test_é.txt', f)
        self.commit = self.st.commit(self.user, u'test commit é')

    def tearDown(self):
        """
            Remove repository.
        """

        for root, dirs, files in os.walk(self.st.repo.workdir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))

            for name in dirs:
                os.rmdir(os.path.join(root, name))

        os.rmdir(self.st.repo.workdir)

    def test_commit_log(self):
        """
            Verify that the commit log of the repository is correct.
        """

        real_commits = [self.commit.hex]
        commits = [commit.hex for commit in self.st.log()]

        self.assertEqual(commits, real_commits)

    def test_commit_log_for_file(self):
        """
            Verify that the commit log of the file test_é.txt is correct.
        """

        real_commits = [self.commit.hex]
        commits = [commit.hex for commit in self.st.log(name=u'test_é.txt')]

        self.assertEqual(commits, real_commits)

    def test_commit_log_limit(self):
        """
            Test the limit parameter.
        """

        commits = self.st.log(limit=1)

        self.assertEqual(len(commits), 1)

if __name__ == '__main__':
    unittest.main()
