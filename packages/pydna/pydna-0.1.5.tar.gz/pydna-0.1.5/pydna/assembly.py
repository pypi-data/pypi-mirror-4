#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Provides functions for assembly of sequences by homologous recombination.
Given a list of sequences (Dseqrecords), all sequences will be analyzed for
overlapping regions of DNA (common substrings).

The assembly algorithm is based on forming a network where each
overlapping sequence forms a node and intervening sequences form edges.

Then all possible linear or circular assemblies will be returned in the
order of their length.


'''

import networkx as nx
import sys
import operator
import Bio.SeqIO
import itertools
import copy

from Bio.Seq                 import Seq
from Bio.Seq                 import reverse_complement as rc
from Bio.SeqUtils.CheckSum   import seguid

from findsubstrings_suffix_arrays_python        import common_sub_strings
#from find_sub_strings         import common_sub_strings
from Bio.Alphabet.IUPAC      import ambiguous_dna
from Bio.SeqFeature          import SeqFeature, FeatureLocation, ExactPosition
from pydna._simple_paths7    import all_circular_paths_edges
from pydna._simple_paths8    import all_simple_paths_edges
from pydna.dsdna             import Dseqrecord


def circular_assembly(form_rec_list, limit=25):
    '''Accepts a list of Dseqrecords and tries to assemble them into a
    circular assembly by homologous recombination based on shared
    regions of homology with a minimum length given by limit.

    Parameters
    ----------

    form_rec_list : list
        a list of Dseqrecord objects.

    limit : int, optional
        limit is set to 25 by default.


    Returns
    -------
    frecs, cp : tuple
        frecs are the same Dseqrecords as given as arguments, but with the
        regions of homology added to the features.

        cp is a list of Dseqrecords representing the circular products
        sorted by length (long -> short).

    '''

    frecs, G = _make_graph(form_rec_list, limit)
    G.remove_nodes_from(('5','3'))

    for cycle in nx.simple_cycles(G)[1:]:
        circular_paths = [(cycle+cycle[1:])[n:len(cycle)+n] for n in range(len(cycle)-1)]
        for circular_path in circular_paths:
            keynode = circular_path[0]
            x=[G[u][v][0]['sek'] for u,v in zip(circular_path, circular_path[1:])] #collect edges around cycle
            y=[G.node[node]['sek'] for node in circular_path]                      #collect nodes around cycle
            sm = reduce(lambda x,y:x+y, [s for s in list(itertools.chain.from_iterable(itertools.izip_longest(y,x)))[:-1]])
            incoming = [(n, keynode) for n in G.predecessors(keynode) if n not in circular_path]
            outgoing = [(keynode, n) for n in G.successors(keynode) if n not in circular_path]
            new_node = seguid(sm.seq)
            G.add_node(new_node, sek=sm)
            G.add_edges_from( [(p[0], new_node, {'sek' : G[p[0]][p[1]][0]['sek'] }) for p in incoming] )
            G.add_edges_from( [(new_node, p[1], {'sek' : G[p[0]][p[1]][0]['sek'] }) for p in outgoing] )

    circular_products=[]
    unique_lengths=set()

    for path in all_circular_paths_edges(G):
        result = Dseqrecord("")
        for first_node, second_node, edgedict in path:
            e=edgedict['sek']
            if e.seq.watson == len(e.seq.watson)*"-":
                result+=G.node[second_node]['sek'][len(e):]
            else:
                result+=e
                result+=G.node[second_node]['sek']

        circular_products.append(Dseqrecord(result, circular = True))
        unique_lengths.add(len(result))

    unique_circular_products=circular_products[:]

    for le in unique_lengths:
        lst = [se for se in circular_products if len(se)==le]
        a = lst.pop(0)
        for b in lst:
            if (str(a.seq).lower() in str(b.seq).lower()*2
                or
                str(a.seq).lower() in str(b.seq.reverse_complement()).lower()*2 ):
                unique_circular_products.remove(b)

    unique_circular_products.sort(key=len, reverse=True)

    for cp in unique_circular_products:
        length = len(cp)
        cp.description = "circular assembly product {}".format(length)
        assert cp.linear==False
        cp2 = Dseqrecord(cp, linear=True) + Dseqrecord(cp, linear=True)
        osf = [feature for feature in cp.features if "from_left" in feature.qualifiers]
        cp.features = [feature for feature in cp.features if not "from_left" in feature.qualifiers]
        for feature in osf:
            seq = feature.qualifiers["from_left"]
            if feature.strand == 1 and str(seq).lower()==str(cp2[feature.location.start:feature.location.start+len(seq)].seq).lower():
                begin = feature.location.start
                end   = feature.location.start+len(seq)
            elif feature.strand == -1 and str(seq).lower()==str(rc(cp2[feature.location.start:feature.location.start+len(seq)].seq)).lower():
                begin = feature.location.start
                end   = feature.location.start+len(seq)
            else:
                continue
            if end > length:
                a = SeqFeature(FeatureLocation(feature.location.start, length),
                               type=feature.type,
                               location_operator=feature.location_operator,
                               strand=feature.strand,
                               id=feature.id,
                               qualifiers=feature.qualifiers,
                               sub_features=None)
                b = SeqFeature(FeatureLocation(0, feature.location.end-length),
                               type=feature.type,
                               location_operator=feature.location_operator,
                               strand=feature.strand,
                               id=feature.id,
                               qualifiers=feature.qualifiers,
                               sub_features=None)
                newf = SeqFeature(FeatureLocation(a.location.start, b.location.end),
                               type=feature.type,
                               location_operator="join",
                               strand=feature.strand,
                               id=feature.id,
                               qualifiers=feature.qualifiers,
                               sub_features=[a,b])
            else:
                newf = SeqFeature(FeatureLocation(begin, end),
                                  type=feature.type,
                                  location_operator=feature.location_operator,
                                  strand=feature.strand,
                                  id=feature.id,
                                  qualifiers={k:v for k,v in feature.qualifiers.items() if k!="from_left"},
                                  sub_features=None,)
            cp.features.append(newf)

        osf = [feature for feature in cp.features if "to_right" in feature.qualifiers]
        cp.features = [feature for feature in cp.features if not "to_right" in feature.qualifiers]
        for feature in osf:
            seq = feature.qualifiers["to_right"]
            if feature.strand == 1 and str(seq).lower()==str(cp2[length+feature.location.start-len(seq):length+feature.location.start].seq).lower():
                begin = feature.location.start-len(seq)
                end   = feature.location.start
            elif feature.strand == -1 and str(seq).lower()==str(rc(cp2[feature.location.start-len(seq):feature.location.start].seq)).lower():
                begin = feature.location.start-len(seq)
                end   = feature.location.start
            else:
                continue
            if feature.location.start < 0:
                a = SeqFeature(FeatureLocation(length+feature.location.end-len(seq), end),
                               type=feature.type,
                               location_operator=feature.location_operator,
                               strand=feature.strand,
                               id=feature.id,
                               qualifiers=feature.qualifiers,
                               sub_features=None)
                b = SeqFeature(FeatureLocation(0, feature.location.end),
                               type=feature.type,
                               location_operator=feature.location_operator,
                               strand=feature.strand,
                               id=feature.id,
                               qualifiers=feature.qualifiers,
                               sub_features=None)
                newf = SeqFeature(FeatureLocation(a.location.start, b.location.end),
                               type=feature.type,
                               location_operator="join",
                               strand=feature.strand,
                               id=feature.id,
                               qualifiers=feature.qualifiers,
                               sub_features=[a,b])
            else:
                newf = SeqFeature(FeatureLocation(begin, end),
                                  type=feature.type,
                                  location_operator=feature.location_operator,
                                  strand=feature.strand,
                                  id=feature.id,
                                  qualifiers={k:v for k,v in feature.qualifiers.items() if k!="to_right"},
                                  sub_features=None,)
            cp.features.append(newf)

    return frecs, unique_circular_products

def linear_assembly(form_rec_list, limit=25):
    '''Accepts a list of Dseqrecords and tries to assemble them into a
    linear assembly by homologous recombination based on shared
    regions of homology with a minimum length given by limit.

    Parameters
    ----------

    form_rec_list : list
        a list of Dseqrecord objects.

    limit : int, optional
        limit is set to 25 by default.

    Returns
    -------
    frecs, lp : tuple
        frecs are the same Dseqrecords as given as arguments, but with the
        regions of homology added to the features.

        lp is a list of Dseqrecords representing the linear products
        sorted by length (long -> short).

    '''
    frecs, G = _make_graph(form_rec_list, limit)

    for cycle in nx.simple_cycles(G):
        circular_paths = [(cycle+cycle[1:])[n:len(cycle)+n] for n in range(len(cycle)-1)]
        for circular_path in circular_paths:
            keynode = circular_path[0]
            x=[G[u][v][0]['sek'] for u,v in zip(circular_path, circular_path[1:])] #collect edges
            y=[G.node[node]['sek'] for node in circular_path]                      #collect nodes
            sm = reduce(lambda x,y:x+y, [s for s in list(itertools.chain.from_iterable(itertools.izip_longest(y,x)))[:-1]])
            incoming = [(n, keynode) for n in G.predecessors(keynode) if n not in circular_path]
            outgoing = [(keynode, n) for n in G.successors(keynode) if n not in circular_path]
            new_node = seguid(sm.seq)
            G.add_node(new_node, sek=sm)
            G.add_edges_from( [(p[0], new_node, {'sek' : G[p[0]][p[1]][0]['sek'] }) for p in incoming] )
            G.add_edges_from( [(new_node, p[1], {'sek' : G[p[0]][p[1]][0]['sek'] }) for p in outgoing] )

    linear_products=[]
    unique_lengths=set()
    for path in all_simple_paths_edges(G, '5', '3', data=True):

        result = Dseqrecord("")

        for first_node, second_node, edgedict in path:
            e=edgedict.values().pop()['sek']
            if e.seq.watson == len(e.seq.watson)*"-":
                result+=G.node[second_node]['sek'][len(e):]
            else:
                result+=e
                result+=G.node[second_node]['sek']

#        for first_node, second_node, edgedict in path:
#            result+=edgedict.values().pop()['sek']
#            result+=G.node[second_node]['sek']
        assert result.circular == False
        linear_products.append(result)
        unique_lengths.add(len(result))

    unique_linear_products=linear_products[:]

    for le in unique_lengths:
        lst = [se for se in linear_products if len(se)==le]
        a = lst.pop()
        for b in lst:
            if ( str(a.seq).lower() == str(b.seq).lower()
                 or
                 str(a.seq).lower() == str(b.seq.reverse_complement()).lower()):
                unique_linear_products.remove(b)

    unique_linear_products.sort(key=len, reverse=True)

    for lp in unique_linear_products:
        lp.description = "linear assembly product {}".format(len(lp))
        osf = [feature for feature in lp.features if "from_left" in feature.qualifiers]
        lp.features = [feature for feature in lp.features if not "from_left" in feature.qualifiers]
        for feature in osf:
            seq = feature.qualifiers["from_left"]
            if feature.strand == 1 and str(seq).lower()==str(lp[feature.location.start:feature.location.start+len(seq)].seq).lower():
                begin = feature.location.start
                end   = feature.location.start+len(seq)
            elif feature.strand == -1 and str(seq).lower()==str(rc(lp[feature.location.start:feature.location.start+len(seq)].seq)).lower():
                begin = feature.location.start
                end   = feature.location.start+len(seq)
            else:
                continue
            newf = SeqFeature(FeatureLocation(begin, end),
                              type=feature.type,
                              location_operator=feature.location_operator,
                              strand=feature.strand,
                              id=feature.id,
                              qualifiers={k:v for k,v in feature.qualifiers.items() if k!="from_left"},
                              sub_features=None,)
            lp.features.append(newf)

        osf = [feature for feature in lp.features if "to_right" in feature.qualifiers]
        lp.features = [feature for feature in lp.features if not "to_right" in feature.qualifiers]
        for feature in osf:
            seq = feature.qualifiers["to_right"]
            if feature.strand == 1 and str(seq).lower()==str(lp[feature.location.start-len(seq):feature.location.start].seq).lower():
                begin = feature.location.start-len(seq)
                end   = feature.location.start
            elif feature.strand == -1 and str(seq).lower()==str(rc(lp[feature.location.start-len(seq):feature.location.start].seq)).lower():
                begin = feature.location.start-len(seq)
                end   = feature.location.start
            else:
                continue
            newf = SeqFeature(FeatureLocation(begin, end),
                              type=feature.type,
                              location_operator=feature.location_operator,
                              strand=feature.strand,
                              id=feature.id,
                              qualifiers={k:v for k,v in feature.qualifiers.items() if k!="to_right"},
                              sub_features=None,)
            lp.features.append(newf)
    return frecs, unique_linear_products

def _make_graph(recs, limit=25):

    form_rec_list=list(copy.deepcopy(recs))

    for frec in form_rec_list:
        frec.features = [f for f in frec.features if f.type!="overlap"]
        frec.seq = frec.seq.fill_in() # !!!

    rc = { frec : frec.rc() for frec in form_rec_list }

    G=nx.MultiDiGraph( multiedges=True, selfloops=False)
    G.add_node( "5", sek=Dseqrecord(""))
    G.add_node( "3", sek=Dseqrecord(""))

    matches=[]

    for a, b in itertools.combinations(form_rec_list, 2):
        match = common_sub_strings(str(a.seq).upper(),
                                   str(b.seq).upper(),
                                                limit)
        if match:
            matches.append((a, b, match))

        match = common_sub_strings(str(a.seq).upper(),
                                   str(rc[b].seq).upper(),
                                   limit)
        if match:
            matches.append((a, rc[b], match))
            matches.append((rc[a], b, [(len(a)-sa-le,len(b)-sb-le,le) for sa,sb,le in match]))

    for a, b, match in matches:
        for start_in_a, start_in_b, length in match:
            node_seq = a[start_in_a:start_in_a+length]
            node_seq2 = b[start_in_b:start_in_b+length]
            assert str(node_seq.seq).lower() == str(node_seq2.seq).lower()
            node_seq.features.extend(node_seq2.features)
            chksum = seguid(node_seq.seq)
            G.add_node(chksum, sek = node_seq)

            qual      = {"note"             : "olp_{}".format(chksum),
                         "chksum"            : chksum,
                         "ApEinfo_fwdcolor" : "green",
                         "ApEinfo_revcolor" : "red",}

            a.features.append( SeqFeature( FeatureLocation(start_in_a,
                                                           start_in_a + length),
                                                           type = "overlap",
                                                           qualifiers = qual))
            b.features.append( SeqFeature( FeatureLocation(start_in_b,
                                                           start_in_b + length),
                                                           type = "overlap",
                                                           qualifiers = qual))
    form_rec_list.extend(rc.values())

    for frec in form_rec_list:
        overlaps = sorted({f.qualifiers["chksum"]:f for f in frec.features if f.type=="overlap"}.values(), key = operator.attrgetter("location.start"))
        if overlaps:
            overlaps = ([SeqFeature(FeatureLocation(0,0),
                         type = "overlap",
                         qualifiers = {"chksum":"5"})]+
                         overlaps+
                        [SeqFeature(FeatureLocation(len(frec),len(frec)),
                                    type = "overlap",
                                    qualifiers = {"chksum":"3"})])

            for olp1, olp2 in zip(overlaps, overlaps[1:]):
                n1 = olp1.qualifiers["chksum"]
                n2 = olp2.qualifiers["chksum"]
                start, end = olp1.location.end, olp2.location.start
                sek = frec[start:end]
                if start>end:
                    sek=Dseqrecord((start-end)*"-") # tandem overlaps overlap with each other !
                for feature in frec.features:
                    if start<feature.location.end<end and feature.location.start<start:
                        newf = SeqFeature(FeatureLocation(feature.location.end-start,
                                                          feature.location.end-start),
                                          type=feature.type,
                                          location_operator=feature.location_operator,
                                          strand=feature.strand,
                                          id=feature.id,
                                          qualifiers=feature.qualifiers,
                                          sub_features=None,)
                        newf.qualifiers['to_right'] = feature.extract(frec).seq
                        sek.features.append(newf)
                    if start<feature.location.start<end and feature.location.end>end:
                        newf = SeqFeature(FeatureLocation(feature.location.start-start,
                                                          feature.location.start-start),
                                          type=feature.type,
                                          location_operator=feature.location_operator,
                                          strand=feature.strand,
                                          id=feature.id,
                                          qualifiers=feature.qualifiers,
                                          sub_features=None,)
                        newf.qualifiers['from_left'] = feature.extract(frec).seq
                        sek.features.append(newf)
                G.add_edge(n1, n2, sek=sek)
    return form_rec_list, G




if __name__=="__main__":
    pass












