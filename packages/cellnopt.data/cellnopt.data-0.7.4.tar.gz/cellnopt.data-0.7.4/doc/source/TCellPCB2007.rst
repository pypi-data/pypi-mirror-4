
.. _TCellPCB2007:

TCellPCB2007
================


.. topic:: Description

    .. include:: ../../share/data/TCellPCB2007/description.txt




Download Data and Model
~~~~~~~~~~~~~~~~~~~~~~~~~

* To download the data, click on the following link :download:`download data   <../../share/data/TCellPCB2007/MD-TCellPCB2007.csv>`
* To download the model, click on the following link :download:`download model  <../../share/data/TCellPCB2007/PKN-TCellPCB2007.sif>`



PKN Model and pre-processed models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following plot shows the PKN, annotated, compressed and compressed and
expanded models. 

.. plot::
    :width: 60%
    :include-source:

    from cinapps.cno import *
    from cellnopt.data import cnodata
    plotPreProcessing(cnodata("PKN-TCellPCB2007.sif"), cnodata("MD-TCellPCB2007.csv"),"TCellPCB2007")

Here below is a high resoultion SVG pictures of the PKN model. 

.. _TCellPCB2007_highres:

.. graphviz:: TCellPCB2007.dot
    


