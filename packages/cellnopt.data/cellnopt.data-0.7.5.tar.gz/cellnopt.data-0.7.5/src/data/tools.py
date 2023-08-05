# -*- python -*-
#
#  This file is part of the CNO software
#
#  Copyright (c) 2011-2012 - EBI
#
#  File author(s): Thomas Cokelaer <cokelaer@ebi.ac.uk>
#
#  Distributed under the GPLv2 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-2.0.html
#
#  CNO website: www.cellnopt.org
#
##############################################################################
"""Common tools to get the correct filename and pathname. """
from os.path import join as pj
import os
import glob
import urllib

__all__ = ['cnodata', 'checksum']

import logging
logging.basicConfig(level=logging.INFO)


# You can add as much url as desired in baseurls
baseurls = ["http://www.ebi.ac.uk/~cokelaer/cno/doc/sampleModels/_downloads/"]


def cnodata(filename, verbose=True, local=False):
    """Returns the full pathname of a file distributed with sampleModels

    .. doctest::

        >>> from cellnopt.data import cnodata
        >>> filename = cnodata("ToyModelPCB.sif") #doctest: +SKIP

    """
    if filename.endswith(".sif")==False and filename.endswith(".csv")==False:
        raise ValueError("webdata ease access to SIF or CSV format only (small caps extension)")

    if os.path.isfile(filename):
        return filename


    # by default, search for a file on the web but the use can overwrite that
    # behaviour
    if local == True:
        pass
    else:
        try:
            filename = _get_data(filename, verbose)
            # if it cannot be found on the web, try locally
        except IOError:
            try:
                filename = _webdata(filename, verbose)
            # if even locally it cannot be found, raise an error
            except Exception:
                raise Exception
    return filename


def _webdata(filename, verbose):
    """Search for a file in the samplemodels repository on the web.

    """
    # try all URL in baseurls
    for url in baseurls:
        url += os.sep + filename
        a = urllib.urlopen(url)

        if a.getcode() == 200:
            local_filename, obj = urllib.urlretrieve(url)
            logging.info("Found %s in %s" % (filename, url))
            return local_filename
        else:
            if verbose==True:
                import warnings
                logging.warning("Could not find %s in %s" % (filename, url))
            raise IOError


def _get_data(filename, verbose=True):
    if verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.ERROR)

    try:
        logging.info("Trying local sampleModels")
        import sampleModels
        from sampleModels import get_data
        filename = get_data(filename, verbose)
        logging.info("Found with get_data from sampleModels")
        return filename
    except ImportError, e:
        print e
        logging.warning("sampleModels not installed")
    except:
        pass 

    try:
        logging.info("Trying to use cellnopt.wrapper.")
        from cellnopt.wrapper import get_data
        filename = get_data(filename)
        return filename
    except ImportError, e:
        print e
        logging.warning("cellnopt.wrapper not installed")
    except:
        raise IOError("file could not be found with sampleModels or cellnopt.wrapper.")


def checksum(filename):
    """Simple checksum on a cnodata file


    :param filename: a file to be found in sampleModels or cellnopt.wrapper

    >>> from cellnopt.data import checksum
    >>> cs = checksum(cnodata("PKN-ToyPCB.sif"))

    """
    import hashlib
    filename_path = cnodata(filename)
    checksum = hashlib.md5(file(filename_path, 'r').read()).digest()
    return checksum
