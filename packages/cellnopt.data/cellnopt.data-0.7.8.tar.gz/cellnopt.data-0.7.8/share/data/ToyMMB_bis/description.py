# -*- python -*-
#
#  This file is part of the CNO software
#
#  Copyright (c) 2011-2012 - EBI
#
#  File author(s): Thomas Cokelaer <cokelaer@ebi.ac.uk>
#
#  Distributed under the GPLv2 License.
#  See accompanying file LICENSE.txt or copy at
#      http://www.gnu.org/licenses/gpl-2.0.html
#
#  CNO website: http://www.ebi.ac.uk/saezrodriguez/cno
#
##############################################################################
name = "ToyMMB_bis"
description = """This model is the same as ToyMMB with an additional link from PI3k to NFkB"""
reference = {
        'authors': "M. K. Morris, I. Melas, J. Saez-Rodriguez.",
        'title': "Construction of cell type-specific logic models of signaling networks using CellNetOptimizer.",
        'journal': "to appear in Methods in Molecular Biology:Computational Toxicology, Ed.  B. Reisfeld and A. Mayeno, Humana Press."
}

further_references = {
}

# comments in RST format
comments = ""


aliases = {
    "PKN-ToyMMB_bis.sif": ["ToyModelMMB_bis.sif", "ToyModelMKM_bis.sif"],
    "MD-ToyMMB_bis.csv": ["ToyModelMMB_bis.csv", "ToyModelMKM_bis.csv"]}





