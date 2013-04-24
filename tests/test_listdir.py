# -*- coding: utf-8 -*-

import unittest
import os

from gitstorage.StorageBackend import GitStorage
from django.core.files.base import ContentFile


class TestUser(object):
    first_name = u'Gérard'
    last_name = u'Test'
    email = u'gerard.test@example.com'


class TestListdir(unittest.TestCase):

    def setUp(self):
        self.st = GitStorage.create_storage('test-listdir-git')
        self.user = TestUser()

        f = ContentFile(u'héhé'.encode('utf-8'))
        self.st.save(u'test_é.txt', f)
        self.st.commit(self.user, u'test commit é')

    def tearDown(self):
        # remove repository
        for root, dirs, files in os.walk(self.st.repo.workdir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))

            for name in dirs:
                os.rmdir(os.path.join(root, name))

        os.rmdir(self.st.repo.workdir)

    def test_listdir(self):
        listdir = (
            [],  # directories
            [u'test_é.txt'],
        )

        self.assertEqual(listdir, self.st.listdir())


if __name__ == '__main__':
    unittest.main()
