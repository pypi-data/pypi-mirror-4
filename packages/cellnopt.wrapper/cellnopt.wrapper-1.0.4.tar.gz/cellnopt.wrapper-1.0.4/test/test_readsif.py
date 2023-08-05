from cellnopt.wrapper import readSIF, get_data

def test_readfiles():
    m = readSIF(get_data("ToyModelMKM.sif"))
