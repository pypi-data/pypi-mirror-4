.. _LiverMSB2009:



LiverMSB2009
=============


.. topic:: Description

    .. include:: ../../share/data/LiverMSB2009/description.txt



Download Data and Model
~~~~~~~~~~~~~~~~~~~~~~~~~

* To download the share/data, click on the following link :download:`download share/data   <../../share/data/LiverMSB2009/MD-LiverMSB2009.csv>`.
* To download the model, click on the following link :download:`download model  <../../share/data/LiverMSB2009/PKN-LiverMSB2009.sif>`.



PKN Model and pre-processed models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following plot shows the PKN, annotated, compressed and compressed and
expanded models. 

.. plot::
    :width: 60%
    :include-source:

    from cellnopt.misc import *
    from cellnopt.data import cnodata
    plotPreProcessing(cnodata("PKN-LiverMSB2009.sif"),cnodata("MD-LiverMSB2009.csv"),"LiverMSB2009")

Here below is a high resolution SVG pictures of the PKN model. 

.. _ExtLiver_highres:

.. graphviz:: LiverMSB2009.dot


.. CNOlist view
   ~~~~~~~~~~~~~~~

.. .. plot::
    :width: 40%
    :include-source:

..    from cellnopt.misc import *
    from sampleModels.tools import get_share/data
    share/data = readMidas(get_share/data("ExtLiverMSB2009.csv"))
    cnolist = makeCNOlist(share/data)
    plotValueSignals(cnolist)


.. .. graphviz:: ../ExtLiverMSB2009.dot
