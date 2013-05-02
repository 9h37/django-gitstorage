# -*- coding: utf-8 -*-

import unittest
import os

from gitstorage.StorageBackend import GitStorage
from django.core.files.base import ContentFile


class TestUser(object):
    first_name = u'Gérard'
    last_name = u'Test'
    email = u'gerard.test@example.com'


class TestDiff(unittest.TestCase):

    def setUp(self):
        """
            Create repository, and commit test_é.txt file.
        """

        self.st = GitStorage.create_storage('test-diff-git')
        self.user = TestUser()

        # First commit
        f = ContentFile(u'héhé'.encode('utf-8'))
        self.st.save(u'test_é.txt', f)
        self.commit1 = self.st.commit(self.user, u'test commit é')

        # Second commit
        f = ContentFile(u'hèhè'.encode('utf-8'))
        self.st.save(u'test_é.txt', f)
        self.commit2 = self.st.commit(self.user, u'test commit è')

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

    def test_diff(self):
        """
            Make sure the diff is correct.
        """

        d = self.st.diff(self.commit1.oid, self.commit2.oid)

        patch = u"""diff --git a/test_é_1.txt b/test_é_1.txt
new file mode 100644
index 0000000..ffe3c60
--- /dev/null
+++ b/test_é_1.txt
@@ -0,0 +1 @@
+hèhè
\ No newline at end of file
"""

        self.assertEqual(d, patch)

    def test_diffs(self):
        """
            Make sure the method returns correct data.
        """

        c1meta = {
            'msg': u'test commit é',
            'author': u'{0} {1}'.format(self.user.first_name, self.user.last_name),
            'sha': self.commit1.hex
        }

        c2meta = {
            'msg': u'test commit è',
            'author': u'{0} {1}'.format(self.user.first_name, self.user.last_name),
            'sha': self.commit2.hex,
            'parent_sha': self.commit1.hex
        }

        # get diffs
        diffs = self.st.diffs()

        # There is two diffs in the list
        self.assertEqual(len(diffs['diffs']), 2)

        for d in diffs['diffs']:
            d.pop('date')

        # Make sure the metadata are the same
        self.assertEqual(diffs['diffs'][0], c2meta)
        self.assertEqual(diffs['diffs'][1], c1meta)


if __name__ == '__main__':
    unittest.main()
