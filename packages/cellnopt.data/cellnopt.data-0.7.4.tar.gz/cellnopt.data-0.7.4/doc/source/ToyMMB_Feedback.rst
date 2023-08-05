.. _ToyMMB_Feedback:



ToyMMB_Feedback
=========================


.. topic:: Description

    .. include:: ../../share/data/ToyMMB_Feedback/description.txt




Download Data and Model
~~~~~~~~~~~~~~~~~~~~~~~~~

* To download the data, click on the following link :download:`download data   <../../share/data/ToyMMB_Feedback/MD-ToyMMB_Feedback.csv>`. Note also you can get :download:`download data variant 2  <../../share/data/ToyMMB_Feedback/MD-ToyMMB_Feedback2.csv>` and  :download:`download data variant 3  <../../share/data/ToyMMB_Feedback/MD-ToyMMB_Feedback3.csv>`.
* To download the model, click on the following link :download:`download model  <../../share/data/ToyMMB_Feedback/PKN-ToyMMB_Feedback.sif>`.

There is also a data set to play with steady states(2 time): 

* To download the data, click on the following link :download:`download data   <../../share/data/ToyMMB_Feedback/MD-ToyMMB_Feedback2.csv>`.


PKN Model and pre-processed models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following plot shows the PKN, annotated, compressed and compressed and
expanded models. 

.. plot::
    :width: 60%
    :include-source:

    from cinapps.cno import *
    from cellnopt.data import cnodata
    plotPreProcessing(cnodata("PKN-ToyMMB_Feedback.sif"), cnodata("MD-ToyMMB_Feedback.csv"),"ToyMMB_Feedback")

Here below is a high resoultion SVG pictures of the PKN model. 

.. _ToyMMB_Feedback_highres:

.. graphviz:: ToyMMB_Feedback.dot
       

.. CNOlist view
.. ~~~~~~~~~~~~~~~

.. .. plot::
    :width: 40%
    :include-source:

..    from cinapps.cno import *
    from sampleModels.tools import get_data
    data = readMidas(get_data("ToyMMB_fEedback.csv"))
    cnolist = makeCNOlist(data)
    plotValueSignals(cnolist)
