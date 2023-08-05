.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.nipy.preprocess
==========================


.. _nipype.interfaces.nipy.preprocess.ComputeMask:


.. index:: ComputeMask

ComputeMask
-----------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/nipy/preprocess.py#L40>`_

Inputs::

        [Mandatory]
        mean_volume: (an existing file name)
                mean EPI image, used to compute the threshold for the mask

        [Optional]
        M: (a float)
                upper fraction of the histogram to be discarded
        cc: (a boolean)
                Keep only the largest connected component
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        m: (a float)
                lower fraction of the histogram to be discarded
        reference_volume: (an existing file name)
                reference volume used to compute the mask. If none is give, the mean volume is used.

Outputs::

        brain_mask: (an existing file name)

.. _nipype.interfaces.nipy.preprocess.FmriRealign4d:


.. index:: FmriRealign4d

FmriRealign4d
-------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/nipy/preprocess.py#L109>`_

Simultaneous motion and slice timing correction algorithm

This interface wraps nipy's FmriRealign4d algorithm [1]_.

Examples
~~~~~~~~
>>> from nipype.interfaces.nipy.preprocess import FmriRealign4d
>>> realigner = FmriRealign4d()
>>> realigner.inputs.in_file = ['functional.nii']
>>> realigner.inputs.tr = 2
>>> realigner.inputs.slice_order = range(0,67)
>>> res = realigner.run() # doctest: +SKIP

References
~~~~~~~~~~
.. [1] Roche A. A four-dimensional registration algorithm with        application to joint correction of motion and slice timing        in fMRI. IEEE Trans Med Imaging. 2011 Aug;30(8):1546-54. DOI_.

.. _DOI: http://dx.doi.org/10.1109/TMI.2011.2131152

Inputs::

        [Mandatory]
        in_file
                File to realign
        tr: (a float)
                TR in seconds

        [Optional]
        between_loops: (an integer, nipype default value: [5])
                loops used to                                                           realign
                different                                                           runs
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        loops: (an integer, nipype default value: [5])
                loops within each run
        slice_order: (a list of items which are an integer)
                0 based slice order
                requires: time_interp
        speedup: (an integer, nipype default value: [5])
                successive image                                   sub-sampling factors
                for acceleration
        start: (a float, nipype default value: 0.0)
                time offset into TR to align slices to
        time_interp: (True)
                Assume smooth changes across time e.g.,                     fmri series. If you don't
                want slice timing                      correction set this to undefined
                requires: slice_order
        tr_slices: (a float)
                TR slices
                requires: time_interp

Outputs::

        out_file: (an existing file name)
                Realigned files
        par_file: (an existing file name)
                Motion parameter files
