#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Provides a class for downloading sequences from genbank.


'''
import re
import os
import urllib2
from urlparse import urlparse
from urlparse import urlunparse
from Bio                    import SeqIO
from Bio                    import Entrez
from Bio.Alphabet.IUPAC     import IUPACAmbiguousDNA
from Bio.GenBank            import RecordParser
from Bio.SeqUtils.CheckSum  import seguid

from pydna.dsdna import read

class Genbank():
    '''Class to facilitate download from genbank.

    Parameters
    ----------
    users_email : string
        Has to be a valid email address. You should always tell
        Genbanks who you are, so that they can contact you.
    proxy : string, optional
        String containing a proxy url:
        "proxy = "http://umiho.proxy.com:3128"
    tool : string, optional
        Default is "pydna". This is to tell Genbank which tool you are
        using.

    Example
    -------

    import pydna
    gb=pydna.Genbank("me@mail.se", proxy = "http://proxy.com:3128")
    gb.nucleotide("L09137") <- this method does the downloading from genbank
    SeqRecord(seq=Seq('TCGCGCGTTTCGGTGATGACGGTGAAAACCTCT.....

    '''

    def __init__(self, users_email, proxy = None, tool="pydna"):
        if not re.match("[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}",users_email,re.IGNORECASE):
            raise(ValueError("Not a valid email address!"))
        self.email=users_email #Always tell NCBI who you are

        if proxy:
            parsed = urlparse(proxy)
            scheme = parsed.scheme
            hostname = parsed.hostname
            test = urlunparse((scheme, hostname,'','','','',))
            try:
                response=urllib2.urlopen(test, timeout=1)
            except urllib2.URLError as err:
                print test
                raise(ValueError("could not contact proxy server."))
            self.proxy = urllib2.ProxyHandler({ scheme : parsed.geturl() })
        else:
            os.environ['http_proxy']=''
            self.proxy = urllib2.ProxyHandler()
        self.opener = urllib2.build_opener(self.proxy)
        urllib2.install_opener(self.opener)

    def test(self):
        '''Test downloading the pUC19 plasmid sequence from genbank
       returns True if successful. Can be used to test the proxy
       and other network settings.
       '''
        try:
            result = self.nucleotide("L09137") # pUC19
        except urllib2.URLError:
            return False
        return seguid(result.seq) == "71B4PwSgBZ3htFjJXwHPxtUIPYE"

    def nucleotide(self, item):
        '''Download a genbank record using a Genbank object.

       item is a string containing one genbank acession number [1]
       for a nucleotide file:

       | A12345   = 1 letter  + 5 numerals
       | AB123456 = 2 letters + 6 numerals

       References
       ----------

       .. [1]   http://www.dsimb.inserm.fr/~fuchs/M2BI/AnalSeq/Annexes/Sequences/Accession_Numbers.htm

       '''

        Entrez.email = self.email

        return read(Entrez.efetch(db ="nucleotide",
                                   id = item,
                                   rettype = "gb",
                                   retmode = "text").read())

if __name__=="__main__":
    import doctest
    doctest.testmod()