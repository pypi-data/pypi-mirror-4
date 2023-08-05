.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.slicer.filtering.imagelabelcombine
=============================================


.. _nipype.interfaces.slicer.filtering.imagelabelcombine.ImageLabelCombine:


.. index:: ImageLabelCombine

ImageLabelCombine
-----------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/slicer/filtering/imagelabelcombine.py#L20>`_

Wraps command **/home/raid3/gorgolewski/software/slicer/Slicer --launch ImageLabelCombine **

title: Image Label Combine

category: Filtering

description: Combine two label maps into one

version: 0.1.0

documentation-url: http://wiki.slicer.org/slicerWiki/index.php/Documentation/4.1/Modules/ImageLabelCombine

contributor: Alex Yarmarkovich (SPL, BWH)

Inputs::

        [Mandatory]

        [Optional]
        InputLabelMap_A: (an existing file name)
                Label map image
        InputLabelMap_B: (an existing file name)
                Label map image
        OutputLabelMap: (a boolean or a file name)
                Resulting Label map image
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        first_overwrites: (a boolean)
                Use first or second label when both are present
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run

Outputs::

        OutputLabelMap: (an existing file name)
                Resulting Label map image
