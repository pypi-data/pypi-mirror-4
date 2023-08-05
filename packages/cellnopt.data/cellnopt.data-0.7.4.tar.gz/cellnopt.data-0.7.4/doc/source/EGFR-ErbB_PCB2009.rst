.. _EGFR-ErbB_PCB2009:

EGFR-ErbB_PCB2009
=======================


.. topic:: Description

    .. include:: ../../share/data/EGFR-ErbB_PCB2009/description.txt



Download Data and Model
---------------------------

* To download the data, click on the following link :download:`download data   <../../share/data/EGFR-ErbB_PCB2009/EGFR-ErbB_PCB2009.csv>`.
* To download the model, click on the following link :download:`download model  <../../share/data/EGFR-ErbB_PCB2009/EGFR-ErbB_PCB2009.sif>`.



PKN Model and pre-processed models
---------------------------------------

This model is quite large and contains a lot of a priori and gates. The
following plot was generated using the following code::

    from cinapps.cno import *
    from cellnopt.data import cnodata
    filename = "EGFR-ErbB_PCB2009"
    model = readSIF(cnodata((filename + ".sif"))
    cnolist = CNOlist(cnodata(filename + ".csv"))

    # prevent plotting of the R figure, caught and saved in a file
    #from rpy2.robjects.packages import importr
    #grdevices = importr('grDevices')
    #grdevices.png(file=filename + ".png", width=1024, height=1024)
    plotModel(model, cnolist=cnolist, filename=filename)
    #grdevices.dev_off()

    # save 
    import os
    os.system("dot -Tpng %s.dot -Gsize=30,30 -o %s.png " %(filename, filename))
    os.system("dot -Tsvg %s.dot -Gsize=30,30 -o %s.svg " %(filename,filename))
    


.. image:: ../../share/data/EGFR-ErbB_PCB2009/EGFR-ErbB_PCB2009.svg
    :width: 60%

.. .. graphviz:: ../../data/EGFR-ErbB_PCB2009/EGFR-ErbB_PCB2009.dot




