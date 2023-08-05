# -*- coding: utf-8 -*-
"""
pyrwt - A cython wrapper for the Rice Wavelet Toolbox
=====================================================

The `Rice Wavelet Toolbox <http://dsp.rice.edu/software/rice-wavelet-toolbox>`_
(**RWT**) is a collection of tools for 1D and 2D wavelet and filter bank design,
analysis, and processing. RWT was developed by the DSP Group in Rice
University and is commonly used in research in the field of signal processing.

**pyrwt** is a python wrapper around RWT. It enables using RWT from the
comfort of the Python scripting language. By using pyrwt, one can compare
side by side his Python algorithm with the algorithms of researches using
RWT with other scientific ecosystems.

pyrwt is available under the 
`Simplified BSD License <http://en.wikipedia.org/wiki/BSD_license#2-clause_license_.28.22Simplified_BSD_License.22_or_.22FreeBSD_License.22.29>`_.
RWT is available under the
`BSD License <http://en.wikipedia.org/wiki/BSD_license#4-clause_license_.28original_.22BSD_License.22.29>`_.

.. codeauthor:: Amit Aides <amitibo@tx.technion.ac.il>
"""

from cyrwt import dwt, idwt, rdwt, irdwt, dwtaxis, idwtaxis
