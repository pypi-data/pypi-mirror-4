from cellnopt.data import XMLMidas
import warnings
warnings.simplefilter("ignore")


def test_xmlmidas():

    print get_data("midas.xml")
    m = XMLMidas(XMLMidas(get_data("midas.xml"))
    m.test()
    sorted(m.stimuli) == ["EGF", "TNFa"]




test_xmlmidas()




from os.path import join as pj
from os.path import isfile
from os import sep

def get_data(filename):

    # read the full path name of this file including the file itself, so we
    # split all directory and rebuild the path without the file
    # itself to obtain the directory. surely there is a better
    # solution...
    moduledir = sep.join(__file__.split(sep)[:-1])
    sharedir =   pj(moduledir, '..','..','share', 'data')

    # now, given the share direcotry, look for the file and
    # check its existence.
    filedir = pj(sharedir, filename)
    if isfile(filedir):
        return filedir

    # well, it seems it did not work (develop mode maybe ?). So, let us try
    # something else
    sharedir =   pj(moduledir, '..','share', 'data')
    filedir = pj(sharedir, filename)
    if isfile(filedir):
        return filedir

    raise IOError("file %s not found in %s" % (filename, sharedir)  )

