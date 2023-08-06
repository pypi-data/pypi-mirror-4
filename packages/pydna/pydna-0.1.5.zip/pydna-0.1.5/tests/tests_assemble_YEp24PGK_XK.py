#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
test YEp24PGK_XK
'''

import unittest

class test_empty(unittest.TestCase):

    def test_empty(self):
        ''' test YEp24PGK_XK'''

        import os

        cwd = os.getcwd()

        os.chdir("../docs/cookbook/")

        import pydna


        p1 =   pydna.read("./cookbook_files/primer1.txt", ds = False)
        p3 =   pydna.read("./cookbook_files/primer3.txt", ds = False)
        XKS1 = pydna.read("./cookbook_files/XKS1_orf.txt")

        PCR_prod = pydna.pcr(p1 ,p3 ,XKS1)

        from Bio.Restriction import BamHI

        stuffer1, insert, stuffer2 = PCR_prod.cut(BamHI)

        YEp24PGK = pydna.read("./cookbook_files/YEp24PGK.txt")

        from Bio.Restriction import BglII

        YEp24PGK_BglII = YEp24PGK.cut(BglII).pop()

        YEp24PGK_XK = YEp24PGK_BglII + insert

        YEp24PGK_XK=YEp24PGK_XK.looped()

        YEp24PGK_XK = YEp24PGK_XK.synced(YEp24PGK)

        self.assertEqual( YEp24PGK_XK.seguid() ,"HRVpCEKWcFsKhw/W+25ednUfldI" )

        os.chdir(cwd)

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity = 1)
    unittest.main(testRunner=runner)









