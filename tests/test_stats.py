# -*- coding: utf-8 -*-

import unittest
import os

from gitstorage.StorageBackend import GitStorage
from django.core.files.base import ContentFile

from datetime import datetime


class TestUser(object):
    first_name = u'Gérard'
    last_name = u'Test'
    email = u'gerard.test@example.com'


class TestStats(unittest.TestCase):

    def setUp(self):
        self.st = GitStorage.create_storage('test-stats-git')
        self.user = TestUser()

        self.f = ContentFile(u'héhé'.encode('utf-8'))
        self.st.save(u'test_é.txt', self.f)
        self.st.commit(self.user, u'test commit é')

        d = datetime.now()
        self.now = datetime(d.year, d.month, d.day, d.hour, d.minute)

    def tearDown(self):
        # remove repository
        for root, dirs, files in os.walk(self.st.repo.workdir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))

            for name in dirs:
                os.rmdir(os.path.join(root, name))

        os.rmdir(self.st.repo.workdir)

    def test_accessed_time(self):
        d = self.st.accessed_time(u'test_é.txt')
        d = datetime(d.year, d.month, d.day, d.hour, d.minute)

        self.assertEqual(self.now, d)

    def test_created_time(self):
        d = self.st.created_time(u'test_é.txt')
        d = datetime(d.year, d.month, d.day, d.hour, d.minute)

        self.assertEqual(self.now, d)

    def test_modified_time(self):
        d = self.st.modified_time(u'test_é.txt')
        d = datetime(d.year, d.month, d.day, d.hour, d.minute)

        self.assertEqual(self.now, d)

    def test_size(self):
        sz = self.st.size(u'test_é.txt')
        self.assertEqual(sz, self.f.size)


if __name__ == '__main__':
    unittest.main()
