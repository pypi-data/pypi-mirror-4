#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__       = "Björn Johansson"
__date__         = "2012-10-25"
__copyright__    = "Copyright 2012, Björn Johansson"
__credits__      = ["Björn Johansson"]
__license__      = "BSD"
__version__      = "0.0.1"
__maintainer__   = "Björn Johansson"
__email__        = "bjorn_johansson@bio.uminho.pt"
__status__       = "Development" # "Production" #"Prototype" # "Production"


from editor import ape
from genbank import gb
#import load_my_primers
#from load_my_primers import primer, new_primer, old_primer


# coding: utf-8
from Bio import SeqIO
from Bio.Alphabet.IUPAC import IUPACAmbiguousDNA

global new_primer
global primer
global old_primer
global new_primer_dict
global primer_dict
global old_primer_dict

new_primer = list(SeqIO.parse("/home/bjorn/Dropbox/wikidata/PrimersToBuy.wiki", "fasta", IUPACAmbiguousDNA()))
primer     = list(SeqIO.parse("/home/bjorn/Dropbox/wikidata/Primers.wiki", "fasta" ,IUPACAmbiguousDNA()))

primer     = primer[::-1]
old_primer = primer[:37]
primer     = primer[37:]

new_primer_dict         = dict((p.id, p) for p in new_primer)
primer_dict             = dict((p.id, p) for p in primer)
old_primer_dict         = dict((p.id, p) for p in old_primer)

assert str(primer_dict["509_mycGFPr"].seq) == "CTACTTGTACAGCTCGTCCA"
assert primer[0].id == "0_S1"
assert primer[580].id == "580_GXF1_YPK_fwd"

print "{:3d} old primers    -> old_primer [list]".format(len(old_primer))
print "{:3d} primers        -> primer [list]".format(len(primer))
print "{:3d} primers to buy -> new_primer [list]".format(len(new_primer))


from pydna.download import Genbank as _Genbank
import sys
import os
import percache
cache = percache.Cache("/tmp/genbank-cache")

def _get_proxy_from_global_settings():

    """Get proxy settings."""
    if sys.platform.startswith('linux'):
        try:
            from gi.repository import Gio
        except ImportError:
            return
        mode = Gio.Settings.new('org.gnome.system.proxy').get_string('mode')
        if mode == 'none':
            return ''
        http_settings = Gio.Settings.new('org.gnome.system.proxy.http')
        host = http_settings.get_string('host')
        port = http_settings.get_int('port')
        if http_settings.get_boolean('use-authentication'):
            username = http_settings.get_string('authentication_user')
            password = http_settings.get_string('authentication_password')
        else:
            username = password = None
            return 'http://{}:{}'.format(host,port)

_proxy = _get_proxy_from_global_settings()

_gbloader = _Genbank("bjornjobb@gmail.com",_proxy)

@cache
def gb(item):
    return _gbloader.nucleotide(item)



from pydna.editor import Ape as _Ape

_apeloader = _Ape("tclsh /home/bjorn/ApE/apeextractor/ApE.vfs/lib/app-AppMain/AppMain.tcl")

def ape(*args,**kwargs):

#    if raw_input("Open {} in Ape? (y/n)".format(plasmid.description))[0] in "yY":
#        ape(plasmid)

    return _apeloader.open(*args,**kwargs)

if __name__=="__main__":
    from pydna import read
    sr1 = read("../../tests/pUC19.gb","gb")
    sr2 = read("../../tests/pCAPs.gb","gb")
    sr3 = read(">abc\naaa")
    ape(sr1, sr1, sr1)
    print "Done!"