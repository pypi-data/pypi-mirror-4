import unittest
import os
import shutil

from manager import RefManager, Manager
from im_exception import *

from __init__ import FIXTURES



class TestReferenceManager(unittest.TestCase):

    folder = 'fake_fixtures'

    @classmethod
    def setUpClass(cls):

        if os.path.isdir(cls.folder):
            shutil.rmtree(cls.folder)
        
        os.mkdir(cls.folder)

    @classmethod
    def tearDownClass(cls):
        if os.path.isdir(cls.folder):
            shutil.rmtree(cls.folder)

    @classmethod
    def copy_local_reference(cls):
        f = os.path.join(FIXTURES, 'local_references.json')
        t = os.path.join(cls.folder, 'local_references.json')
        shutil.copy(f,t)


    def test_001_create_reference_manager(self):

        """ Test for loading a reference file that doesn  exist """

        self.assertRaises(ReferenceFileError, RefManager, self.folder)

    def test_002_create_reference_manager(self):
        self.copy_local_reference()
        rm = RefManager(self.folder)


class TestManager(unittest.TestCase):
    
    folder = 'fake_fixtures'

    @classmethod
    def setUpClass(cls):

        if os.path.isdir(cls.folder):
            shutil.rmtree(cls.folder)
        
        os.mkdir(cls.folder)

    @classmethod
    def tearDownClass(cls):
        if os.path.isdir(cls.folder):
            shutil.rmtree(cls.folder)

    @classmethod
    def copy_local_reference(cls):
        f = os.path.join(FIXTURES, 'local_references.json')
        t = os.path.join(cls.folder, 'local_references.json')
        shutil.copy(f,t)


    def test_001_create_manager(self):
        self.assertRaises(ReferenceFileError, Manager, self.folder)
        self.copy_local_reference()
        m = Manager(self.folder)



if __name__ == '__main__':
    unittest.main()