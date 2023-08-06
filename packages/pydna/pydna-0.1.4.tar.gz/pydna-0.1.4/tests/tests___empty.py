#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
test empty
'''

import unittest

#from pydna import ...

class test_empty(unittest.TestCase):

    def test_empty(self):
        ''' test ....?'''

        self.assertEqual( True , True )
        self.assertTrue( True )
        self.assertFalse( False )

        with self.assertRaises(TypeError):
            1+"1"

        with self.assertRaisesRegexp(TypeError, "unsupported"):
            1+"1"


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity = 1)
    unittest.main(testRunner=runner)









