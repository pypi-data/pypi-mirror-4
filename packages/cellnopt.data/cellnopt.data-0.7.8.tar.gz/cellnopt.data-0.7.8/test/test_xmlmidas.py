from cellnopt.data import XMLMidas, cnodata
import warnings
warnings.simplefilter("ignore")
import os
from os.path import join as pj


from easydev import get_shared_directory_path
shared = pj(get_shared_directory_path("cellnopt.data"), "data", "XML")

def test_xmlmidas():

    m = XMLMidas(pj(shared, "midas.xml"))
    m.test()
    sorted(m.stimuliNames) == ["EGF", "TNFa"]




