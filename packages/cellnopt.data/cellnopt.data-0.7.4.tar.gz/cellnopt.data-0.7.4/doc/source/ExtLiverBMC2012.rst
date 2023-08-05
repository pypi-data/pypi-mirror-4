.. _ExtLiverBMC2012:



ExtLiverBMC2012
=================


.. topic:: Description

    .. include:: ../../share/data/ExtLiverBMC2012/description.txt



Download Data and Model
~~~~~~~~~~~~~~~~~~~~~~~~~



* :download:`download model PKN-ExtLiverBMC2012.sif  <../../share/data/ExtLiverBMC2012/PKN-ExtLiverBMC2012.sif>` in the same format as :ref:`ExtLiverPCB`.
* :download:`download model PKN-ExtLiverMSBmodUP.sif  <../../share/data/ExtLiverBMC2012/PKN-ExtLiverBMC2012.sif>`, which is the same as above but with uniprot IDs.
* :download:`download data MD-ExtLiverPCB.csv  <../../share/data/ExtLiverBMC2012/MD-ExtLiverPCB.csv>` identical to the data in :ref:`ExtLiverPCB`.
* :download:`download data MCP_HepG2mod4.csv  <../../share/data/ExtLiverBMC2012/MD-ExtLiverPCB.csv>` (uniprot IDS).
* :download:`download data MCP_PriHumod5.csv  <../../share/data/ExtLiverBMC2012/MD-ExtLiverPCB.csv>` (uniprot IDS).



PKN Model and pre-processed models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following plot shows the PKN, annotated, compressed and compressed and
expanded models. 

.. plot::
    :width: 60%
    :include-source:

    from cinapps.cno import *
    from cellnopt.data import cnodata
    plotPreProcessing(cnodata("PKN-ExtLiverBMC2012.sif"),cnodata("MD-ExtLiverPCB.csv"),"ExtLiverBMC2012")

Here below is a high resoultion SVG pictures of the PKN model. 

.. _ExtLiver_highres:

.. graphviz:: ExtLiverBMC2012.dot


.. CNOlist view
   ~~~~~~~~~~~~~~~

.. .. plot::
    :width: 40%
    :include-source:

..    from cinapps.cno import *
    from sampleModels.tools import get_share/data
    share/data = readMidas(get_share/data("ExtLiverMSB2012.csv"))
    cnolist = makeCNOlist(share/data)
    plotValueSignals(cnolist)


.. .. graphviz:: ../ExtLiverMSB2012.dot
