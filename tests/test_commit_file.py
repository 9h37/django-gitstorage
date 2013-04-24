# -*- coding: utf-8 -*-

import unittest
import os

from gitstorage.StorageBackend import GitStorage, GitFile
from django.core.files.base import ContentFile


class TestUser(object):
    first_name = u'Gérard'
    last_name = u'Test'
    email = u'gerard.test@example.com'


class TestCommitFile(unittest.TestCase):

    def setUp(self):
        self.st = GitStorage.create_storage('test-create-storage-git')
        self.user = TestUser()

    def tearDown(self):
        # remove repository
        for root, dirs, files in os.walk(self.st.repo.workdir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))

            for name in dirs:
                os.rmdir(os.path.join(root, name))

        os.rmdir(self.st.repo.workdir)

    def test_commit_open(self):
        f = self.st.open(u'test_é.txt', 'w')

        self.assertIsInstance(f, GitFile)

        f.write(u'héhé')
        f.close()

        abspath = os.path.join(self.st.repo.workdir, u'test_é.txt')
        self.assertTrue(os.path.exists(abspath))

        self.st.commit(self.user, u'test commit é')

    def test_commit_save(self):
        f = ContentFile(u'héhé'.encode('utf-8'))

        self.st.save(u'test_é.txt', f)

        abspath = os.path.join(self.st.repo.workdir, u'test_é.txt')
        self.assertTrue(os.path.exists(abspath))

        self.st.commit(self.user, u'test commit é')

if __name__ == '__main__':
    unittest.main()
