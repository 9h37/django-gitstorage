# -*- coding: utf-8 -*-

import unittest
import os

from gitstorage.StorageBackend import GitStorage
from django.core.files.base import ContentFile


class TestUser(object):
    first_name = u'Gérard'
    last_name = u'Test'
    email = u'gerard.test@example.com'


class TestSearch(unittest.TestCase):

    def setUp(self):
        """
            Create repository, and commit test_é.txt file.
        """

        self.st = GitStorage.create_storage('test-search-git')
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

    def test_search(self):
        """
            Make sure the search works.
        """

        expected = [
            (u'test_é.txt', [u'héhé'])
        ]

        results = self.st.search(u'hé')

        self.assertEqual(expected, results)

    def test_search_no_results(self):
        """
            Make sure we get nothing when there is no match.
        """

        expected = []
        results = self.st.search('test')

        self.assertEqual(expected, results)

    def test_search_exclude(self):
        """
            Make sure the exclude pattern works.
        """

        expected = []
        results = self.st.search(u'hé', exclude=r'^test(.+)')

        self.assertEqual(expected, results)

if __name__ == '__main__':
    unittest.main()
