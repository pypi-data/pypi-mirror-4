#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''This module provides miscellaneous functions.


'''

from Bio.SeqFeature import SeqFeature
from Bio.SeqFeature import FeatureLocation


def eq(*args,**kwargs):
    '''Compares two or more DNA sequences for equality i.e. they
    represent the same DNA molecule. Comparisons are case insensitive.

    Parameters
    ----------
    args : iterable
        iterable containing sequences
        args can be strings, Biopython Seq or SeqRecord, Dseqrecord
        or dsDNA objects.
    circular : bool, optional
        Consider all molecules circular or linear
    linear : bool, optional
        Consider all molecules circular or linear

    Returns
    -------
    eq : bool
        Returns True or False

    Notes
    -----

    Compares two or more DNA sequences for equality i.e. if they
    represent the same DNA molecule.

    Two linear sequences are considiered equal if either:

    * They have the same sequence (case insensitive)
    * One sequence is the reverse complement of the other (case insensitive)

    Two circular sequences are considiered equal if:

    1. They have the same length.

    AND

    2. One sequence or its reverse complement can be found in the
       concatenation of the other sequence with itself (they are circular
       permutations).

    The topology for the comparison can be set using one of the keywords
    linear or circular to True or False.

    If circular or linear is not set, it will be deduced from the topology of
    each sequence for sequences that have a linear or circular attribute
    (like Dseq and Dseqrecord).

    Examples
    --------

    >>> from pydna import eq, Dseqrecord
    >>> eq("aaa","AAA")
    True
    >>> eq("aaa","AAA","TTT")
    True
    >>> eq("aaa","AAA","TTT","tTt")
    True
    >>> eq("aaa","AAA","TTT","tTt", linear=True)
    True
    >>> eq("Taaa","aTaa", linear = True)
    False
    >>> eq("Taaa","aTaa", circular = True)
    True
    >>> a=Dseqrecord("Taaa")
    >>> b=Dseqrecord("aTaa")
    >>> eq(a,b)
    False
    >>> eq(a,b,circular=True)
    True
    >>> a=a.looped()
    >>> b=b.looped()
    >>> eq(a,b)
    True
    >>> eq(a,b,circular=False)
    False
    >>> eq(a,b,linear=True)
    False
    >>> eq(a,b,linear=False)
    True
    >>> eq("ggatcc","GGATCC")
    True
    >>> eq("ggatcca","GGATCCa")
    True
    >>> eq("ggatcca","tGGATCC")
    True


    '''

    from Bio.Seq import reverse_complement
    from Bio.SeqRecord import SeqRecord
    import itertools
    args=list(args)
    for i, arg in enumerate(args):
        if not hasattr(arg, "__iter__") or isinstance(arg, SeqRecord):
            args[i] = (arg,)
    args = list(itertools.chain.from_iterable(args))

    topology = None

    if "linear" in kwargs:
        if kwargs["linear"]==True:
            topology = "linear"
        if kwargs["linear"]==False:
            topology = "circular"
    elif "circular" in kwargs:
        if kwargs["circular"]==True:
            topology = "circular"
        if kwargs["circular"]==False:
            topology = "linear"
    else:
        # topology keyword not set, look for topology associated to each sequence
        # otherwise raise exception
        topology = set([arg.circular if hasattr(arg, "circular") else None for arg in args])

        if len(topology)!=1:
            raise Exception("sequences have different topologies")
        topology = topology.pop()
        if topology in (False, None):
            topology = "linear"
        elif topology==True:
            topology = "circular"

    #args_string_list    = [str(arg.seq).lower() if hasattr(arg,"seq") else str(arg).lower() for arg in args]

    args = [arg.seq if hasattr(arg, "seq") else arg for arg in args]
    args_string_list    = [arg.watson.lower() if hasattr(arg, "watson") else str(arg).lower() for arg in args]

    length = set((len(s) for s in args_string_list))
    if len(length)!=1:
        return False
    same = True
    if topology == "circular":
        # force circular comparison of all given sequences
        for s1, s2 in itertools.combinations(args_string_list, 2):
            if not ( s1 in s2+s2 or reverse_complement(s1) in s2+s2):
                same = False
    elif topology == "linear":
        # force linear comparison of all given sequences
        for s1,s2 in itertools.combinations(args_string_list, 2):
            if not ( s1==s2 or s1==reverse_complement(s2) ):
                same = False
    return same

def shift_origin(seq, shift):
    '''Shift the origin of seq which is assumed to be a circular
    sequence.

    Parameters
    ----------
    seq : string, Biopython Seq, Biopython SeqRecord, Dseq or Dseqrecord
        sequence to be shifted.

    Returns
    -------
    new_seq : string, Biopython Seq, Biopython SeqRecord, Dseq or Dseqrecord
        sequence with a new origin.

    Examples
    --------

    >>> import pydna
    >>> pydna.shift_origin("taaa",1)
    'aaat'
    >>> pydna.shift_origin("taaa",0)
    'taaa'
    >>> pydna.shift_origin("taaa",2)
    'aata'
    >>> pydna.shift_origin("gatc",2)
    'tcga'

    '''
    from Bio.SeqFeature import SeqFeature
    from Bio.SeqFeature import FeatureLocation
    from Bio.SeqRecord  import SeqRecord
    import copy

    length=len(seq)

    if not 0<=shift<length:
        raise(ValueError("shift ({}) has to be 0<=shift<length({})",format((shift,length,))))

    if hasattr(seq, "linear"):
        new = seq.tolinear()
    else:
        new = seq

    new = (new+new)[shift:shift+length]

    def wraparound(feature):
        new_start = length -(shift-feature.location.start)
        new_end   = feature.location.end-shift
        a = SeqFeature(FeatureLocation(0, new_end),
                       type=feature.type,
                       location_operator=feature.location_operator,
                       strand=feature.strand,
                       id=feature.id,
                       qualifiers=feature.qualifiers,
                       sub_features=None)
        b = SeqFeature(FeatureLocation(new_start, length),
                       type=feature.type,
                       location_operator=feature.location_operator,
                       strand=feature.strand,
                       id=feature.id,
                       qualifiers=feature.qualifiers,
                       sub_features=None)
        c = SeqFeature(FeatureLocation(new_start, new_end),
                       type=feature.type,
                       location_operator="join",
                       strand=feature.strand,
                       id=feature.id,
                       qualifiers=feature.qualifiers,
                       sub_features=[a,b])
        sub_features=[]
        for sf in feature.sub_features:
            if feature.location.end<shift:
                sub_features.append(SeqFeature(FeatureLocation(length-feature.location.start,
                                                               length-feature.location.end),
                                    type=feature.type,
                                    location_operator=feature.location_operator,
                                    strand=feature.strand,
                                    id=feature.id,
                                    qualifiers=feature.qualifiers,
                                    sub_features=None))
            elif feature.location.start>shift:
                sub_features.append(SeqFeature(FeatureLocation(feature.location.start-shift,
                                                               feature.location.end-shift),
                                    type=feature.type,
                                    location_operator=feature.location_operator,
                                    strand=feature.strand,
                                    id=feature.id,
                                    qualifiers=feature.qualifiers,
                                     sub_features=None))
            else:
                sub_features.extend(wraparound(sf))
        c.sub_features.extend(sub_features)
        return c

    if hasattr(seq, "features"):
        for feature in seq.features:
            if shift in feature:
                new.features.append(wraparound(feature))

    if hasattr(seq, "linear"):
        new = new.looped()

    return new


def sync(seq, ref):
    '''Synchronize two circular sequences.

    Parameters
    ----------
    seq : string, Biopython Seq, Biopython SeqRecord, Dseq or Dseqrecord
        sequence to be shifted.
    ref : string, Biopython Seq, Biopython SeqRecord, Dseq or Dseqrecord
        The reference sequence.

    Returns
    -------
    sequence : string, Biopython Seq, Biopython SeqRecord, Dseq or Dseqrecord
        sequence with a new origin.

    This function tries to rotate the circular sequence seq
    so that it has a maximum overlap with ref.

    Examples
    --------

    >>> import pydna
    >>> pydna.sync("taaatc","aaataa")
    'aaatct'
    >>> pydna.sync("taaatc","aaataa")
    'aaatct'
    >>> pydna.sync("taaat","aaataa")
    'aaatt'


    '''
    import itertools
    import copy
    from Bio.Seq import reverse_complement
    from Bio.Seq import Seq
    from Bio.SeqRecord import SeqRecord
    from findsubstrings_suffix_arrays_python import  common_sub_strings
    from utils import eq

    if hasattr(seq, "linear"):
        sequence = seq.tolinear()
    else:
        sequence = copy.deepcopy(seq)

    if hasattr(sequence, "seq"):
        sequence = sequence.seq
        if hasattr(sequence, "watson"):
            a    = str(sequence.watson).lower()
            a_rc = str(sequence.crick).lower()
            sequence_rc     = sequence.reverse_complement()
            double_sequence = sequence+sequence
        else:
            a               = str(sequence.lower())
            a_rc            = str(sequence.reverse_complement()).lower()
            sequence_rc     = sequence.reverse_complement()
            double_sequence = sequence+sequence
    else:
        a    = str(sequence).lower()
        a_rc = str(reverse_complement(sequence)).lower()
        sequence_rc = reverse_complement(sequence)
        double_sequence = a+a

    if hasattr(ref, "seq"):
        b=ref.seq
        if hasattr(ref, "watson"):
            b = str(b.watson).lower()
        else:
            b = str(b).lower()
    else:
        b = str(ref.lower())

    b=b[:len(a)]

    c = common_sub_strings(a+a, b, limit = min(25, 25*(len(a)/25)+1))
    d = common_sub_strings(a_rc+a_rc, b, limit = min(25, 25*(len(a)/25)+1))

    if c:
        starta, startb, length = c.pop(0)
    else:
        starta, startb, length = 0,0,0

    if d:
        starta_rc, startb_rc, length_rc = d.pop(0)
    else:
        starta_rc, startb_rc, length_rc = 0,0,0

    if not c and not d:
        raise Exception("no overlap !")

    if length_rc>length:
        starta, startb = starta_rc, startb_rc
        sequence = sequence_rc

    if starta>startb:
        if len(a)<len(b):
            ofs = starta-startb + len(b)-len(a)
        else:
            ofs = starta-startb
    elif starta<startb:
        ofs = startb-starta + len(a)-len(b)
        ofs = len(a)-ofs
    elif starta==startb:
        ofs=0

    sequence = shift_origin(seq, ofs)

    try:
        sequence.circular=True
    except AttributeError:
        pass

    if hasattr(seq, "watson"):
        assert eq(seq.watson, sequence, circular =True)
        return dsdna(sequence)
    assert eq(seq, sequence, circular =True)
    return sequence

def copy_features(source_sr, target_sr, limit = 10):
    '''This function tries to copy all features in source_seq and copy
    them to target_seq. Source_sr and target_sr are objects with
    a features property, such as Dseqrecord or Biopython SeqRecord.

    Parameters
    ----------

    source_seq : SeqRecord or Dseqrecord
        The sequence to copy features from

    target_seq : SeqRecord or Dseqrecord
        The sequence to copy features to

    Returns
    -------
    bool : True
        This function acts on target_seq in place.
        No data is returned.


    '''
    import re
    from Bio.Seq import reverse_complement as rc
    target_length    = len(target_sr)
    target_string    = str(target_sr.seq).upper()

    try:
        circular = bool(target_sr.circular)
    except AttributeError:
        circular=False

    newfeatures=[]

    trgt_string = target_string
    trgt_string_rc = rc(trgt_string)

    for feature in [f for f in source_sr.features if len(f)>limit]:
        fsr            = feature.extract(source_sr).upper()
        featurelength  = 0# len(fsr)

        if circular:
            trgt_string = target_string+target_string[:featurelength]
            trgt_string_rc = rc(trgt_string)

        positions = (
        [(m.start(), m.end(), 1,) for m in re.finditer(str(fsr.seq),trgt_string)]
        +
        [(len(trgt_string_rc)-m.end(),len(trgt_string_rc)-m.start(),-1,)
                      for m in re.finditer(str(fsr.seq),trgt_string_rc)])

        for begin, end, strand in positions:
            if circular and begin<target_length<end:
                end = end-len(
                              target_sr)
                sf1 = SeqFeature(FeatureLocation(begin, trgt_length),
                                 type=feature.type,
                                 location_operator=feature.location_operator,
                                 strand=strand,
                                 id=feature.id,
                                 qualifiers=feature.qualifiers,
                                 sub_features=None,)
                sf2 = SeqFeature(FeatureLocation(0, end),
                                 type=feature.type,
                                 location_operator=feature.location_operator,
                                 strand=strand,
                                 id=feature.id,
                                 qualifiers=feature.qualifiers,
                                 sub_features=None,)
                nf =  SeqFeature(FeatureLocation(begin, end),
                                 type=feature.type,
                                 location_operator="join",
                                 strand=strand,
                                 id=feature.id,
                                 qualifiers=feature.qualifiers,
                                 sub_features=[sf1,sf2],)
            else:
                nf = SeqFeature(FeatureLocation(begin,end),
                     type=feature.type,
                     location_operator=feature.location_operator,
                     strand=strand,
                     id=feature.id,
                     qualifiers=feature.qualifiers,
                     sub_features=None)
            newfeatures.append(nf)
    target_sr.features.extend(newfeatures)
    return True

if __name__=="__main__":
    import doctest
    doctest.testmod()
