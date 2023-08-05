.. _ToyPB:


ToyPB
==============


.. topic:: Description

    .. include:: ../../share/data/ToyPB/description.txt



Download Data and Model
---------------------------

* To download the data, click on the following link :download:`download data   <../../share/data/ToyPB/MD-ToyPB.csv>`.
* To download the model, click on the following link :download:`download model  <../../share/data/ToyPB/PKN-ToyPB.sif>`.




PKN Model and pre-processed models
---------------------------------------


The following plot shows the PKN, annotated, compressed and compressed and
expanded models. 

.. plot::
    :width: 60%
    :include-source:

    from cinapps.cno import *
    from cellnopt.data import cnodata
    plotPreProcessing(cnodata("PKN-ToyPB.sif"),cnodata("MD-ToyPB.csv"),"ToyPB")


Here below is a high resoultion SVG pictures of the PKN model. 

.. _ToyPB_highres:

.. graphviz:: ToyPB.dot



.. CNOlist view
   -----------------

.. .. plot::
    :width: 40%
    :include-source:

..     from cnolab.wrapper import *
    from cinapps.cno import plotValueSignals
    from sampleModels.tools import get_data
    data = readMIDAS(get_data("ToyPB.csv"))
    cnolist = makeCNOlist(data)
    plotValueSignals(cnolist)
