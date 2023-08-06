#!/usr/bin/env python

import unittest
import shutil
import os.path

from file_distribution import FileDistribution

__author__ =  'Adam Kubica (caffecoder) <caffecoder@kaizen-step.com>'

class TestFileDistribution(unittest.TestCase):
    def setUp(self):
        if not os.path.exists("/tmp/storage"):
            os.makedirs("/tmp/storage")

        self.fd = FileDistribution("/tmp/storage//")

    def testPath(self):
        self.assertEqual(self.fd.get_path(), "/tmp/storage")

    def testCase1(self):
        self.fd.set_extension("tmp")
        self.fd.set_extension(".dat")
        self.fd.hex_path(102423)
        self.assertEqual(self.fd.get_path(), "/tmp/storage/01/90/17.dat")

    def testCase2(self):
        self.fd.set_extension("dat")
        self.fd.hex_path(256)
        self.assertEqual(self.fd.get_path(), "/tmp/storage/01/00.dat")

    def testCase3(self):
        self.fd.set_extension("")
        self.fd.hex_path(256)
        self.assertEqual(self.fd.get_path(), "/tmp/storage/01/00")

    def testcase4(self):
        self.fd.hex_path(1)
        self.assertEqual(self.fd.get_path(), "/tmp/storage/01.dat")

    def testCase5(self):
        f = open('/tmp/test.txt', 'w')
        f.close()

        self.assertTrue(os.path.exists("/tmp/test.txt"))

        self.fd.set_extension(".dat")
        self.fd.hex_path(256)

        self.fd.rename_from("/tmp/test.txt")
        self.assertTrue(os.path.exists("/tmp/storage/01/00.dat"))

    def testCase6(self):
        f = open('/tmp/test1.txt', 'w')
        f.close()

        f = open('/tmp/test2.txt', 'w')
        f.close()

        self.assertTrue(os.path.exists("/tmp/test1.txt"))
        self.assertTrue(os.path.exists("/tmp/test2.txt"))

        self.fd.set_extension(".dat")

        self.fd.hex_path(1)
        self.fd.rename_from("/tmp/test1.txt")
        self.assertTrue(os.path.exists("/tmp/storage/01.dat"))

        self.fd.hex_path(256)
        self.fd.rename_from("/tmp/test2.txt")
        self.assertTrue(os.path.exists("/tmp/storage/01/00.dat"))

    def tearDown(self):
        if os.path.exists("/tmp/storage"):
            shutil.rmtree("/tmp/storage")

if __name__ == '__main__':
    unittest.main()
