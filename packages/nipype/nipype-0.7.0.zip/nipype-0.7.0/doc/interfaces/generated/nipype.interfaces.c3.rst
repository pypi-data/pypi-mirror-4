.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.c3
=============


.. _nipype.interfaces.c3.C3dAffineTool:


.. index:: C3dAffineTool

C3dAffineTool
-------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/c3.py#L27>`_

Wraps command **c3d_affine_tool**

Converts fsl-style Affine registration into ANTS compatible itk format

Example
>>> from nipype.interfaces.c3 import C3dAffineTool
>>> c3 = C3dAffineTool()
>>> c3.inputs.source_file = 'cmatrix.mat'
>>> c3.inputs.itk_transform = 'affine.txt'
>>> c3.inputs.fsl2ras = True
>>> c3.cmdline
'c3d_affine_tool -src cmatrix.mat -fsl2ras -oitk affine.txt'

Inputs::

        [Mandatory]

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        fsl2ras: (a boolean)
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        itk_transform: (a boolean or a file name)
                Export ITK transform.
        reference_file: (an existing file name)
        source_file: (an existing file name)
        transform_file: (an existing file name)

Outputs::

        itk_transform: (an existing file name)
