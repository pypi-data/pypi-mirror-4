from cellnopt.data import cnodata
import warnings
warnings.simplefilter("ignore")


def test_webdata():
    cnodata("ToyModelMKM.sif") # should be found on the web
    cnodata("ToyModelMKM.sif", local=True) # look into sampleModels locally.

    # try a file available in wrapper only.
    cnodata("ToyModelMMB.sif") # cellnopt.wrapper
    cnodata("ToyModelT2.sif")  # cellnopt.wrapper

    # try non-existing file
    try:
        cnodata("dummy.sif")  # cellnopt.wrapper
        assert False
    except:
        assert True
    # try incorrect extension file
    try:
        cnodata("dummy.DUM")  # cellnopt.wrapper
        assert False
    except:
        assert True
