.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.slicer.filtering.extractskeleton
===========================================


.. _nipype.interfaces.slicer.filtering.extractskeleton.ExtractSkeleton:


.. index:: ExtractSkeleton

ExtractSkeleton
---------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/slicer/filtering/extractskeleton.py#L22>`_

Wraps command **/home/raid3/gorgolewski/software/slicer/Slicer --launch ExtractSkeleton **

title: Extract Skeleton

category: Filtering

description: Extract the skeleton of a binary object.  The skeleton can be limited to being a 1D curve or allowed to be a full 2D manifold.  The branches of the skeleton can be pruned so that only the maximal center skeleton is returned.

version: 0.1.0.$Revision: 2104 $(alpha)

documentation-url: http://wiki.slicer.org/slicerWiki/index.php/Documentation/4.1/Modules/ExtractSkeleton

contributor: Pierre Seroul (UNC), Martin Styner (UNC), Guido Gerig (UNC), Stephen Aylward (Kitware)

acknowledgements: The original implementation of this method was provided by ETH Zurich, Image Analysis Laboratory of Profs Olaf Kuebler, Gabor Szekely and Guido Gerig.  Martin Styner at UNC, Chapel Hill made enhancements.  Wrapping for Slicer was provided by Pierre Seroul and Stephen Aylward at Kitware, Inc.

Inputs::

        [Mandatory]

        [Optional]
        InputImageFileName: (an existing file name)
                Input image
        OutputImageFileName: (a boolean or a file name)
                Skeleton of the input image
        args: (a string)
                Additional parameters to the command
        dontPrune: (a boolean)
                Return the full skeleton, not just the maximal skeleton
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        numPoints: (an integer)
                Number of points used to represent the skeleton
        pointsFile: (a string)
                Name of the file to store the coordinates of the central (1D) skeleton points
        type: ('1D' or '2D')
                Type of skeleton to create

Outputs::

        OutputImageFileName: (an existing file name)
                Skeleton of the input image
