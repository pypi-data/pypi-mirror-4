'''
Created on 02.07.2012

@author: kruis
'''
import unittest


class Test(unittest.TestCase):


    def testDistutils(self):
        import distutils
        reload(distutils)
        self.assertIsInstance(distutils.__version__, basestring)

    def testDistutilsCommand(self):
        from distutils import command
        reload(command)
        self.assertTrue(command.__all__)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()