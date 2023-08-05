
.. _ToyMSB2009:

ToyMSB2009
================


.. topic:: Description

    .. include:: ../../share/data/ToyMSB2009/description.txt




Download Data and Model
~~~~~~~~~~~~~~~~~~~~~~~~~

* To download the data, click on the following link :download:`download data   <../../share/data/ToyMSB2009/MD-ToyMSB2009.csv>`
* To download the model, click on the following link :download:`download model  <../../share/data/ToyMSB2009/PKN-ToyMSB2009.sif>`



PKN Model and pre-processed models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following plot shows the PKN, annotated, compressed and compressed and
expanded models. 

.. plot::
    :width: 60%
    :include-source:

    from cinapps.cno import *
    from cellnopt.data import cnodata
    plotPreProcessing(cnodata("PKN-ToyMSB2009.sif"), cnodata("MD-ToyMSB2009.csv"),"ToyMSB2009")

Here below is a high resoultion SVG pictures of the PKN model. 

.. _ToyMSB2009_highres:

.. graphviz:: ToyMSB2009.dot
    


.. CNOlist view
.. ~~~~~~~~~~~~~~~

.. .. plot::
    :width: 40%
    :include-source:

..    from cinapps.cno import *
    from sampleModels.tools import get_data
    data = readMidas(get_data("MD-Toy-MSB2009.csv"))
    cnolist = makeCNOlist(data)
    plotValueSignals(cnolist)
