
.. _ToyMMB:

ToyMMB
================


.. topic:: Description

    .. include:: ../../share/data/ToyMMB/description.txt




Download Data and Model
~~~~~~~~~~~~~~~~~~~~~~~~~

* To download the data, click on the following link :download:`download data   <../../share/data/ToyMMB/MD-ToyMMB.csv>`
* To download the model, click on the following link :download:`download model  <../../share/data/ToyMMB/PKN-ToyMMB.sif>`



PKN Model and pre-processed models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following plot shows the PKN, annotated, compressed and compressed and
expanded models. 

.. plot::
    :width: 60%
    :include-source:

    from cinapps.cno import *
    from cellnopt.data import cnodata
    plotPreProcessing(cnodata("PKN-ToyMMB.sif"), cnodata("MD-ToyMMB.csv"),"ToyMMB")

Here below is a high resoultion SVG pictures of the PKN model. 

.. _ToyMMB_highres:

.. graphviz:: ToyMMB.dot
    


.. CNOlist view
   ~~~~~~~~~~~~~~~

..    .. plot::
        :width: 40%
        :include-source:

..    from cinapps.cno import *
    from sampleModels.tools import get_data
    data = readMidas(get_data("ToyMMB.csv"))
    cnolist = makeCNOlist(data)
    plotValueSignals(cnolist)
