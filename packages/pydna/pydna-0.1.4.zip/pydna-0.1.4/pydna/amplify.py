#!/usr/bin/env python
# -*- coding: utf-8 -*-
# doctest: +NORMALIZE_WHITESPACE
'''This module provides functions for PCR.

Primers with 5' tails as well as inverse PCR on
circular templates are handled correctly.

'''


import datetime
import itertools
import math
import re
import string
import sys
import textwrap
import collections
import warnings
import copy

from StringIO                       import StringIO
from Bio.SeqUtils.CheckSum          import seguid
from math                           import log10
from math                           import log
from Bio                            import SeqIO
from Bio.Seq                        import Seq
from Bio.Seq                        import reverse_complement
from Bio.Alphabet.IUPAC             import unambiguous_dna
from Bio.Alphabet.IUPAC             import ambiguous_dna
from Bio.SeqRecord                  import SeqRecord
from Bio.SeqUtils                   import GC
from Bio.SeqUtils.MeltingTemp       import Tm_staluc
from Bio.SeqFeature                 import SeqFeature
from Bio.SeqFeature                 import FeatureLocation
from Bio.SeqFeature                 import ExactPosition
from Bio.SeqRecord                  import SeqRecord
from pydna.dsdna                    import Dseq, Dseqrecord, rc, parse

def _annealing_positions(primer, template, limit=15):
    '''Finds the annealing position(s) for primer on template where the
    primer anneals with at least limit nucleotides in the 3' part.
    start is a position (integer)
    footprint1 and tail1 are strings.

    ::

        <------------- start ---->
     5'-...gctactacacacgtactgactgcctccaagatagagtcagtaaccacactcgat...3'
           ||||||||||||||||||||||||||||||||||||||||||||||||
                                  3'-gttctatctcagtcattggtgtATAGTG-5'

                                                        <tail>
                                     <---footprint----->
                                     <--------- primer ------>

    Parameters
    ----------
    primer : string
        The primer sequence 5'-3'

    template : string
        The template sequence 5'-3'

    limit : int = 15, optional
        footprint needs to be at least of length limit.

    Returns
    -------
    describe : list of tuples (int, string, string)
        [ (start1, footprint1, tail1), (start2, footprint2, tail2),..., ]

    '''

    if len(primer)<limit:
        return []
    prc = rc(primer)
    head = prc[:limit]
    positions = [m.start() for m in re.finditer('(?={0})'.format(head), template, re.I)]
    if positions:
        tail = prc[limit:]
        length = len(tail)
        revtail = tail[::-1]
        results = []
        for match_start in positions:
            tm = template[match_start+limit:match_start+limit+length]
            footprint = rc(template[match_start:match_start+limit]+"".join([b for a,b in itertools.takewhile(lambda x: x[0].lower()==x[1].lower(),zip(tail, tm))]))
            results.append((match_start, footprint, primer[: len(primer) - len(footprint) ]))
        return results
    return []

class Amplicon:
    '''Holds information about a PCR reaction involving two
    primers and one template. This class is used by the
    Anneal class and is not meant to be instantiated directly.

    Parameters
    ----------
    forward_primer : SeqRecord(Biopython)
        SeqRecord object holding the forward (sense) primer

    reverse_primer : SeqRecord(Biopython)
        SeqRecord object holding the reverse (antisense) primer

    template : Dseqrecord
        Dseqrecord object holding the template (circular or linear)

    saltc : float, optional
        saltc = monovalent cations (mM) (Na,K..)
        default value is 50mM
        This is used for Tm calculations.

    fc : float, optional
        primer concentration (nM)
        default set to 1000nM = 1µM
        This is used for Tm calculations.

    rc : float, optional
        primer concentration (nM)
        default set to 1000nM = 1µM
        This is used for Tm calculations.

    '''

    def __init__(self,
                  forward_primer,
                  reverse_primer,
                  template,
                  saltc=50,
                  fc=1000,
                  rc=1000):

        self.forward_primer             = forward_primer
        self.reverse_primer             = reverse_primer
        self.fc                         = fc
        self.rc                         = rc
        self.saltc                      = saltc
        self.template                   = template
        self.product                    = None

    def __repr__(self):
        '''returns a short string representation of the object
       '''
        return "Amplicon({})".format(self.__len__())

    def __len__(self):
        '''returns the lenght of the PCR product
       '''
        length  = len(self.forward_primer.primer)
        length += len(self.reverse_primer.primer)
        if self.reverse_primer.pos>self.forward_primer.pos:
            length += abs(self.reverse_primer.pos-self.forward_primer.pos)
        else:
            length += len(self.template)-abs(self.reverse_primer.pos-self.forward_primer.pos)
        return length

    def pcr_product(self):
        '''Returns the PCR product as a Dseqrecord object.
       Primers are marked as SeqFeatures(Biopython)
       associated with the sequence.

       '''
        if self.product:
            return self.product

        begin = self.forward_primer.pos
        end   = self.reverse_primer.pos

        if self.template.circular:
            tmpl=Dseqrecord(Dseq(self.template.seq.watson,self.template.seq.crick, ovhg=0, linear = True))
            tmpl.features = self.template.features
            tmpl=tmpl+tmpl
            if begin>end:
                end=end+len(self.template)
        else:
            tmpl=self.template

        self.product = ( Dseqrecord(self.forward_primer.primer) +
                         tmpl[begin:end] +
                         Dseqrecord(self.reverse_primer.primer.reverse_complement()) )

        features = tmpl[begin-len(self.forward_primer.footprint):end+len(self.reverse_primer.footprint)].features

        self.product.features = [f._shift(len(self.forward_primer.tail)) for f in features]

        # description = Genbank LOCUS max 16 chars

        length = len(self.product)

        self.product.name = "{0}bp_PCR_prod".format(length)[:16]
        self.product.id = "{0}bp {1}".format( str(length)[:14],self.product.seguid() )
        self.product.description="Primers {0} {1}".format( self.forward_primer.primer.name,
                                                  self.reverse_primer.primer.name)

        self.product.features.append(SeqFeature(FeatureLocation(0,len(self.forward_primer.primer)),
                                       type ="primer_bind",strand = 1,
                                       qualifiers = {"note":self.forward_primer.primer.name}))
        self.product.features.append(SeqFeature(FeatureLocation(length - len(self.reverse_primer.primer),length),
                                       type ="primer_bind",
                                       strand = -1,
                                       qualifiers = {"note":self.reverse_primer.primer.name}))

        return self.product

    def flankup(self,flankuplength=50):
        '''Returns a Dseqrecord object containing flankuplength bases upstream of the forward primer footprint,
       Truncated if the template is not long enough.

       ::

        <--- flankup --->

                  5TAATAAactactgactatct3
                         ||||||||||||||
        acgcattcagctactgtactactgactatctatcg

       '''
        return self.template.seq[self.forward_primer.pos-flankuplength-len(self.forward_primer.footprint):self.forward_primer.pos-len(self.forward_primer.footprint)]

    def flankdn(self,flankdnlength=50):
        '''Returns a Dseqrecord object containing flankdnlength bases downstream of the reverse primer footprint.
       Truncated if the template is not long enough.

       ::

                                       <---- flankdn ------>

                        3actactgactatctTAATAA5
                         ||||||||||||||
        acgcattcagctactgtactactgactatctatcgtacatgtactatcgtat

       '''
        return self.template.seq[self.reverse_primer.pos+len(self.reverse_primer.footprint):self.reverse_primer.pos+flankdnlength+len(self.reverse_primer.footprint)]

    def _tm(self):
        '''Tm calculations according to SantaLucia 1998
       Four variables are set.

       '''
        self.tmf = Tm_staluc(str(self.forward_primer.footprint),dnac=50, saltc=self.saltc)
        self.tmr = Tm_staluc(str(self.reverse_primer.footprint),dnac=50, saltc=self.saltc)
        '''
       Ta calculation for enzymes with dsDNA binding domains (dbd)
       like Pfu-Sso7d, Phusion or Phire
       https://www.finnzymes.fi/tm_determination.html

       '''
        self.tmf_dbd = tmbresluc(str(self.forward_primer.footprint),primerc=self.fc)
        self.tmr_dbd = tmbresluc(str(self.reverse_primer.footprint),primerc=self.rc)

    def detailed_figure(self):
        '''::

        5gctactacacacgtactgactg3
         |||||||||||||||||||||| tm 52.6 (dbd) 58.3
        5gctactacacacgtactgactg...caagatagagtcagtaaccaca3
        3cgatgatgtgtgcatgactgac...gttctatctcagtcattggtgt5
                                  |||||||||||||||||||||| tm 49.1 (dbd) 57.7
                                 3gttctatctcagtcattggtgt5


       Returns
       -------
       figure:string
            A string containing a text representation of the primers
            annealing on the template.


       Notes
       -----
       tm is the melting temperature (Tm) calculated according to
       SantaLucia 1998 [1] for each primer.

       (dbd) is Tm calculation for enzymes with dsDNA binding domains
       like Pfu-Sso7d [2]. See [3] for more information.

       References
       ----------

       .. [1] J. SantaLucia, “A Unified View of Polymer, Dumbbell, and Oligonucleotide DNA Nearest-neighbor Thermodynamics,” Proceedings of the National Academy of Sciences 95, no. 4 (1998): 1460.
       .. [2] M. Nørholm, “A Mutant Pfu DNA Polymerase Designed for Advanced Uracil-excision DNA Engineering,” BMC Biotechnology 10, no. 1 (2010): 21, doi:10.1186/1472-6750-10-21.
       .. [3] http://www.thermoscientificbio.com/webtools/tmc/

       '''

        self._tm()
        f =   '''
            {sp1}5{faz}...{raz}3
             {sp3}{rap} tm {tmr} (dbd) {tmr_dbd}
            {sp3}3{rp}5
            5{fp}3
             {fap:>{fplength}} tm {tmf} (dbd) {tmf_dbd}
            {sp2}3{fzc}...{rzc}5
            '''.format( fp       = self.forward_primer.primer.seq,
                        fap      = "|"*len(self.forward_primer.footprint),
                        fplength = len(self.forward_primer.primer.seq),
                        tmf      = round(self.tmf,1),
                        tmr      = round(self.tmr,1),
                        tmf_dbd  = round(self.tmf_dbd,1),
                        tmr_dbd  = round(self.tmr_dbd,1),
                        rp       = self.reverse_primer.primer.seq[::-1],
                        rap      = "|"*len(self.reverse_primer.footprint),
                        rplength = len(self.reverse_primer.primer.seq),
                        faz      = self.forward_primer.footprint,
                        raz      = self.reverse_primer.footprint.reverse_complement(),
                        fzc      = self.forward_primer.footprint.complement(),
                        rzc      = self.reverse_primer.footprint[::-1],
                        sp1       = " "*(len(self.forward_primer.primer.seq)-len(self.forward_primer.footprint)),
                        sp2       = " "*(len(self.forward_primer.primer.seq)-len(self.forward_primer.footprint)),
                        sp3      = " "*(3+len(self.forward_primer.primer.seq))
                       )
        return textwrap.dedent(f).strip("\n")



    def pcr_program(self):
        '''Returns a string containing a text representation of two proposed
       PCR programs. The first program is adapted for Taq poymerase, while
       the second is adapted for Pfu-Sso7d.

       ::

        Taq (rate 30 nt/s)
        Three-step|         30 cycles     |      |SantaLucia 1998
        94.0°C    |94.0°C                 |      |SaltC 50mM
        __________|_____          72.0°C  |72.0°C|
        04min00s  |30s  \         ________|______|
                  |      \ 46.0°C/ 0min 1s|10min |
                  |       \_____/         |      |
                  |         30s           |      |4-8°C

        Pfu-Sso7d (rate 15s/kb)
        Three-step|          30 cycles   |      |Breslauer1986,SantaLucia1998
        98.0°C    |98.0°C                |      |SaltC 50mM
        __________|_____          72.0°C |72.0°C|Primer1C   1µM
        00min30s  |10s  \ 61.0°C ________|______|Primer2C   1µM
                  |      \______/ 0min 0s|10min |
                  |        10s           |      |4-8°C

       '''
        self._tm()
        if not self.product:
            self.pcr_product()
        # Ta calculation according to
        # Rychlik, Spencer, and Rhoads, 1990, Optimization of the anneal
        # ing temperature for DNA amplification in vitro
        # http://www.ncbi.nlm.nih.gov/pubmed/2003928
        GC_prod=GC(str(self.product.seq))
        tml = min(self.tmf,self.tmr)
        #print GC(str(self.product.seq)), self.saltc/1000.0, len(self.product)
        tmp = 81.5 + 0.41*GC(str(self.product.seq)) + 16.6*log10(self.saltc/1000.0) - 675/len(self.product)
        ta = 0.3*tml+0.7*tmp-14.9
        # Fermentas recombinant taq
        taq_extension_rate = 30  # seconds/kB PCR product length
        extension_time_taq = taq_extension_rate * len(self.product) / 1000 # seconds
        f  = textwrap.dedent(u'''
                                Taq (rate {rate} nt/s)
                                Three-step|         30 cycles     |      |SantaLucia 1998
                                94.0°C    |94.0°C                 |      |SaltC {saltc:2}mM
                                __________|_____          72.0°C  |72.0°C|
                                04min00s  |30s  \         ________|______|
                                          |      \ {ta}°C/{0:2}min{1:2}s|10min |
                                          |       \_____/         |      |
                                          |         30s           |      |4-8°C
                             '''.format(rate    = taq_extension_rate,
                                        ta      = math.ceil(ta),
                                        saltc   = self.saltc,
                                        *divmod(extension_time_taq,60)))

        PfuSso7d_extension_rate = 15 #seconds/kB PCR product
        extension_time_PfuSso7d = PfuSso7d_extension_rate * len(self.product) / 1000  # seconds

        # Ta calculation for enzymes with dsDNA binding domains like Pfu-Sso7d
        # https://www.finnzymes.fi/tm_determination.html

        length_of_f = len(self.forward_primer.footprint)
        length_of_r = len(self.reverse_primer.footprint)

        if (length_of_f>20 and length_of_r>20 and self.tmf_dbd>=69.0 and self.tmr_dbd>=69.0) or (self.tmf_dbd>=72.0 and self.tmr_dbd>=72.0):
            f+=textwrap.dedent( u'''
                                    Pfu-Sso7d (rate {rate}s/kb)
                                    Two-step|    30 cycles |      |Breslauer1986,SantaLucia1998
                                    98.0°C  |98.0C         |      |SaltC {saltc:2}mM
                                    _____ __|_____         |      |Primer1C {fc:3}µM
                                    00min30s|10s  \  72.0°C|72.0°C|Primer2C {rc:3}µM
                                            |      \_______|______|
                                            |      {0:2}min{1:2}s|10min |4-8°C
                                 '''.format(rate = PfuSso7d_extension_rate,
                                            fc = self.fc,
                                            rc = self.rc,
                                            saltc = self.saltc,
                                            *divmod(extension_time_PfuSso7d,60)))
        else:

            if (length_of_f>20 and length_of_r>20):
                ta = min(self.tmf_dbd,self.tmr_dbd)+3
            else:
                ta = min(self.tmf_dbd,self.tmr_dbd)


            f+=textwrap.dedent( u'''
                                    Pfu-Sso7d (rate {rate}s/kb)
                                    Three-step|          30 cycles   |      |Breslauer1986,SantaLucia1998
                                    98.0°C    |98.0°C                |      |SaltC {saltc:2}mM
                                    __________|_____          72.0°C |72.0°C|Primer1C {fc:3}µM
                                    00min30s  |10s  \ {ta}°C ________|______|Primer2C {rc:3}µM
                                              |      \______/{0:2}min{1:2}s|10min |
                                              |        10s           |      |4-8°C
                                 '''.format(rate = PfuSso7d_extension_rate,
                                            ta   = math.ceil(ta),
                                            fc   = self.fc/1000,
                                            rc   = self.rc/1000,
                                            saltc= self.saltc,
                                            *divmod(extension_time_PfuSso7d,60)))
        return f



class Anneal:
    '''
    Parameters
    ----------
    primers : iterable containing SeqRecord objects
        Primer sequences 5'-3'.

    template : Dseqrecord object
        The template sequence 5'-3'.

    homology_limit : int, optional
        limit length of the annealing part of the primers.

    max_product_size: int, optional
        PCR products longer than max_product_size are not reported

    Attributes
    ----------
    amplicons : list of Amplicon objects.
        A list of Amplicon objects, one for each primer pair that may
        form a PCR product.


    Examples
    --------

    >>> import pydna
    >>> template = pydna.Dseqrecord("tacactcaccgtctatcattatctactatcgactgtatcatctgatagcac")
    >>> from Bio.SeqRecord import SeqRecord
    >>> p1=pydna.read(">p1\\ntacactcaccgtctatcattatc", ds = False)
    >>> p2 = pydna.read(">p1\\ncgactgtatcatctgatagcac", ds = False).reverse_complement()
    >>> pydna.Anneal((p1,p2), template)
    Anneal(amplicons = 1)
    >>> pydna.Anneal((p1,p2), template).amplicons
    [Amplicon(51)]
    >>> amplicon_list = pydna.Anneal((p1,p2), template).amplicons
    >>> amplicon = amplicon_list.pop()
    >>> amplicon
    Amplicon(51)
    >>> print amplicon.detailed_figure()
    5tacactcaccgtctatcattatc...cgactgtatcatctgatagcac3
                               |||||||||||||||||||||| tm 50.6 (dbd) 60.5
                              3gctgacatagtagactatcgtg5
    5tacactcaccgtctatcattatc3
     ||||||||||||||||||||||| tm 49.4 (dbd) 58.8
    3atgtgagtggcagatagtaatag...gctgacatagtagactatcgtg5
    >>> prod = amplicon.pcr_product()
    >>> prod.annotations['date'] = '02-FEB-2013'
    >>> print prod
    Dseqrecord
    circular: False
    size: 51
    ID: 51bp U96+TO06Y6pFs74SQx8M1IVTBiY
    Name: 51bp_PCR_prod
    Description: Primers p1 <unknown name>
    Number of features: 2
    /date=02-FEB-2013
    Dseq(-51)
    tacactcaccgtctatcatt...actgtatcatctgatagcac
    atgtgagtggcagatagtaa...tgacatagtagactatcgtg
    >>>

    '''
    def __init__(self,
                  primers,
                  template,
                  homology_limit=13,
                  max_product_size=15000):

        self.homology_limit = homology_limit

        primers=[p for p in primers if p.seq]

        self.template = Dseqrecord(template)

        primer = collections.namedtuple("primer","primer pos footprint tail")

        self.fwd_primers = []
        self.rev_primers = []
        self.amplicons   = []

        twl = len(self.template.seq.watson)
        tcl = len(self.template.seq.crick)

        if self.template.linear:
            tw = self.template.seq.watson
            tc = self.template.seq.crick
        else:
            tw = self.template.seq.watson+template.seq.watson
            tc = self.template.seq.crick+template.seq.crick

        for p in primers:
            self.fwd_primers.extend((primer(p,
                                            tcl-pos - min(self.template.seq.ovhg, 0),
                                            Seq(fp), Seq(tl))
                                    for pos, fp, tl in _annealing_positions(
                                                        str(p.seq),
                                                        tc,
                                                        homology_limit) if pos<tcl))
            self.rev_primers.extend((primer(p,
                                            pos + max(0, self.template.seq.ovhg),
                                            Seq(fp), Seq(tl))
                                     for pos, fp, tl in _annealing_positions(
                                                        str(p.seq),
                                                        tw,
                                                        homology_limit) if pos<twl))

        for fp in self.fwd_primers:
            for rp in self.rev_primers:
                tail_lengths = len(fp.tail)+len(rp.tail)
                if (rp.pos >= fp.pos ):
                    self.amplicons.append(Amplicon(fp, rp, self.template))
                elif self.template.circular and fp.pos > rp.pos and len(template)-fp.pos-rp.pos < max_product_size:
                    self.amplicons.append(Amplicon(fp, rp, self.template))

    def report(self):
        '''This method is an alias of str(Annealobj).
        Returns a short string representation.
       '''
        return self.__str__()

    def __repr__(self):
        ''' return a short string represenation '''
        return "Anneal(amplicons = {})".format(len(self.amplicons))

    def __str__(self):
        '''return a short report describing if or where primer
       anneal on the template.
       '''
        mystring = "Template {name} {size} nt {top}:\n".format(name=self.template.name,
                                                                    size=len(self.template),
                                                                    top={True:"circular",
                                                                         False:"linear"}[self.template.circular]
                                                                    )
        if self.fwd_primers:
            for p in self.fwd_primers:
                mystring += "Primer {name} anneals at position {pos}\n".format(name=p.primer.name, pos=p.pos)
        else:
            mystring += "No forward primers anneal...\n"
        if self.rev_primers:
            for p in self.rev_primers:
                mystring += "Primer {name} anneals reverse at position {pos}\n".format(name=p.primer.name, pos=p.pos)
        else:
             mystring += "No reverse primers anneal...\n"
        return mystring.strip()

    def products(self):
        ''' returns all pcr product as a list of Dseqrecords '''
        return [a.product for a in self.amplicons]

    def featured_template(self):
        '''returns the template Dseqrecord object with the footprint of all
       annealing primers marked as SeqFeatures.

       '''
        template = self.template
        for primer in self.fwd_primers:
            if primer.pos-len(primer.footprint)>0:
                start = primer.pos-len(primer.footprint)
                end = primer.pos
                template.features.append(SeqFeature(FeatureLocation(start,end+1),type ="primer_bind",strand = 1, qualifiers = {"note":fp.name,"ApEinfo_fwdcolor":"green","ApEinfo_revcolor":"red"}))
            else:
                start = len(template)-len(primer.footprint)+primer.pos
                end = start+len(primer.footprint)-len(template)

                suba = SeqFeature( FeatureLocation(start,len(template)),
                                   type ="primer_bind",
                                   strand = 1,
                                   qualifiers = {"note":primer.primer.name} )

                subb = SeqFeature( FeatureLocation(0,end),
                                   type ="primer_bind",
                                   strand = 1,
                                   qualifiers = {"note":primer.primer.name})

                template.features.append(SeqFeature(FeatureLocation(start,end),
                                                    type ="primer_bind",
                                                    sub_features = [suba,subb],
                                                    location_operator= "join",
                                                    strand = 1,
                                                    qualifiers = {"note":primer.primer.name}))
        for primer in self.rev_primers:
            if primer.pos+len(primer.footprint)<=len(template):
                start = primer.pos
                end = primer.pos + len(footprint)
                template.features.append(SeqFeature(FeatureLocation(start-1,end),type ="primer_bind",strand = -1, qualifiers = {"note":rp.name,"ApEinfo_fwdcolor":"green","ApEinfo_revcolor":"red"}))
            else:
                start = primer.pos
                end = primer.pos+len(primer.footprint)-len(template)
                suba = SeqFeature(FeatureLocation(start,len(template)),
                                  type ="primer_bind",
                                  strand = -1,
                                  qualifiers = {"note":primer.primer.name})
                subb = SeqFeature(FeatureLocation(0,end),
                                  type ="primer_bind",
                                  strand = -1,
                                  qualifiers = {"note":primer.primer.name,})
                template.features.append(SeqFeature(FeatureLocation(start,end),
                                                    type ="primer_bind",
                                                    sub_features = [suba,subb],
                                                    location_operator= "join",
                                                    strand = -1,
                                                    qualifiers = {"note":primer.primer.name}))
        return template


def pcr(*args,**kwargs):
    '''pcr is a convenience function for Anneal to simplify its usage,
    especially from the command line. If more than one PCR product is
    formed, an exception is raised.

    args is any iterable of sequences or an iterable of iterables of sequences.
    args will be greedily flattened.

    Parameters
    ----------

    args : iterable containing sequence objects
        Several arguments are also accepted.

    limit : int = 13, optional
        limit length of the annealing part of the primers.

    Notes
    -----

    sequences in args could be of type:

    string
    Seq
    SeqRecord
    Dseqrecord

    The last sequence will be interpreted as the template
    all preceeding sequences as primers.

    This is a powerful function, use with care!

    Returns
    -------

    product : Dseqrecord
        a Dseqrecord object representing the PCR product.
        The direction of the PCR product will be the same as
        for the template sequence.

    Examples
    --------

    >>> import pydna
    >>> template = pydna.Dseqrecord("tacactcaccgtctatcattatctactatcgactgtatcatctgatagcac")
    >>> from Bio.SeqRecord import SeqRecord
    >>> p1 = pydna.read(">p1\\ntacactcaccgtctatcattatc", ds = False)
    >>> p2 = pydna.read(">p1\\ncgactgtatcatctgatagcac", ds = False).reverse_complement()
    >>> pydna.pcr(p1, p2, template)
    Dseqrecord(-51)
    >>> pydna.pcr([p1, p2], template)
    Dseqrecord(-51)
    >>> pydna.pcr((p1,p2,), template)
    Dseqrecord(-51)
    >>>

    '''

    import itertools
    from Bio.SeqRecord import SeqRecord
    # flatten args
    output = []
    stack = []
    stack.extend(reversed(args))
    while stack:
        top = stack.pop()
        if hasattr(top, "__iter__") and not isinstance(top, SeqRecord):
            stack.extend(reversed(top))
        else:
            output.append(top)
    new=[]

    for s in output:
        if isinstance(s, Seq):
            s = SeqRecord(s)
        elif isinstance(s, SeqRecord):
            pass
        elif hasattr(s, "watson"):
            s=s.watson
        elif isinstance(s, basestring):
            s = SeqRecord(Seq(s))
        else:
            raise TypeError("the record property needs to be a string, a Seq object or a SeqRecord object")
        new.append(s)

    anneal_primers = Anneal(new[:-1],
                            new[-1],
                            **kwargs)
    if anneal_primers:
        if len(anneal_primers.amplicons) == 1:
            return anneal_primers.amplicons.pop().pcr_product()
        elif len(anneal_primers.amplicons) == 0:
            raise Exception("No PCR products! {}".format(anneal_primers.report()))
        else:
            raise Exception("PCR not specific! {}".format(anneal_primers.report()))
    else:
        raise Exception(anneal_primers.report())
    return


def basictm(primer):
    '''Returns the melting temperature (Tm) of the primer using
    the basic formula.

    | Tm = (wA+xT)*2 + (yG+zC)*4 assumed 50mM monovalent cations
    |
    | w = number of A in primer
    | x = number of T in primer
    | y = number of G in primer
    | z = number of C in primer

    Parameters
    ----------
    primer : string
        Primer sequence 5'-3'

    Returns
    -------
    tm : int

    Examples
    --------
    >>> from pydna.amplify import basictm
    >>> basictm("ggatcc")
    20
    >>>

    '''
    primer = str(primer).lower()
    return (primer.count("a") + primer.count("t"))*2 + (primer.count("g") + primer.count("c"))*4

# http://www.promega.com/techserv/tools/biomath/calc11.htm#melt_results

def tmstaluc98(primer,dnac=50,saltc=50):
    '''Returns the melting temperature (Tm) of the primer using
    the nearest neighbour algorithm. Formula and thermodynamic data
    is taken from SantaLucia 1998. This implementation gives the same
    answer as the one provided by Biopython (See Examples).

    Thermodynamic data used:

    =====  ====  ====
    pair   dH    dS
    =====  ====  ====
    AA/TT  7.9   22.2
    AT/TA  7.2   20.4
    TA/AT  7.2   21.3
    CA/GT  8.5   22.7
    GT/CA  8.4   22.4
    CT/GA  7.8   21.0
    GA/CT  8.2   22.2
    CG/GC  10.6  27.2
    GC/CG  9.8   24.4
    GG/CC  8.0   19.9
    =====  ====  ====

    Parameters
    ----------
    primer : string
        Primer sequence 5'-3' in UPPERCASE

    Returns
    -------
    tm : float
        tm of the primer


    References
    ----------
    .. [1] J. SantaLucia, “A Unified View of Polymer, Dumbbell, and Oligonucleotide DNA Nearest-neighbor Thermodynamics,” Proceedings of the National Academy of Sciences 95, no. 4 (1998): 1460.

    Examples
    --------

    >>> from pydna.amplify import tmstaluc98
    >>> from Bio.SeqUtils.MeltingTemp import Tm_staluc
    >>> tmstaluc98("ACGTCATCGACACTATCATCGAC")
    54.55597724052518
    >>> Tm_staluc("ACGTCATCGACACTATCATCGAC")
    54.555977240525124
    >>>



    '''

    nntermsl={  "AA": (7.9  , 22.2),
                "TT": (7.9  , 22.2),
                "AT": (7.2  , 20.4),
                "TA": (7.2  , 21.3),
                "CA": (8.5  , 22.7),
                "TG": (8.5  , 22.7),
                "GT": (8.4  , 22.4),
                "AC": (8.4  , 22.4),
                "CT": (7.8  , 21.0),
                "AG": (7.8  , 21.0),
                "GA": (8.2  , 22.2),
                "TC": (8.2  , 22.2),
                "CG": (10.6 , 27.2),
                "GC": (9.8  , 24.4),
                "GG": (8    , 19.9),
                "CC": (8    , 19.9),
                "A" : (0    , 0   ),
                "C" : (0    , 0   ),
                "G" : (0    , 0   ),
                "T" : (0    , 0   )  }

    helixinit = {   "G": (-0.1 ,2.8),
                    "C": (-0.1 ,2.8),
                    "A": (-2.3, -4.1),
                    "T": (-2.3, -4.1) }

    dH, dS = helixinit[primer[0]]
    H ,  S = helixinit[primer[-1]]
    dH = dH+H
    dS = dS+S

    for p in range(len(primer)):
        dn = primer[p:p+2]
        H,S = nntermsl[dn]
        dH+=H
        dS+=S
    R = 1.987 # universal gas constant in Cal/degrees C*Mol
    k = (dnac/4.0)*1e-9
    dS = dS-0.368*(len(primer)-1)*math.log(saltc/1e3)
    tm = ((1000* (-dH))/(-dS+(R * (math.log(k)))))-273.15
    return tm

def tmbreslauer86(primer,dnac=500.0,saltc=50.0,thermodynamics=False):
    '''Returns the melting temperature (Tm) of the primer using
    the nearest neighbour algorithm. Formula and thermodynamic data
    is taken from Breslauer 1986. These data are no longer widely used.


    Breslauer 1986, table 2 [1]

    =====  ===== ====   ===
    pair   dH    dS     dG
    =====  ===== ====   ===
    AA/TT  9.1   24.0   1.9
    AT/TA  8.6   23.9   1.5
    TA/AT  6.0   16.9   0.9
    CA/GT  5.8   12.9   1.9
    GT/CA  6.5   17.3   1.3
    CT/GA  7.8   20.8   1.6
    GA/CT  5.6   13.5   1.6
    CG/GC  11.9  27.8   3.6
    GC/CG  11.1  26.7   3.1
    GG/CC  11.0  26.6   3.1
    =====  ===== ====   ===

    Parameters
    ----------
    primer : string
        Primer sequence 5'-3' in UPPERCASE

    Returns
    -------
    tm : float


    References
    ----------
    .. [1] K.J. Breslauer et al., “Predicting DNA Duplex Stability from the Base Sequence,” Proceedings of the National Academy of Sciences 83, no. 11 (1986): 3746.


    Examples
    ---------

    >>> from pydna.amplify import tmbreslauer86
    >>> tmbreslauer86("ACGTCATCGACACTATCATCGAC")
    64.28863985851899







    '''

    nntermbr={  "AA": (9.1   ,24.0   ,1.9),
                "TT": (9.1   ,24.0   ,1.9),
                "AT": (8.6   ,23.9   ,1.5),
                "TA": (6.0   ,16.9   ,0.9),
                "CA": (5.8   ,12.9   ,1.9),
                "TG": (5.8   ,12.9   ,1.9),
                "GT": (6.5   ,17.3   ,1.3),
                "AC": (6.5   ,17.3   ,1.3),
                "CT": (7.8   ,20.8   ,1.6),
                "AG": (7.8   ,20.8   ,1.6),
                "GA": (5.6   ,13.5   ,1.6),
                "TC": (5.6   ,13.5   ,1.6),
                "CG": (11.9  ,27.8   ,3.6),
                "GC": (11.1  ,26.7   ,3.1),
                "GG": (11.0  ,26.6   ,3.1),
                "CC": (11.0  ,26.6   ,3.1),
                "A" : (0     , 0     ,0),
                "C" : (0     , 0     ,0),
                "G" : (0     , 0     ,0),
                "T" : (0     , 0     ,0),     }
    dH=3.4
    dS=12.4
    dG=0
    for p in range(len(primer)):
        dn = primer[p:p+2]
        H,S,G = nntermbr[dn]
        dG+=G
        dH+=H
        dS+=S

    R = 1.9872          # universal gas constant in Cal/degrees C*Mol
    k = dnac*1E-9/2.0
    dH = dH - 5
    dS = dS-0.368*(len(primer)-1)*math.log(saltc/1E3) # SantaLucia salt correction formula
    tm = 1000 * -dH /(-dS + R * math.log(k) )  - 273.15 # degrees Celsius

    if thermodynamics:
        return tm,dH,dS
    else:
        return tm


def tmbresluc(primer, primerc=500.0, saltc=50.0, thermodynamics=False):
    '''Returns the tm for a primer using a formula adapted to polymerases
    with a DNA binding domain.

    Parameters
    ----------

    primer : string
        primer sequence 5'-3'

    primerc : float
       concentration (nM)

    saltc : float, optional
       Monovalent cation concentration (mM)

    thermodynamics : bool, optional
        prints details of the thermodynamic data to stdout. For
        debugging only.

    Returns
    -------
    tm : float
        the tm of the primer

    tm,dH,dS : tuple
        tm and dH and dS used for the calculation

    '''

    import collections

    dHBr = collections.defaultdict(dict)
    dSBr = collections.defaultdict(dict)

    dHBr[0][0] = -9100
    dSBr[0][0] = -24
    dHBr[0][1] = -7633.3000000000002
    dSBr[0][1] = -20.699999999999999
    dHBr[0][2] = -6500
    dSBr[0][2] = -17.300000000000001
    dHBr[0][3] = -8500
    dSBr[0][3] = -22.899999999999999
    dHBr[0][6] = -7800
    dSBr[0][6] = -20.800000000000001
    dHBr[0][7] = -8066.6999999999998
    dSBr[0][7] = -21.699999999999999
    dHBr[0][10] = -8200
    dSBr[0][10] = -22.399999999999999
    dHBr[0][12] = -7800
    dSBr[0][12] = -20.699999999999999
    dHBr[0][13] = -8000
    dSBr[0][13] = -21.5
    dHBr[0][17] = -8450
    dSBr[0][17] = -22.399999999999999
    dHBr[0][18] = -7150
    dSBr[0][18] = -19.100000000000001
    dHBr[0][19] = -8600
    dSBr[0][19] = -23.899999999999999
    dHBr[0][21] = -7800
    dSBr[0][21] = -20.699999999999999
    dHBr[0][22] = -8850
    dSBr[0][22] = -24
    dHBr[0][23] = -8000
    dSBr[0][23] = -21.5
    dHBr[0][24] = -7550
    dSBr[0][24] = -20.600000000000001
    dHBr[1][0] = -5800
    dSBr[1][0] = -14.4
    dHBr[1][1] = -8866.7000000000007
    dSBr[1][1] = -21.800000000000001
    dHBr[1][2] = -9233.2999999999993
    dSBr[1][2] = -22.300000000000001
    dHBr[1][3] = -7722.1999999999998
    dSBr[1][3] = -19.199999999999999
    dHBr[1][6] = -9566.7000000000007
    dSBr[1][6] = -22.399999999999999
    dHBr[1][7] = -7611.1000000000004
    dSBr[1][7] = -19.100000000000001
    dHBr[1][10] = -8683.2999999999993
    dSBr[1][10] = -21.600000000000001
    dHBr[1][12] = -7516.6999999999998
    dSBr[1][12] = -18.399999999999999
    dHBr[1][13] = -8100
    dSBr[1][13] = -20
    dHBr[1][17] = -7683.3000000000002
    dSBr[1][17] = -18.399999999999999
    dHBr[1][18] = -9400
    dSBr[1][18] = -22.399999999999999
    dHBr[1][19] = -7800
    dSBr[1][19] = -20.699999999999999
    dHBr[1][21] = -8200
    dSBr[1][21] = -19.699999999999999
    dHBr[1][22] = -6800
    dSBr[1][22] = -17.600000000000001
    dHBr[1][23] = -8100
    dSBr[1][23] = -20
    dHBr[1][24] = -8516.7000000000007
    dSBr[1][24] = -21.5
    dHBr[2][0] = -5800
    dSBr[2][0] = -12.9
    dHBr[2][1] = -10233.299999999999
    dSBr[2][1] = -25.100000000000001
    dHBr[2][2] = -11000
    dSBr[2][2] = -26.600000000000001
    dHBr[2][3] = -8500
    dSBr[2][3] = -20.5
    dHBr[2][6] = -11900
    dSBr[2][6] = -27.800000000000001
    dHBr[2][7] = -8200
    dSBr[2][7] = -20.100000000000001
    dHBr[2][10] = -9850
    dSBr[2][10] = -24.300000000000001
    dHBr[2][12] = -8400
    dSBr[2][12] = -19.800000000000001
    dHBr[2][13] = -9125
    dSBr[2][13] = -22
    dHBr[2][17] = -8850
    dSBr[2][17] = -20.399999999999999
    dHBr[2][18] = -11450
    dSBr[2][18] = -27.199999999999999
    dHBr[2][19] = -7800
    dSBr[2][19] = -20.800000000000001
    dHBr[2][21] = -9566.7000000000007
    dSBr[2][21] = -22.399999999999999
    dHBr[2][22] = -6800
    dSBr[2][22] = -16.899999999999999
    dHBr[2][23] = -9125
    dSBr[2][23] = -22
    dHBr[2][24] = -9400
    dSBr[2][24] = -23.699999999999999
    dHBr[3][0] = -6900
    dSBr[3][0] = -18.100000000000001
    dHBr[3][1] = -8000
    dSBr[3][1] = -20.300000000000001
    dHBr[3][2] = -7733.3000000000002
    dSBr[3][2] = -19.199999999999999
    dHBr[3][3] = -7722.1999999999998
    dSBr[3][3] = -20
    dHBr[3][6] = -8200
    dSBr[3][6] = -20.100000000000001
    dHBr[3][7] = -7566.6999999999998
    dSBr[3][7] = -19.699999999999999
    dHBr[3][10] = -8133.3000000000002
    dSBr[3][10] = -20.899999999999999
    dHBr[3][12] = -7316.6999999999998
    dSBr[3][12] = -18.699999999999999
    dHBr[3][13] = -7725
    dSBr[3][13] = -19.800000000000001
    dHBr[3][17] = -7550
    dSBr[3][17] = -19.100000000000001
    dHBr[3][18] = -7966.6999999999998
    dSBr[3][18] = -19.600000000000001
    dHBr[3][19] = -8066.6999999999998
    dSBr[3][19] = -21.699999999999999
    dHBr[3][21] = -7611.1000000000004
    dSBr[3][21] = -19.100000000000001
    dHBr[3][22] = -7483.3000000000002
    dSBr[3][22] = -19.899999999999999
    dHBr[3][23] = -7725
    dSBr[3][23] = -19.800000000000001
    dHBr[3][24] = -7900
    dSBr[3][24] = -20.5
    dHBr[6][0] = -5600
    dSBr[6][0] = -13.5
    dHBr[6][1] = -9533.2999999999993
    dSBr[6][1] = -23.5
    dHBr[6][2] = -11100
    dSBr[6][2] = -26.699999999999999
    dHBr[6][3] = -7700
    dSBr[6][3] = -19.100000000000001
    dHBr[6][6] = -11000
    dSBr[6][6] = -26.600000000000001
    dHBr[6][7] = -7733.3000000000002
    dSBr[6][7] = -19.199999999999999
    dHBr[6][10] = -8750
    dSBr[6][10] = -22
    dHBr[6][12] = -8350
    dSBr[6][12] = -20.100000000000001
    dHBr[6][13] = -8550
    dSBr[6][13] = -21
    dHBr[6][17] = -8300
    dSBr[6][17] = -20.100000000000001
    dHBr[6][18] = -11050
    dSBr[6][18] = -26.699999999999999
    dHBr[6][19] = -6500
    dSBr[6][19] = -17.300000000000001
    dHBr[6][21] = -9233.2999999999993
    dSBr[6][21] = -22.300000000000001
    dHBr[6][22] = -6050
    dSBr[6][22] = -15.4
    dHBr[6][23] = -8550
    dSBr[6][23] = -21
    dHBr[6][24] = -8800
    dSBr[6][24] = -22
    dHBr[7][0] = -6966.6999999999998
    dSBr[7][0] = -17.899999999999999
    dHBr[7][1] = -8233.2999999999993
    dSBr[7][1] = -20.800000000000001
    dHBr[7][2] = -7700
    dSBr[7][2] = -19.100000000000001
    dHBr[7][3] = -7988.8999999999996
    dSBr[7][3] = -20.399999999999999
    dHBr[7][6] = -8500
    dSBr[7][6] = -20.5
    dHBr[7][7] = -7722.1999999999998
    dSBr[7][7] = -20
    dHBr[7][10] = -8500
    dSBr[7][10] = -21.699999999999999
    dHBr[7][12] = -7333.3000000000002
    dSBr[7][12] = -18.5
    dHBr[7][13] = -7916.6999999999998
    dSBr[7][13] = -20.100000000000001
    dHBr[7][17] = -7733.3000000000002
    dSBr[7][17] = -19.199999999999999
    dHBr[7][18] = -8100
    dSBr[7][18] = -19.800000000000001
    dHBr[7][19] = -8500
    dSBr[7][19] = -22.899999999999999
    dHBr[7][21] = -7722.1999999999998
    dSBr[7][21] = -19.199999999999999
    dHBr[7][22] = -7733.3000000000002
    dSBr[7][22] = -20.399999999999999
    dHBr[7][23] = -7916.6999999999998
    dSBr[7][23] = -20.100000000000001
    dHBr[7][24] = -8100
    dSBr[7][24] = -21
    dHBr[10][0] = -5800
    dSBr[10][0] = -15.199999999999999
    dHBr[10][1] = -8183.3000000000002
    dSBr[10][1] = -20.199999999999999
    dHBr[10][2] = -8350
    dSBr[10][2] = -20.100000000000001
    dHBr[10][3] = -7333.3000000000002
    dSBr[10][3] = -18.5
    dHBr[10][6] = -8400
    dSBr[10][6] = -19.800000000000001
    dHBr[10][7] = -7316.6999999999998
    dSBr[10][7] = -18.699999999999999
    dHBr[10][10] = -8100
    dSBr[10][10] = -20.199999999999999
    dHBr[10][12] = -7075
    dSBr[10][12] = -17.699999999999999
    dHBr[10][13] = -7587.5
    dSBr[10][13] = -18.899999999999999
    dHBr[10][17] = -7100
    dSBr[10][17] = -17.5
    dHBr[10][18] = -8375
    dSBr[10][18] = -19.899999999999999
    dHBr[10][19] = -7800
    dSBr[10][19] = -20.699999999999999
    dHBr[10][21] = -7516.6999999999998
    dSBr[10][21] = -18.399999999999999
    dHBr[10][22] = -6800
    dSBr[10][22] = -17.899999999999999
    dHBr[10][23] = -7587.5
    dSBr[10][23] = -18.899999999999999
    dHBr[10][24] = -8075
    dSBr[10][24] = -20.399999999999999
    dHBr[12][0] = -7450
    dSBr[12][0] = -18.5
    dHBr[12][1] = -8933.2999999999993
    dSBr[12][1] = -22.899999999999999
    dHBr[12][2] = -8750
    dSBr[12][2] = -22
    dHBr[12][3] = -8500
    dSBr[12][3] = -21.699999999999999
    dHBr[12][6] = -9850
    dSBr[12][6] = -24.300000000000001
    dHBr[12][7] = -8133.3000000000002
    dSBr[12][7] = -20.899999999999999
    dHBr[12][10] = -9025
    dSBr[12][10] = -23.300000000000001
    dHBr[12][12] = -8100
    dSBr[12][12] = -20.199999999999999
    dHBr[12][13] = -8562.5
    dSBr[12][13] = -21.800000000000001
    dHBr[12][17] = -8650
    dSBr[12][17] = -21.399999999999999
    dHBr[12][18] = -9300
    dSBr[12][18] = -23.100000000000001
    dHBr[12][19] = -8200
    dSBr[12][19] = -22.399999999999999
    dHBr[12][21] = -8683.2999999999993
    dSBr[12][21] = -21.600000000000001
    dHBr[12][22] = -7825
    dSBr[12][22] = -20.399999999999999
    dHBr[12][23] = -8562.5
    dSBr[12][23] = -21.800000000000001
    dHBr[12][24] = -8475
    dSBr[12][24] = -22.199999999999999
    dHBr[13][0] = -6625
    dSBr[13][0] = -16.800000000000001
    dHBr[13][1] = -8558.2999999999993
    dSBr[13][1] = -21.5
    dHBr[13][2] = -8550
    dSBr[13][2] = -21
    dHBr[13][3] = -7916.6999999999998
    dSBr[13][3] = -20.100000000000001
    dHBr[13][6] = -9125
    dSBr[13][6] = -22
    dHBr[13][7] = -7725
    dSBr[13][7] = -19.800000000000001
    dHBr[13][10] = -8562.5
    dSBr[13][10] = -21.800000000000001
    dHBr[13][12] = -7587.5
    dSBr[13][12] = -18.899999999999999
    dHBr[13][13] = -8075
    dSBr[13][13] = -20.300000000000001
    dHBr[13][17] = -7875
    dSBr[13][17] = -19.399999999999999
    dHBr[13][18] = -8837.5
    dSBr[13][18] = -21.5
    dHBr[13][19] = -8000
    dSBr[13][19] = -21.5
    dHBr[13][21] = -8100
    dSBr[13][21] = -20
    dHBr[13][22] = -7312.5
    dSBr[13][22] = -19.199999999999999
    dHBr[13][23] = -8075
    dSBr[13][23] = -20.300000000000001
    dHBr[13][24] = -8275
    dSBr[13][24] = -21.300000000000001
    dHBr[17][0] = -7350
    dSBr[17][0] = -18.800000000000001
    dHBr[17][1] = -8583.2999999999993
    dSBr[17][1] = -22.100000000000001
    dHBr[17][2] = -8800
    dSBr[17][2] = -22
    dHBr[17][3] = -8100
    dSBr[17][3] = -21
    dHBr[17][6] = -9400
    dSBr[17][6] = -23.699999999999999
    dHBr[17][7] = -7900
    dSBr[17][7] = -20.5
    dHBr[17][10] = -8475
    dSBr[17][10] = -22.199999999999999
    dHBr[17][12] = -8075
    dSBr[17][12] = -20.399999999999999
    dHBr[17][13] = -8275
    dSBr[17][13] = -21.300000000000001
    dHBr[17][17] = -8375
    dSBr[17][17] = -21.199999999999999
    dHBr[17][18] = -9100
    dSBr[17][18] = -22.899999999999999
    dHBr[17][19] = -7550
    dSBr[17][19] = -20.600000000000001
    dHBr[17][21] = -8516.7000000000007
    dSBr[17][21] = -21.5
    dHBr[17][22] = -7450
    dSBr[17][22] = -19.699999999999999
    dHBr[17][23] = -8275
    dSBr[17][23] = -21.300000000000001
    dHBr[17][24] = -8175
    dSBr[17][24] = -21.300000000000001
    dHBr[18][0] = -5700
    dSBr[18][0] = -13.199999999999999
    dHBr[18][1] = -9883.2999999999993
    dSBr[18][1] = -24.300000000000001
    dHBr[18][2] = -11050
    dSBr[18][2] = -26.699999999999999
    dHBr[18][3] = -8100
    dSBr[18][3] = -19.800000000000001
    dHBr[18][6] = -11450
    dSBr[18][6] = -27.199999999999999
    dHBr[18][7] = -7966.6999999999998
    dSBr[18][7] = -19.600000000000001
    dHBr[18][10] = -9300
    dSBr[18][10] = -23.100000000000001
    dHBr[18][12] = -8375
    dSBr[18][12] = -19.899999999999999
    dHBr[18][13] = -8837.5
    dSBr[18][13] = -21.5
    dHBr[18][17] = -8575
    dSBr[18][17] = -20.199999999999999
    dHBr[18][18] = -11250
    dSBr[18][18] = -26.899999999999999
    dHBr[18][19] = -7150
    dSBr[18][19] = -19.100000000000001
    dHBr[18][21] = -9400
    dSBr[18][21] = -22.399999999999999
    dHBr[18][22] = -6425
    dSBr[18][22] = -16.100000000000001
    dHBr[18][23] = -8837.5
    dSBr[18][23] = -21.5
    dHBr[18][24] = -9100
    dSBr[18][24] = -22.899999999999999
    dHBr[19][0] = -6000
    dSBr[19][0] = -16.899999999999999
    dHBr[19][1] = -6833.3000000000002
    dSBr[19][1] = -16.800000000000001
    dHBr[19][2] = -5600
    dSBr[19][2] = -13.5
    dHBr[19][3] = -6966.6999999999998
    dSBr[19][3] = -17.899999999999999
    dHBr[19][6] = -5800
    dSBr[19][6] = -12.9
    dHBr[19][7] = -6900
    dSBr[19][7] = -18.100000000000001
    dHBr[19][10] = -7450
    dSBr[19][10] = -18.5
    dHBr[19][12] = -5800
    dSBr[19][12] = -15.199999999999999
    dHBr[19][13] = -6625
    dSBr[19][13] = -16.800000000000001
    dHBr[19][17] = -5900
    dSBr[19][17] = -14.9
    dHBr[19][18] = -5700
    dSBr[19][18] = -13.199999999999999
    dHBr[19][19] = -9100
    dSBr[19][19] = -24
    dHBr[19][21] = -5800
    dSBr[19][21] = -14.4
    dHBr[19][22] = -7550
    dSBr[19][22] = -20.5
    dHBr[19][23] = -6625
    dSBr[19][23] = -16.800000000000001
    dHBr[19][24] = -7350
    dSBr[19][24] = -18.800000000000001
    dHBr[21][0] = -6833.3000000000002
    dSBr[21][0] = -16.800000000000001
    dHBr[21][1] = -9133.2999999999993
    dSBr[21][1] = -23.100000000000001
    dHBr[21][2] = -9533.2999999999993
    dSBr[21][2] = -23.5
    dHBr[21][3] = -8233.2999999999993
    dSBr[21][3] = -20.800000000000001
    dHBr[21][6] = -10233.299999999999
    dSBr[21][6] = -25.100000000000001
    dHBr[21][7] = -8000
    dSBr[21][7] = -20.300000000000001
    dHBr[21][10] = -8933.2999999999993
    dSBr[21][10] = -22.899999999999999
    dHBr[21][12] = -8183.3000000000002
    dSBr[21][12] = -20.199999999999999
    dHBr[21][13] = -8558.2999999999993
    dSBr[21][13] = -21.5
    dHBr[21][17] = -8533.2999999999993
    dSBr[21][17] = -20.899999999999999
    dHBr[21][18] = -9883.2999999999993
    dSBr[21][18] = -24.300000000000001
    dHBr[21][19] = -7633.3000000000002
    dSBr[21][19] = -20.699999999999999
    dHBr[21][21] = -8866.7000000000007
    dSBr[21][21] = -21.800000000000001
    dHBr[21][22] = -7233.3000000000002
    dSBr[21][22] = -18.699999999999999
    dHBr[21][23] = -8558.2999999999993
    dSBr[21][23] = -21.5
    dHBr[21][24] = -8583.2999999999993
    dSBr[21][24] = -22.100000000000001
    dHBr[22][0] = -7550
    dSBr[22][0] = -20.5
    dHBr[22][1] = -7233.3000000000002
    dSBr[22][1] = -18.699999999999999
    dHBr[22][2] = -6050
    dSBr[22][2] = -15.4
    dHBr[22][3] = -7733.3000000000002
    dSBr[22][3] = -20.399999999999999
    dHBr[22][6] = -6800
    dSBr[22][6] = -16.899999999999999
    dHBr[22][7] = -7483.3000000000002
    dSBr[22][7] = -19.899999999999999
    dHBr[22][10] = -7825
    dSBr[22][10] = -20.399999999999999
    dHBr[22][12] = -6800
    dSBr[22][12] = -17.899999999999999
    dHBr[22][13] = -7312.5
    dSBr[22][13] = -19.199999999999999
    dHBr[22][17] = -7175
    dSBr[22][17] = -18.699999999999999
    dHBr[22][18] = -6425
    dSBr[22][18] = -16.100000000000001
    dHBr[22][19] = -8850
    dSBr[22][19] = -24
    dHBr[22][21] = -6800
    dSBr[22][21] = -17.600000000000001
    dHBr[22][22] = -8200
    dSBr[22][22] = -22.199999999999999
    dHBr[22][23] = -7312.5
    dSBr[22][23] = -19.199999999999999
    dHBr[22][24] = -7450
    dSBr[22][24] = -19.699999999999999
    dHBr[23][0] = -6625
    dSBr[23][0] = -16.800000000000001
    dHBr[23][1] = -8558.2999999999993
    dSBr[23][1] = -21.5
    dHBr[23][2] = -8550
    dSBr[23][2] = -21
    dHBr[23][3] = -7916.6999999999998
    dSBr[23][3] = -20.100000000000001
    dHBr[23][6] = -9125
    dSBr[23][6] = -22
    dHBr[23][7] = -7725
    dSBr[23][7] = -19.800000000000001
    dHBr[23][10] = -8562.5
    dSBr[23][10] = -21.800000000000001
    dHBr[23][12] = -7587.5
    dSBr[23][12] = -18.899999999999999
    dHBr[23][13] = -8075
    dSBr[23][13] = -20.300000000000001
    dHBr[23][17] = -7875
    dSBr[23][17] = -19.399999999999999
    dHBr[23][18] = -8837.5
    dSBr[23][18] = -21.5
    dHBr[23][19] = -8000
    dSBr[23][19] = -21.5
    dHBr[23][21] = -8100
    dSBr[23][21] = -20
    dHBr[23][22] = -7312.5
    dSBr[23][22] = -19.199999999999999
    dHBr[23][23] = -8075
    dSBr[23][23] = -20.300000000000001
    dHBr[23][24] = -8275
    dSBr[23][24] = -21.300000000000001
    dHBr[24][0] = -5900
    dSBr[24][0] = -14.9
    dHBr[24][1] = -8533.2999999999993
    dSBr[24][1] = -20.899999999999999
    dHBr[24][2] = -8300
    dSBr[24][2] = -20.100000000000001
    dHBr[24][3] = -7733.3000000000002
    dSBr[24][3] = -19.199999999999999
    dHBr[24][6] = -8850
    dSBr[24][6] = -20.399999999999999
    dHBr[24][7] = -7550
    dSBr[24][7] = -19.100000000000001
    dHBr[24][10] = -8650
    dSBr[24][10] = -21.399999999999999
    dHBr[24][12] = -7100
    dSBr[24][12] = -17.5
    dHBr[24][13] = -7875
    dSBr[24][13] = -19.399999999999999
    dHBr[24][17] = -7375
    dSBr[24][17] = -17.600000000000001
    dHBr[24][18] = -8575
    dSBr[24][18] = -20.199999999999999
    dHBr[24][19] = -8450
    dSBr[24][19] = -22.399999999999999
    dHBr[24][21] = -7683.3000000000002
    dSBr[24][21] = -18.399999999999999
    dHBr[24][22] = -7175
    dSBr[24][22] = -18.699999999999999
    dHBr[24][23] = -7875
    dSBr[24][23] = -19.399999999999999
    dHBr[24][24] = -8375
    dSBr[24][24] = -21.199999999999999

    saltc = saltc/1000
    pri  = primerc/10E7
    dS = -12.4
    dH = -3400

    STR = primer.lower();

    for i in range(len(STR)-1):
        n1=ord(STR[i])
        n2=ord(STR[i+1])
        dH += dHBr[n1 - 97][n2 - 97]
        dS += dSBr[n1 - 97][n2 - 97]

    tm = (dH / (1.9872 * math.log(pri / 1600) + dS) + (16.6 * math.log(saltc)) / math.log(10)) - 273.15

    if thermodynamics:
        return tm,dH,dS
    else:
        return tm

'''

Examples
--------

>>> from pydna import read
>>> from pydna import Anneal
>>> template = read(">MyTemplate\\ngctactacacacgtactgactgcctccaagatagagtcagtaaccaca")
>>> fp = read(">ForwardPrimer\\ngctactacacacgtactgactg", ds=False )
>>> rp = read(">ReversePrimer\\ntgtggttactgactctatcttg", ds=False )
>>> primers = (fp,rp)
>>> p = Anneal(primers, template)
>>> p
Anneal(amplicons = 1)
>>> print p.report()
Template MyTemplate 48 nt linear:
Primer ForwardPrimer anneals at position 21
Primer ReversePrimer anneals reverse at position 27
>>> p.amplicons
[Amplicon(48)]
>>> prod = p.amplicons.pop()
>>> prod
Amplicon(48)
>>> prod.pcr_product()
Dseqrecord(-48)
>>> prod.pcr_product().seq
Dseq(-48)
gctactacacacgtactgac...agatagagtcagtaaccaca
cgatgatgtgtgcatgactg...tctatctcagtcattggtgt
>>> print prod.detailed_figure()
5gctactacacacgtactgactg3
 |||||||||||||||||||||| tm 52.6 (dbd) 58.3
5gctactacacacgtactgactg...caagatagagtcagtaaccaca3
3cgatgatgtgtgcatgactgac...gttctatctcagtcattggtgt5
                          |||||||||||||||||||||| tm 49.1 (dbd) 57.7
                         3gttctatctcagtcattggtgt5
>>>

'''



if __name__=="__main__":
    import doctest
    doctest.testmod()


    t = Dseqrecord("gctactacacacgtactgactgCCnnnTCcaagatagagtcagtaaccaca",circular=False)
    p1 = SeqRecord(Seq("NUNgctactacacacgtactgactg"))
    p2 = SeqRecord(Seq("NCNtgtggttactgactctatct"))
    assert pcr(p1,p2,t).seq.watson == "NUNgctactacacacgtactgactgCCnnnTCcaagatagagtcagtaaccacaNGN"
    t = Dseqrecord("gctactacacacgtactgactgCCnnnTCcaagatagagtcagtaaccaca",circular=True)
    p1 = SeqRecord(Seq("NANgctactacacacgtactgactg"))
    p2 = SeqRecord(Seq("NCNtgtggttactgactctatct"))
    assert pcr(p1,p2,t).seq.watson == "NANgctactacacacgtactgactgCCnnnTCcaagatagagtcagtaaccacaNGN"


    '''

    NANgctactacacacgtactgactg
       cgatgatgtgtgcatgactgacGGnnnAGgttctatctcagtcattggtgt

                             -------------29--------------

       --------------31---------------
       gctactacacacgtactgactgCCnnnTCcaagatagagtcagtaaccaca
                                      tctatctcagtcattggtgtNCN


    '''


    t = Dseqrecord("caagatagagtcagtaaccacagctactacacacgtactgactgCCnnnTC", circular=True)
    p1 = SeqRecord(Seq("NANgctactacacacgtactgactg"))
    p2 = SeqRecord(Seq("NCNtgtggttactgactctatct"))
    assert pcr(p1,p2,t).seq.watson == "NANgctactacacacgtactgactgCCnnnTCcaagatagagtcagtaaccacaNGN"



    '''
       --
       caagatagagtcagtaaccacagctactacacacgtactgactgCCnnnTC
         tctatctcagtcattggtgtNCN
                          NANgctactacacacgtactgactg
       gttctatctcagtcattggtgtcgatgatgtgtgcatgactgacGGnnnAG
                                                   -------
       ............................................




    '''



    import textwrap

    oligos_table_3='''
    GCGCGC
    CGTCGACG
    GAAGCTTC
    GGAATTCC
    GGTATACC
    GCGAATTCGC
    CAAAAAG
    CAAACAAAG
    CAAAAAAAG
    CAAATAAAG
    CAAAGAAAG
    CGCGTACGCGTACGCG'''

    for oligo in textwrap.dedent(oligos_table_3).splitlines():
        pass #print tmbreslauer86(oligo, thermodynamics = True)[3]

    oligos = '''
                CAGTCAGTACGTACGTGTACTGCCGTA
                CAGTCAGTACGTACGTGTACTGCCGTAGG
                CAGTCAGTACGTACGTGTACTGCCG
             '''

    for oligo in textwrap.dedent(oligos).splitlines():
        print oligo
        print tmbreslauer86(oligo)#, thermodynamics = True)
        print tmbresluc(oligo)    #, thermodynamics = True)
        print

     #                                  FZ     Primer3Plus
     #  CAGTCAGTACGTACGTGTACTGCCGTA     68.83  68.69
     #  CAGTCAGTACGTACGTGTACTGCCGTAGG   71.5   71.70
     #  CAGTCAGTACGTACGTGTACTGCCG       68.7   68.59




    s = parse('''
        >524_pFA6aF (29-mer)
        cacatacgatttaggtgacactatagaac
        >523_AgTEF1tpR (21-mer)
        ggttgtttatgttcggatgtg
        ''')

    from pydna import Dseq

    f= Dseq("cacatacgatttaggtgacactatagaaccacatccgaacataaacaacc",
            "gctaaatccactgtgatatcttggtgtaggcttgtatttgttgg"[::-1])


    print Anneal(s,Dseqrecord(f)).amplicons.pop().detailed_figure()



#    from pydna import read

#    template = Dseqrecord("tacactcaccgtctatcattatctactatcgactgtatcatctgatagcac")
#    p1 = read(">p1\ntacactcaccgtctatcattatc", ds= False)
#    p2 = read(">p1\ncgactgtatcatctgatagcac", ds = False).reverse_complement()
#    amplicon_list = Anneal((p1,p2), template).amplicons
#    amplicon = amplicon_list.pop()
#    print amplicon.detailed_figure()





