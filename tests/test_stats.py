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
        """
            Create repository, and commit test_é.txt file.
        """

        self.st = GitStorage.create_storage('test-stats-git')
        self.user = TestUser()

        self.f = ContentFile(u'héhé'.encode('utf-8'))
        self.st.save(u'test_é.txt', self.f)
        self.st.commit(self.user, u'test commit é')

        # save current time (without microseconds)
        # the current time is the last accessed time,
        # the last modified time, and the creation time
        # of test_é.txt file.
        d = datetime.now()
        self.now = datetime(d.year, d.month, d.day, d.hour, d.minute)

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

    def test_accessed_time(self):
        """
            Verify that the last accessed time is correct.
        """

        d = self.st.accessed_time(u'test_é.txt')
        d = datetime(d.year, d.month, d.day, d.hour, d.minute)

        self.assertEqual(self.now, d)

    def test_created_time(self):
        """
            Verify that the creation time is correct.
        """

        d = self.st.created_time(u'test_é.txt')
        d = datetime(d.year, d.month, d.day, d.hour, d.minute)

        self.assertEqual(self.now, d)

    def test_modified_time(self):
        """
            Verify that the last modified time is correct.
        """

        d = self.st.modified_time(u'test_é.txt')
        d = datetime(d.year, d.month, d.day, d.hour, d.minute)

        self.assertEqual(self.now, d)

    def test_size(self):
        """
            Test that the file size is correct.
        """

        sz = self.st.size(u'test_é.txt')
        self.assertEqual(sz, self.f.size)


if __name__ == '__main__':
    unittest.main()
