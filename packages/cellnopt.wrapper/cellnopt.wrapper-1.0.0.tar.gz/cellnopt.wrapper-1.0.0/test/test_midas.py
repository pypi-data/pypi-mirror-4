from cellnopt.wrapper import readMIDAS, get_data, makeCNOlist
import glob

def test_readfiles():
    filename = "ToyModelMKM.csv"
    m = readMIDAS(get_data(filename), verbose=False)
    cnolist = makeCNOlist(m)


