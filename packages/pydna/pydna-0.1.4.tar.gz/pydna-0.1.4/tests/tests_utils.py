#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
utils tests
'''

import unittest

from pydna import eq, sync, shift_origin, read, Dseqrecord
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

class test_empty(unittest.TestCase):

    def test_eq(self):
        ''' test eq'''

        self.assertTrue(  eq( "AAA" ,"TTT", linear   = True ) )
        self.assertTrue(  eq( "AAA" ,"TTT", linear   = False) )

        self.assertTrue(  eq( "aAA" ,"TtT", linear   = True ) )
        self.assertTrue(  eq( "AAa" ,"TtT", linear   = False) )


        self.assertTrue(  eq( "ATA" ,"AAT", circular = True ) )
        self.assertFalse( eq( "ATA" ,"AAT", circular = False) )
        self.assertTrue(  eq( "AAA" ,"AAA", linear   = True ) )
        self.assertTrue(  eq( "AAA" ,"AAA", linear   = False) )

        self.assertTrue(  eq( "ATA" ,Seq("AAT"), circular = True ) )
        self.assertFalse( eq( "ATA" ,Seq("AAT"), circular = False) )
        self.assertTrue(  eq( "AAA" ,Seq("AAA"), linear   = True ) )
        self.assertTrue(  eq( "AAA" ,Seq("AAA"), linear   = False) )

        self.assertTrue(  eq( "ATA" ,SeqRecord("AAT"), circular = True ) )
        self.assertFalse( eq( "ATA" ,SeqRecord("AAT"), circular = False) )
        self.assertTrue(  eq( "AAA" ,SeqRecord("AAA"), linear   = True ) )
        self.assertTrue(  eq( "AAA" ,SeqRecord("AAA"), linear   = False) )

        self.assertTrue(  eq( "ATA" ,Dseqrecord("AAT"), circular = True ) )
        self.assertFalse( eq( "ATA" ,Dseqrecord("AAT"), circular = False) )
        self.assertTrue(  eq( "AAA" ,Dseqrecord("AAA"), linear   = True ) )
        self.assertTrue(  eq( "AAA" ,Dseqrecord("AAA"), linear   = False) )

        self.assertTrue(  eq( Seq("ATA") ,SeqRecord("AAT"), circular = True ) )
        self.assertFalse( eq( Seq("ATA") ,SeqRecord("AAT"), circular = False) )
        self.assertTrue(  eq( Seq("AAA") ,SeqRecord("AAA"), linear   = True ) )
        self.assertTrue(  eq( Seq("AAA") ,SeqRecord("AAA"), linear   = False) )

        self.assertTrue(  eq( Seq("ATA") ,Dseqrecord("AAT"), circular = True ) )
        self.assertFalse( eq( Seq("ATA") ,Dseqrecord("AAT"), circular = False) )
        self.assertTrue(  eq( Seq("AAA") ,Dseqrecord("AAA"), linear   = True ) )
        self.assertTrue(  eq( Seq("AAA") ,Dseqrecord("AAA"), linear   = False) )

        self.assertTrue(  eq( Dseqrecord("AAA",circular=False) ,Dseqrecord("AAA",circular=False)) )
        self.assertTrue(  eq( Dseqrecord("AAA",circular=True)  ,Dseqrecord("AAA",circular=True))   )
        self.assertFalse( eq( Dseqrecord("ATA",circular=False) ,Dseqrecord("AAT",circular=False)) )
        self.assertTrue(  eq( Dseqrecord("ATA",circular=True)  ,Dseqrecord("AAT",circular=True)) )

        self.assertEqual( True , True )
        self.assertTrue( True )
        self.assertFalse( False )

        with self.assertRaises(TypeError):
            1+"1"

        with self.assertRaisesRegexp(TypeError, "unsupported"):
            1+"1"

    def test_shift_origin(self):

        pCAPs   = read("./pCAPs.gb")
        self.assertTrue( pCAPs.circular )
        pCAPs_b = shift_origin(pCAPs, 200)
        self.assertEqual( len(pCAPs), len(pCAPs_b) )
        self.assertTrue( pCAPs_b.circular )
        self.assertTrue( eq(pCAPs, pCAPs_b) )
        pCAPs_b_linear = pCAPs_b.tolinear()
        self.assertTrue( eq(pCAPs, pCAPs_b_linear, circular=True) )
        pCAPs_c = pCAPs[200:]+pCAPs[:200]
        self.assertTrue( eq(pCAPs, pCAPs_c, circular=True) )
        with self.assertRaisesRegexp(ValueError, "shift"):
            pCAPs_b = shift_origin(pCAPs, 20000)



    def test_sync(self):
        from Bio.Seq import reverse_complement

        pcaps = read("./pCAPs.gb")
        self.assertTrue(pcaps.circular == True)
        pcaps2 = sync(pcaps, "tctgacacatgcagctcccggagacggtcac")
        self.assertTrue(pcaps2.circular == True)
        self.assertTrue( pcaps2.seq.watson.lower().startswith("tctgacacatgcagctcccggagacggtcac"))
        pcaps2 = sync(pcaps, "agaaaccattattatcatgacattaacctataaaaa")
        self.assertTrue(   str(pcaps2.seq).lower().startswith("agaaaccattattatcatgacattaacctataaaaa"))
        pcaps2 = sync(pcaps, "tctagacaaaccgtgggacgaattcttaag")
        pcaps3 = sync(pcaps2,"tcgcgcgtttcggtgatgacggtgaaaacc")
        self.assertTrue(  eq(pcaps,pcaps2, pcaps3))
        self.assertFalse( eq(pcaps,pcaps2, linear=True))
        self.assertFalse( eq(pcaps,pcaps2, pcaps3, linear=True))
        self.assertTrue(  eq(pcaps,pcaps3, linear=True))
        plasmid = read("./pCAPs_lowgc.gb")
        plasmid2 = sync(plasmid, pcaps)
        self.assertEqual( str(plasmid2[:10].seq).upper(), "TCGCGCGTTT")

        a=read("./pUC19.gb")

        a=a.synced("cggtgatgacggtgaaaacctctgacacat")

        self.assertEqual(str(a.seq[0:60]), "CGGTGATGACGGTGAAAACCTCTGACACATGCAGCTCCCGGAGACGGTCACAGCTTGTCT")





    def test_copy_features(self):

        from Bio.SeqUtils.CheckSum import seguid
        from pydna import read,copy_features
        a=read("./pCAPs.gb")
        b=read("./pCAPs_fasta.txt")
        b=b.looped()

        for sh in [1,2,3,3127,3128,3129]:
            newb = (b[sh:]+b[:sh]).looped()
            copy_features(a, newb)
            self.assertTrue( sorted([f.extract(a).seq.tostring().lower() for f in a.features if len(f)>10],key=len) == sorted([f.extract(newb).seq.tostring().lower() for f in newb.features],key=len))

        b=b.rc()

        for sh in [1,2,3,3127,3128,3129]:
            newb = b[sh:]+b[:sh]
            copy_features(a, newb)
            self.assertTrue( sorted([f.extract(a).seq.tostring().lower() for f in a.features if len(f)>10],key=len) == sorted([f.extract(newb).seq.tostring().lower() for f in newb.features],key=len))

        seguid_bla = "riT98j2v4NxVS8sbw/Q8epCwQwo"
        seguid_cre = "xLZ2xs2O8CUMmWh2OrhmNFp5ZLg"

        copy_features(a, b)
        assert [seguid(f.extract(b).seq) for f in b.features] == [seguid_cre,seguid_cre,seguid_bla,seguid_bla]

        b=read("./pCAPs_fasta.txt").looped()

        b=sync(b,"attaacgagtgccgtaaacgacgatggttttacc")

        copy_features(a, b)
        assert [seguid(f.extract(b).seq) for f in b.features] == [seguid_cre,seguid_cre,seguid_bla,seguid_bla]

        b=read("./pCAPs_fasta.txt").looped()
        b=sync(b,"ttaacgagtgccgtaaacgacgatggttttacc")

        copy_features(a, b)
        assert [seguid(f.extract(b).seq) for f in b.features] == [seguid_cre,seguid_cre,seguid_bla,seguid_bla]

        b=read("./pCAPs_fasta.txt").looped()
        b=sync(b,"taacgagtgccgtaaacgacgatggttttacc")

        copy_features(a, b)
        assert [seguid(f.extract(b).seq) for f in b.features] == [seguid_bla,seguid_bla]

        b=read("./pCAPs_fasta.txt").looped()
        b=sync(b,"gttaccaatgcttaatcagtgaggcacctatctcagc")

        copy_features(a, b)
        assert [seguid(f.extract(b).seq) for f in b.features] == [seguid_cre,seguid_cre,seguid_bla,seguid_bla]

        b=read("./pCAPs_fasta.txt").looped()
        b=sync(b,"ttaccaatgcttaatcagtgaggcacctatctcagc")

        copy_features(a, b)
        assert [seguid(f.extract(b).seq) for f in b.features] == [seguid_cre,seguid_cre,seguid_bla,seguid_bla]

        b=read("./pCAPs_fasta.txt").looped()
        b=sync(b,"taccaatgcttaatcagtgaggcacctatctcagc")

        copy_features(a, b)
        assert [seguid(f.extract(b).seq) for f in b.features] == [seguid_cre,seguid_cre,]

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity = 1)
    unittest.main(testRunner=runner)