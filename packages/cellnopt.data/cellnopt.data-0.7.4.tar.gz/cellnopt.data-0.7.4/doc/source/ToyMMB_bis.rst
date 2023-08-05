
.. _ToyMMB_bis:

ToyMMB_bis
================


.. topic:: Description

    .. include:: ../../share/data/ToyMMB_bis/description.txt




Download Data and Model
~~~~~~~~~~~~~~~~~~~~~~~~~

* To download the data, click on the following link :download:`download data   <../../share/data/ToyMMB_bis/MD-ToyMMB_bis.csv>`
* To download the model, click on the following link :download:`download model  <../../share/data/ToyMMB_bis/PKN-ToyMMB_bis.sif>`



PKN Model and pre-processed models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following plot shows the PKN, annotated, compressed and compressed and
expanded models. 

.. plot::
    :width: 60%
    :include-source:

    from cinapps.cno import *
    from cellnopt.data import cnodata
    plotPreProcessing(cnodata("PKN-ToyMMB_bis.sif"), cnodata("MD-ToyMMB_bis.csv"),"ToyMMB_bis")

Here below is a high resoultion SVG pictures of the PKN model. 

.. _ToyMMB_bis_highres:

.. graphviz:: ToyMMB_bis.dot
    


.. CNOlist view
    ~~~~~~~~~~~~~~~

.. .. plot::
    :width: 40%
    :include-source:

..    from cinapps.cno import *
    from sampleModels.tools import get_data
    data = readMidas(get_data("ToyMMB_bis.csv"))
    cnolist = makeCNOlist(data)
    plotValueSignals(cnolist)
