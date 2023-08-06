#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''This module provides a class for opening a sequence using an editor
that accepts a path as a command line argument.

ApE - A plasmid Editor [1]_ is such an editor.

References
----------

.. [1] http://biologylabs.utah.edu/jorgensen/wayned/ape/



Examples
--------

>>> import pydna
>>> ape = pydna.Editor("tclsh /home/bjorn/ApE/apeextractor/ApE.vfs/lib/app-AppMain/AppMain.tcl")
>>> ape.open("aaa")
>>>

'''

import tempfile
import sys
import os
import subprocess
import itertools
import operator
import shutil
from Bio           import SeqIO
from Bio.SeqRecord import SeqRecord
import dsdna

class Editor:

    def __init__(self, shell_command_for_editor, tmpdir=None):
        path    = (shell_command_for_editor,
                   shell_command_for_editor.split("tcl")[1].strip(),
                   shell_command_for_editor.split("tclsh")[1].strip(),)

        if True in [os.path.isfile(p) for p in path]:
            self.path_to_editor = shell_command_for_editor
        else:
            print
            print path_to_editor
            print "is not a valid path to ApE"
            raise(ValueError("invalid path to ApE"))

        self.tmpdir = tmpdir or os.path.join(tempfile.gettempdir(),"ApE")
        try:
            os.makedirs(self.tmpdir)
        except OSError:
            pass

    def open(self,*args,**kwargs):
        '''Open a sequence for editing in an editor.

       Parameters
       ----------
       args : sequence or iterable of sequences
            sequences to to be opened by the editor.

       '''

        args=list(args)
        for i, arg in enumerate(args):
            if not hasattr(arg, "__iter__") or isinstance(arg, SeqRecord):
                args[i] = (arg,)
        seqs = []
        names = []
        for arg in itertools.chain.from_iterable(args):
            seq=dsdna.Dseqrecord(arg)
            for feature in seq.features:
                qf = feature.qualifiers
                if not "label" in qf:
                    try:
                        qf["label"] = qf["note"]
                    except KeyError:
                        qf["label"] = "feat{}".format(len(feature))
                if not "ApEinfo_fwdcolor" in qf:
                    qf["ApEinfo_fwdcolor"]="cyan"
                if not "ApEinfo_revcolor" in qf:
                    qf["ApEinfo_revcolor"]="red"
            seq.features.sort(key = operator.attrgetter("location.start"))
            seqs.append(seq)
            name=seq.name
            n=1
            while True:
                if name in names:
                    newname=name+"_"+str(n)
                    if newname in names:
                        n+=1
                        continue
                    else:
                        names.append(newname)
                        break
                else:
                    names.append(seq.description)
                    break
        pathstofiles = []
        path = tempfile.mkdtemp(dir=self.tmpdir)

        for name, seq in zip(names,seqs):
            whole_path = "{}.gb".format(os.path.join(path, name))
            seq.write(whole_path)
            pathstofiles.append('"{}"'.format(whole_path))

        #print "{} {}".format(self.path_to_editor,
        #                       " ".join(pathstofiles))

        p = subprocess.Popen("{} {}".format(self.path_to_editor," ".join(pathstofiles)),
                             shell=True,
                             stdout = tempfile.TemporaryFile(),
                             stderr = tempfile.TemporaryFile()).pid

        #shutil.rmtree(path)

if __name__=="__main__":
    from Bio import SeqIO
    sr1 = SeqIO.parse("../tests/pUC19.gb","gb").next()
    sr2 = SeqIO.parse("../tests/pCAPs.gb","gb").next()
    aperunner = Ape("tclsh /home/bjorn/ApE/apeextractor/ApE.vfs/lib/app-AppMain/AppMain.tcl")
    aperunner.open(sr1,sr2)
