Prior knowledge Network (PKN) or protein-protein interactions and MIDAS CSV files provided in **cellnopt.data** are wither published data sets or data setes to be used for testing.

If you want to add a model/data, you will need to have access to the 
SVN and add them in the share/data directory. Please see existing 
directories for the layout. The new directory must contain:

 #. a model file (.sif extension)
 #. a data file (.csv extension in MIDAS format)
 #. a description file called description.txt

and possibly 

 * a data file using reactions/metabolites format like in CNA
 * a file called Type.NA if your model contains AND gates. This file is an
   attribute file for Cytoscape and is also used in the matlab version of CNO to
   import AND gates

The layout of the description file should be as faithful as possible to the
following layout so that it can be intrepreted by the documentation builder
automatically::

    **Name of the model (which is also the name of the directory)**

    Description of the model, its origins and main features. 

    :References:

    **authors of a paper**
    *title of the paper*
    Reference
    `Citation <http://www.pubmedcentral.nih.gov/articlerender.fcgi?artid=XXXXXXXXX>`_

    **authors of a paper**
    *title of the paper*
    Reference
    `Citation <http://www.pubmedcentral.nih.gov/articlerender.fcgi?artid=XXXXXXXXX>`_


Convention for directory name and filenames
----------------------------------------------

MIDAS files should start with "MD-" followed by a tag and the extension must be
".csv"::


    MD-TAG1.csv

SIF files should start with "PKN-" followed by a tag and the extension must be
".sif"::

    PKN-TAG1.sif

TAG1 is a label corresponding to the model. Variant of a file should have second tag as follows::

    PKN-TAG1_TAG2.sif

A compressed and expanded model to be saved could be saved as follows::

    CEN-Tag1.sif




