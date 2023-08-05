.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.dynamic_slicer
=========================


.. _nipype.interfaces.dynamic_slicer.SlicerCommandLine:


.. index:: SlicerCommandLine

SlicerCommandLine
-----------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/dynamic_slicer.py#L14>`_

Wraps command **Slicer3**

Experimental Slicer wrapper. Work in progress.

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
        module: (a string)
                name of the Slicer command line module you want to use

Outputs::

        None
