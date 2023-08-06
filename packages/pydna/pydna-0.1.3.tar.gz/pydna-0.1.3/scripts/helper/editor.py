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