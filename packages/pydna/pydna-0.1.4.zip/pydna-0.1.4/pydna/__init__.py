#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2013 by Björn Johansson.  All rights reserved.
# This code is part of the Python-dna distribution and governed by its
# license.  Please see the LICENSE.txt file that should have been included
# as part of this package.

'''
    Python-dna
    ~~~~~~~~~~

    The Python-dna package.

    :copyright: Copyright 2013 by Björn Johansson.  All rights reserved.
    :license:   This code is part of the Python-dna distribution and governed by its
                license.  Please see the LICENSE.txt file that should have been included
                as part of this package.

'''

__author__       = "Björn Johansson"
__date__         = "2013-03-15"
__copyright__    = "Copyright 2013, Björn Johansson"
__credits__      = ["Björn Johansson"]
__license__      = "BSD"
__version__      = "0.1.4"
__maintainer__   = "Björn Johansson"
__email__        = "bjorn_johansson@bio.uminho.pt"
__status__       = "Development" # "Production" #"Prototype" # "Production"

#__all__ = [ "Ape",
#            "Anneal",
#            "linear_assembly",
#            "circular_assembly",
#            "Dseq",
#            "Dseqrecord",
#            "Genbank",
#            "eq",
#            "shift_origin",
#            "copy_features",
#            "parse",
#            "pcr",
#            "read",
#            "sync",
#            "common_sub_strings",]

from pydna.editor              import Editor
from pydna.amplify             import Anneal
from pydna.download            import Genbank
from pydna.assembly            import circular_assembly
from pydna.findsubstrings_suffix_arrays_python    import common_sub_strings
from pydna.utils               import copy_features
from pydna.dsdna               import Dseqrecord
from pydna.dsdna               import Dseq
from pydna.utils               import eq

from pydna.assembly            import linear_assembly

from pydna.dsdna               import parse
from pydna.amplify             import pcr
from pydna.dsdna               import read
from pydna.utils               import shift_origin
from pydna.utils               import sync

try:
    del findsubstrings_suffix_arrays_python
    del assembly
    del dsdna
    del editor
    del amplify
    del utils
    del download
    del _simple_paths7
    del _simple_paths8
except NameError:
    pass
