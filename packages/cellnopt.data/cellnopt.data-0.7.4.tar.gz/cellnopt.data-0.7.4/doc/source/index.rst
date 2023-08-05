

###################################
CELLNOPT.DATA (a.k.a sampleModels)
###################################

.. sidebar:: sampleModels

    :Version: |version|
    :Date: |today|
    :Author: **Thomas Cokelaer**



Overview
############


.. container:: twocol

    .. container:: leftside

        The package `cellnopt.data <http://pypi.python.org/pypi/cellnopt.data/>`_
        provides data sets and models used in various references that involve
        `CellNOpt software <http://www.cellnopt.org>`_.
        It also provides tools to ease the access to these data sets and models.
        For instance, the following code returns the path of the model *PKN-ToyMMB.sif* 
        that is installed in your system (installed with this package)::

            from cellnopt.data import cnodata
            filename = cnodata("PKN-ToyMMB.sif")

        .. seealso:: :ref:`quickstart`

        If you want to add your own pair of data/model in this package, please let us know (cnodev@ebi.ac.uk).
        If you have access to the SVN repository, see the :ref:`howto_add_a_model` section.

    .. container:: rightside

        .. image:: _static/network.png
            :width: 90%



.. raw:: html

    <div style="clear:both"/>

.. note:: files and images corresponding to the data sets and models can be found in the summary section together with references.





Installation
###################

If you only want to get/download a model or MIDAS data set, there is no need to install **cellnopt.data**: just browse those pages. 

Would you still want to download the package in its integrity, **cellnopt.data** is available on `PyPi <http://pypi.python.org/>`_. The 
following command should install the package and its dependencies automatically::

    easy_install cellnopt.data


Summary of the model/data available
######################################

.. include:: summary.rst



.. toctree::
    :numbered:
    :maxdepth: 1
    :hidden:

    quickstart.rst
    summary.rst
    LiverDREAM.rst
    ExtLiverPCB.rst
    ExtLiverBMC2012.rst
    ExtLiverPriHu-MCP2010.rst
    EGFR-ErbB_PCB2009.rst
    TCellPCB2007.rst
    ToyMSB2009.rst
    ToyPCB.rst
    ToyMMB.rst
    ToyMMB_bis.rst
    ToyMMB_Feedback.rst
    ToyMMB_FeedbackAnd.rst
    ToyPB.rst



References
##################


.. toctree::
    :maxdepth: 2
    :numbered:


    addmodel.rst
    references
