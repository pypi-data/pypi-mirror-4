.. _ToyPCB:


ToyPCB
==============


.. topic:: Description

    .. include:: ../../share/data/ToyPCB/description.txt



Download Data and Model
---------------------------

* To download the data, click on the following link :download:`download data   <../../share/data/ToyPCB/MD-ToyPCB.csv>`.
* To download the model, click on the following link :download:`download model  <../../share/data/ToyPCB/PKN-ToyPCB.sif>`.



PKN Model and pre-processed models
---------------------------------------

The following plot shows the PKN, annotated, compressed and compressed and
expanded models. 

.. plot::
    :width: 60%
    :include-source:

    from cinapps.cno import *
    from cellnopt.data import cnodata
    plotPreProcessing(cnodata("PKN-ToyPCB.sif"), cnodata("MD-ToyPCB.csv"),"ToyPCB")

Here below is a high resoultion SVG pictures of the PKN model. 

.. _ToyPCB_highres:

.. graphviz:: ToyPCB.dot


.. CNOlist view
   -----------------

.. .. plot::
    :width: 40%
    :include-source:

..    from cinapps.cno import *
    from cellnopt.data import cnodata
    data = readMidas(get_data("ToyPCB.csv"))
    cnolist = makeCNOlist(data)
    plotValueSignals(cnolist)
