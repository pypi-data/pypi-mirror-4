.. _LiverDREAM:

LiverDREAM
=============


.. topic:: Description

    .. include:: ../../share/data/LiverDREAM/description.txt



Download Data and Model
~~~~~~~~~~~~~~~~~~~~~~~~~

* To download the data, click on the following link :download:`download data   <../../share/data/LiverDREAM/LiverDREAM.csv>`.
* To download the model, click on the following link :download:`download model  <../../share/data/LiverDREAM/LiverDREAM.sif>`.


PKN Model and pre-processed models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following plot shows the PKN, annotated, compressed and compressed and
expanded models. 

.. plot::
    :width: 60%
    :include-source:

    from cinapps.cno import *
    from cellnopt.data import cnodata
    plotPreProcessing(cnodata("LiverDREAM.sif"),cnodata("LiverDREAM.csv"),"LiverDREAM")

Here below is a high resoultion SVG pictures of the PKN model. 

.. _LiverDREAM_highres:

.. graphviz:: LiverDREAM.dot




.. CNOlist view
    ~~~~~~~~~~~~~~~

..     .. plot::
        :width: 40%
        :include-source:
    
        from cinapps.cno import *
        from sampleModels.tools import get_data
        data = readMidas(get_data("LiverDREAM.csv"))
        cnolist = makeCNOlist(data)
        plotValueSignals(cnolist)
