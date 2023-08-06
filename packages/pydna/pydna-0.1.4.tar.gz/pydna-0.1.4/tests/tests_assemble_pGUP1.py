#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
test pGUP1
'''

import unittest

class test_empty(unittest.TestCase):

    def test_empty(self):
        ''' test pGUP1'''

        import os

        cwd = os.getcwd()

        os.chdir("../docs/cookbook/")

        import pydna

        GUP1rec1sens = pydna.read("./cookbook_files/GUP1rec1sens.txt")
        GUP1rec2AS = pydna.read("./cookbook_files/GUP1rec2AS.txt")
        GUP1_locus = pydna.read("./cookbook_files/GUP1_locus.gb")
        pGREG505 = pydna.read("./cookbook_files/pGREG505.gb")

        insert = pydna.pcr(GUP1rec1sens, GUP1rec2AS, GUP1_locus)

        from Bio.Restriction import SalI

        lin_vect, his3 = pGREG505.cut(SalI)

        fs, cp = pydna.circular_assembly((insert, lin_vect), limit=28)

        pGUP1 = cp.pop()

        pGUP1 = pydna.sync(pGUP1, pGREG505)

        self.assertEqual(pGUP1.seguid(), "42wIByERn2kSe/Exn405RYwhffU")

        os.chdir(cwd)

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity = 1)
    unittest.main(testRunner=runner)









