# -*- coding: utf-8 -*-
import unittest

import os
import time

import  sphinxcontrib.recentpages as target
from util import *


class TestRecentpages(unittest.TestCase):

    def setUp(self):
        atime = mtime = time.mktime((2012, 11, 1, 1, 1, 1, 0, 0, -1))
        os.utime((test_root / 'file2.rst'), (atime, mtime))
        atime = mtime = time.mktime((2012, 11, 2, 1, 1, 1, 0, 0, -1))
        os.utime((test_root / 'file1.rst'), (atime, mtime))
        atime = mtime = time.mktime((2012, 11, 3, 1, 1, 1, 0, 0, -1))
        os.utime((test_root / 'index.rst'), (atime, mtime))
        atime = mtime = time.mktime((2012, 11, 4, 1, 1, 1, 0, 0, -1))
        os.utime((test_root / 'file3.rst'), (atime, mtime))

    def tearDown(self):
        (test_root / '_build').rmtree(True)

    def test_get_file_list_ordered_by_mtime(self):
        app = TestApp(buildername='html')
        app.build(force_all=True, filenames=[])
        env = app.builder.env
        res = target.get_file_list_ordered_by_mtime(env)

        self.assertEqual([
            ('file3', 1351958461.0, u'file 3'),
            ('index', 1351872061.0,
             u"Welcome to sphinxcontrib-recentpages's documentation!"),
            ('file1', 1351785661.0, u'file 1'),
            ('file2', 1351699261.0, u'file 2'),
        ], res)

if __name__ == '__main__':
    unittest.main()
