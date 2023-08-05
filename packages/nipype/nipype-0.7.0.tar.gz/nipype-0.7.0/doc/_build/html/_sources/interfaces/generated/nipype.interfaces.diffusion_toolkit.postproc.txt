.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.diffusion_toolkit.postproc
=====================================


.. _nipype.interfaces.diffusion_toolkit.postproc.SplineFilter:


.. index:: SplineFilter

SplineFilter
------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/diffusion_toolkit/postproc.py#L26>`_

Wraps command **spline_filter**


Inputs::

        [Mandatory]
        step_length: (a float)
                in the unit of minimum voxel size
        track_file: (an existing file name)
                file containing tracks to be filtered

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        output_file: (a file name, nipype default value: spline_tracks.trk)
                target file for smoothed tracks

Outputs::

        smoothed_track_file: (an existing file name)
