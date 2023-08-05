.. _quickstart:

How to retrieve the path to a data or model file
##################################################

quickstart
===========

The following code should return a path to a temporary file corresponding to the
requested filename::

    from cellnopt.data import cnodata
    temp_filename = cnodata("ToyModelPCB.sif")

that can be used later on. For instance with :ref:`cellnopt.wrapper.readSIF`::

    from cellnopt.wrapper import readSIF
    readSIF(temp_filename)

motivation
===========

In cellnopt.wrapper, where the wrapper of CellNOptR occurs, you already have few
model and data sets. It is a good starting point. For example::

    >>> from cellnopt.wrapper import *
    >>> get_data("ToyModel.sif")

However, there are only a few model and data sets. A more complete set of published models is stored in an independent SVN repository called
sampleModels that is only accessible from EBI sysbiomed repository::

    >>> from sampleModels import get_data
    >>> get_data("ToyModelPCB.sif")

The issue here is that there are 2 get_data functions,  which is a bit confusing.
Moreover, you must have access to the SVN to get the model and data sets from
sampleModels.

Yet, the documentation together with the data and model is
published  `sampleModels page <http://www.ebi.ac.uk/~cokelaer/cno/doc/sampleModels/>`_ on a regular basis.

**cellnopt.data** main objective is to ease the access to data hence the unique
function :func:`cnodata`. 

Here are the steps follows by cnodata:

    #. tries in the local directory (not very useful... but in case it is already there.)
    #. tries to find sampleModels package locally and get the file from that package. 
    #. tries to obtain the data from the sampleModels web page. 
    #. if sampleModels is not installed, tries to find it in cellnopt.wrapper (just a few model/data are available there).

