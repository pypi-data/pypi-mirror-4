.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.slicer.filtering.checkerboardfilter
==============================================


.. _nipype.interfaces.slicer.filtering.checkerboardfilter.CheckerBoardFilter:


.. index:: CheckerBoardFilter

CheckerBoardFilter
------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/slicer/filtering/checkerboardfilter.py#L20>`_

Wraps command **/home/raid3/gorgolewski/software/slicer/Slicer --launch CheckerBoardFilter **

title: CheckerBoard Filter

category: Filtering

description: Create a checkerboard volume of two volumes. The output volume will show the two inputs alternating according to the user supplied checkerPattern. This filter is often used to compare the results of image registration. Note that the second input is resampled to the same origin, spacing and direction before it is composed with the first input. The scalar type of the output volume will be the same as the input image scalar type.

version: 0.1.0.$Revision: 19608 $(alpha)

documentation-url: http://wiki.slicer.org/slicerWiki/index.php/Documentation/4.1/Modules/CheckerBoard

contributor: Bill Lorensen (GE)

acknowledgements: This work is part of the National Alliance for Medical Image Computing (NAMIC), funded by the National Institutes of Health through the NIH Roadmap for Medical Research, Grant U54 EB005149.

Inputs::

        [Mandatory]

        [Optional]
        args: (a string)
                Additional parameters to the command
        checkerPattern: (an integer)
                The pattern of input 1 and input 2 in the output image. The user can specify the number
                of checkers in each dimension. A checkerPattern of 2,2,1 means that images will
                alternate in every other checker in the first two dimensions. The same pattern will be
                used in the 3rd dimension.
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        inputVolume1: (an existing file name)
                First Input volume
        inputVolume2: (an existing file name)
                Second Input volume
        outputVolume: (a boolean or a file name)
                Output filtered

Outputs::

        outputVolume: (an existing file name)
                Output filtered
