.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.slicer.utilities
===========================


.. _nipype.interfaces.slicer.utilities.EMSegmentTransformToNewFormat:


.. index:: EMSegmentTransformToNewFormat

EMSegmentTransformToNewFormat
-----------------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/slicer/utilities.py#L19>`_

Wraps command **/home/raid3/gorgolewski/software/slicer/Slicer --launch EMSegmentTransformToNewFormat **

title:
  Transform MRML Files to New EMSegmenter Standard


category:
  Utilities


description:
  Transform MRML Files to New EMSegmenter Standard

Inputs::

        [Mandatory]

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        inputMRMLFileName: (an existing file name)
                Active MRML scene that contains EMSegment algorithm parameters in the format before
                3.6.3 - please include absolute  file name in path.
        outputMRMLFileName: (a boolean or a file name)
                Write out the MRML scene after transformation to format 3.6.3 has been made. - has to be
                in the same directory as the input MRML file due to Slicer Core bug  - please include
                absolute  file name in path
        templateFlag: (a boolean)
                Set to true if the transformed mrml file should be used as template file

Outputs::

        outputMRMLFileName: (an existing file name)
                Write out the MRML scene after transformation to format 3.6.3 has been made. - has to be
                in the same directory as the input MRML file due to Slicer Core bug  - please include
                absolute  file name in path
