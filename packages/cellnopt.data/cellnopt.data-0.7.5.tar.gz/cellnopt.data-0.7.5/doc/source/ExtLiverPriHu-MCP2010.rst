.. _ExtLiverPriHu-MCP2010:



ExtLiverPriHu-MCP2010
============================


.. topic:: Description

    .. include:: ../../share/data/ExtLiverPriHu-MCP2010/description.txt



Download Data and Model
~~~~~~~~~~~~~~~~~~~~~~~~~

* To download the raw data, click on the following link :download:`download data   <../../share/data/ExtLiverPriHu-MCP2010/MD-ExtLiverPriHu-MCP2010-mod5.csv>`.
* To download the normalised data, click on the following link :download:`download model  <../../share/data/ExtLiverPriHu-MCP2010/MD-ExtLiverPriHu-MCP2010-mod5-normed.csv>`.
* To download the model, click on the following link :download:`download model  <../../share/data/ExtLiverPriHu-MCP2010/PKN-ExtLiverPriHu-MCP2010.sif>`.





PKN Model and pre-processed models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following plot shows the PKN, annotated, compressed and compressed and
expanded models. 

.. plot::
    :width: 60%
    :include-source:

    from cinapps.cno import *
    from cellnopt.data import cnodata
    plotPreProcessing(cnodata("PKN-ExtLiverPriHu-MCP2010.sif"), cnodata("MD-ExtLiverPriHu-MCP2010-mod5-normed.csv"),"ExtLiverPriHu-MCP2010")

Here below is a high resoultion SVG pictures of the PKN model. 

.. _ExtLiver_highres:

.. graphviz:: ExtLiverPriHu-MCP2010.dot




.. .. graphviz:: ../ExtLiverPriHu-MCP2010.dot
