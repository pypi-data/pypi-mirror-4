#!/usr/bin/env python

from secobj import *
import unittest , os , glob

class TestSequenceFunctions(unittest.TestCase):
    def setUp(self):
        self.key = 'spam and eggs'
        self.enc = EncObject(self.key)
        self.filename = '/tmp/secobj.test'
        self.obj = [1 , 2 , 3 , 4]

    def test_file_obj_encrypt(self):
        fh = open(self.filename , 'wb')
        self.enc.encryptToFile(self.obj , fh)
        fh.close()
        fh = open(self.filename , 'rb')
        obj = self.enc.decryptFromFile(fh , True)
        self.assertEqual(self.obj , obj)
        fh.close()

    def test_filename_encrypt(self):
        self.enc.encryptToFile(self.obj , self.filename)
        obj = self.enc.decryptFromFile(self.filename , True)
        self.assertEqual(self.obj , obj)

    def test_string_encrypt(self):
        encStr , iv = self.enc.encryptToStr(self.obj)
        obj = self.enc.decryptFromStr(encStr , iv)
        self.assertEqual(self.obj , obj)

    def tearDown(self):
        for f in glob.glob('./*.pyc'):
            try:
                os.unlink(f)
            except:
                pass

if __name__ == '__main__':
    unittest.main()
