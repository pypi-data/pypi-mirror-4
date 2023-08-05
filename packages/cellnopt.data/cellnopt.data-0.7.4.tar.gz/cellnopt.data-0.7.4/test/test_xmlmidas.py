from cellnopt.data import XMLMidas
import warnings
warnings.simplefilter("ignore")

from easydev import get_shared_directory_path
shareddir = get_shared_directory_path("cellnopt.data")
from os.path import join as pj



def test_xmlmidas():

    m = XMLMidas(pj(shareddir, "data", "midas.xml"))
    m.test()
    sorted(m.stimuliNames) == ["EGF", "TNFa"]




