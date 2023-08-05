
.. _ToyMMB_FeedbackAnd:

ToyMMB_FeedbackAnd
=========================


.. topic:: Description

    .. include:: ../../share/data/ToyMMB_FeedbackAnd/description.txt




Download Data and Model
~~~~~~~~~~~~~~~~~~~~~~~~~

* To download the data, click on the following link :download:`download data   <../../share/data/ToyMMB_FeedbackAnd/MD-ToyMMB_FeedbackAnd.csv>`.
* To download the model, click on the following link :download:`download model  <../../share/data/ToyMMB_FeedbackAnd/PKN-ToyMMB_FeedbackAnd.sif>`.



PKN Model and pre-processed models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following plot shows the PKN, annotated, compressed and compressed and
expanded models. 

.. plot::
    :width: 60%
    :include-source:

    from cinapps.cno import *
    from cellnopt.data import cnodata
    plotPreProcessing(cnodata("PKN-ToyMMB_FeedbackAnd.sif"), cnodata("MD-ToyMMB_FeedbackAnd.csv"),"ToyMMB_FeedbackAnd")

Here below is a high resoultion SVG pictures of the PKN model. 

.. _ToyMMB_FeedbackAnd_highres:

.. graphviz:: ToyMMB_FeedbackAnd.dot
       

CNOlist view
~~~~~~~~~~~~~~~

.. plot::
    :width: 40%
    :include-source:

    from cinapps.cno import *
    from sampleModels.tools import get_data
    data = readMidas(get_data("ToyMMB_FeedbackAnd.csv"))
    cnolist = makeCNOlist(data)
    plotValueSignals(cnolist)
