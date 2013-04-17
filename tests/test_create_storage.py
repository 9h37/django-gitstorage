# -*- coding: utf-8 -*-

import unittest
import os

from gitstorage.StorageBackend import GitStorage


class TestCreateStorage(unittest.TestCase):

    def tearDown(self):
        # remove repository
        for root, dirs, files in os.walk('test-create-storage-git', topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))

            for name in dirs:
                os.rmdir(os.path.join(root, name))

        os.rmdir('test-create-storage-git')

    def test_create_repository(self):
        r = GitStorage.create_storage('test-create-storage-git')

        self.assertIsNotNone(r.repo.workdir)
        self.assertTrue(os.path.exists(r.repo.workdir))

        r2 = GitStorage('test-create-storage-git')

        self.assertIsNotNone(r2.repo.workdir)
        self.assertTrue(os.path.exists(r2.repo.workdir))
        self.assertEqual(r.repo.workdir, r2.repo.workdir)

if __name__ == '__main__':
    unittest.main()
