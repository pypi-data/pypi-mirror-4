.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.afni.preprocess
==========================


.. _nipype.interfaces.afni.preprocess.Allineate:


.. index:: Allineate

Allineate
---------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/afni/preprocess.py#L797>`_

Wraps command **3dAllineate**

Program to align one dataset (the 'source') to a base dataset

For complete details, see the `3dAllineate Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dAllineate.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> allineate = afni.Allineate()
>>> allineate.inputs.in_file = 'functional.nii'
>>> allineate.inputs.out_file= 'functional_allineate.nii'
>>> allineate.inputs.matrix= 'cmatrix.mat'
>>> res = allineate.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dAllineate

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        matrix: (an existing file name)
                matrix to align input file
        out_file: (a file name, nipype default value: %s_allineate)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        prefix: (a string)
                output image prefix
        suffix: (a string)
                output image suffix

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.AutoTcorrelate:


.. index:: AutoTcorrelate

AutoTcorrelate
--------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/afni/preprocess.py#L326>`_

Wraps command **3dAutoTcorrelate**

Computes the correlation coefficient between the time series of each
pair of voxels in the input dataset, and stores the output into a
new anatomical bucket dataset [scaled to shorts to save memory space].

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> corr = afni.AutoTcorrelate()
>>> corr.inputs.in_file = 'functional.nii'
>>> corr.inputs.out_file = 'my_similarity_matrix.1D'
>>> corr.inputs.polort = -1
>>> corr.inputs.eta2 = True
>>> corr.inputs.mask = 'mask.nii'
>>> corr.inputs.mask_only_targets = True
>>> corr.cmdline # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
'3dAutoTcorrelate -eta2 -mask mask.nii -mask_only_targets -prefix ...my_similarity_matrix.1D -polort -1 functional.nii'
>>> res = corr.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                timeseries x space (volume or surface) file

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        eta2: (a boolean)
                eta^2 similarity
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        mask: (an existing file name)
                mask of voxels
        mask_only_targets: (a boolean)
                use mask only on targets voxels
        out_file: (a file name, nipype default value: %s_similarity_matrix.1D)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        polort: (an integer)
                Remove polynomical trend of order m or -1 for no detrending
        prefix: (a string)
                output image prefix
        suffix: (a string)
                output image suffix

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.Automask:


.. index:: Automask

Automask
--------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/afni/preprocess.py#L503>`_

Wraps command **3dAutomask**

Create a brain-only mask of the image using AFNI 3dAutomask command

For complete details, see the `3dAutomask Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dAutomask.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> automask = afni.Automask()
>>> automask.inputs.in_file = 'functional.nii'
>>> automask.inputs.dilate = 1
>>> automask.inputs.outputtype = "NIFTI"
>>> automask.cmdline
'3dAutomask -apply_prefix functional_masked.nii -dilate 1 -prefix functional_mask.nii functional.nii'
>>> res = automask.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dAutomask

        [Optional]
        apply_mask: (a file name)
                output file from 3dAutomask
        apply_suffix: (a string)
                out_file suffix
        args: (a string)
                Additional parameters to the command
        brain_file: (a file name, nipype default value: %s_masked)
                output file from 3dAutomask
        clfrac: (a float)
                sets the clip level fraction (must be 0.1-0.9). A small value will tend to make the mask
                larger [default = 0.5].
        dilate: (an integer)
                dilate the mask outwards
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        erode: (an integer)
                erode the mask inwards
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        mask_suffix: (a string)
                out_file suffix
        out_file: (a file name, nipype default value: %s_mask)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        prefix: (a string)
                output image prefix
        suffix: (a string)
                output image suffix

Outputs::

        brain_file: (an existing file name)
                brain file (skull stripped)
        out_file: (an existing file name)
                mask file

.. _nipype.interfaces.afni.preprocess.BrickStat:


.. index:: BrickStat

BrickStat
---------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/afni/preprocess.py#L1045>`_

Wraps command **3dBrickStat**

Compute maximum and/or minimum voxel values of an input dataset

For complete details, see the `3dBrickStat Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dBrickStat.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> brickstat = afni.BrickStat()
>>> brickstat.inputs.in_file = 'functional.nii'
>>> brickstat.inputs.mask = 'skeleton_mask.nii.gz'
>>> brickstat.inputs.min = True
>>> res = brickstat.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dmaskave

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        mask: (an existing file name)
                -mask dset = use dset as mask to include/exclude voxels
        min: (a boolean)
                print the minimum value in dataset
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype

Outputs::

        min_val: (a float)
                output

.. _nipype.interfaces.afni.preprocess.Calc:


.. index:: Calc

Calc
----

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/afni/preprocess.py#L1203>`_

Wraps command **3dcalc**

This program does voxel-by-voxel arithmetic on 3D datasets

For complete details, see the `3dcalc Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dcalc.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> calc = afni.Calc()
>>> calc.inputs.in_file_a = 'functional.nii'
>>> calc.inputs.in_file_b = 'functional2.nii'
>>> calc.inputs.expr='a*b'
>>> calc.inputs.out_file =  'functional_calc.nii.gz'
>>> calc.inputs.outputtype = "NIFTI"
>>> calc.cmdline
'3dcalc -a functional.nii  -b functional2.nii -expr "a*b" -prefix functional_calc.nii.gz'

Inputs::

        [Mandatory]
        expr: (a string)
                expr
        in_file_a: (an existing file name)
                input file to 3dcalc

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        in_file_b: (an existing file name)
                operand file to 3dcalc
        out_file: (a file name, nipype default value: %s_calc)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        prefix: (a string)
                output image prefix
        single_idx: (an integer)
                volume index for in_file_a
        start_idx: (an integer)
                start index for in_file_a
                requires: stop_idx
        stop_idx: (an integer)
                stop index for in_file_a
                requires: start_idx
        suffix: (a string)
                output image suffix

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.Copy:


.. index:: Copy

Copy
----

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/afni/preprocess.py#L682>`_

Wraps command **3dcopy**

Copies an image of one type to an image of the same
or different type using 3dcopy command

For complete details, see the `3dcopy Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dcopy.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> copy = afni.Copy()
>>> copy.inputs.in_file = 'functional.nii'
>>> copy.inputs.out_file = 'new_func.nii'
>>> res = copy.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dcopy

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        out_file: (a file name, nipype default value: %s_copy)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        prefix: (a string)
                output image prefix
        suffix: (a string)
                output image suffix

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.Despike:


.. index:: Despike

Despike
-------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/afni/preprocess.py#L438>`_

Wraps command **3dDespike**

Removes 'spikes' from the 3D+time input dataset

For complete details, see the `3dDespike Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dDespike.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> despike = afni.Despike()
>>> despike.inputs.in_file = 'functional.nii'
>>> res = despike.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dDespike

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        out_file: (a file name, nipype default value: %s_despike)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        prefix: (a string)
                output image prefix
        suffix: (a string)
                output image suffix

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.Detrend:


.. index:: Detrend

Detrend
-------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/afni/preprocess.py#L404>`_

Wraps command **3dDetrend**

This program removes components from voxel time series using
linear least squares

For complete details, see the `3dDetrend Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dDetrend.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> detrend = afni.Detrend()
>>> detrend.inputs.in_file = 'functional.nii'
>>> detrend.inputs.args = '-polort 2'
>>> res = detrend.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dDetrend

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        out_file: (a file name, nipype default value: %s_detrend)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        prefix: (a string)
                output image prefix
        suffix: (a string)
                output image suffix

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.Fim:


.. index:: Fim

Fim
---

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/afni/preprocess.py#L950>`_

Wraps command **3dfim+**

Program to calculate the cross-correlation of
an ideal reference waveform with the measured FMRI
time series for each voxel

For complete details, see the `3dfim+ Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dfim+.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> fim = afni.Fim()
>>> fim.inputs.in_file = 'functional.nii'
>>> fim.inputs.ideal_file= 'seed.1D'
>>> fim.inputs.out_file = 'functional_corr.nii'
>>> fim.inputs.out = 'Correlation'
>>> fim.inputs.fim_thr = 0.0009
>>> res = fim.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        ideal_file: (an existing file name)
                ideal time series file name
        in_file: (an existing file name)
                input file to 3dfim+

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        fim_thr: (a float)
                fim internal mask threshold value
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        out: (a string)
                Flag to output the specified parameter
        out_file: (a file name, nipype default value: %s_fim)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        prefix: (a string)
                output image prefix
        suffix: (a string)
                output image suffix

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.Fourier:


.. index:: Fourier

Fourier
-------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/afni/preprocess.py#L723>`_

Wraps command **3dFourier**

Program to lowpass and/or highpass each voxel time series in a
dataset, via the FFT

For complete details, see the `3dFourier Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dfourier.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> fourier = afni.Fourier()
>>> fourier.inputs.in_file = 'functional.nii'
>>> fourier.inputs.args = '-retrend'
>>> fourier.inputs.highpass = 0.005
>>> fourier.inputs.lowpass = 0.1
>>> res = fourier.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        highpass: (a float)
                highpass
        in_file: (an existing file name)
                input file to 3dFourier
        lowpass: (a float)
                lowpass

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        out_file: (a file name, nipype default value: %s_fourier)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        prefix: (a string)
                output image prefix
        suffix: (a string)
                output image suffix

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.Maskave:


.. index:: Maskave

Maskave
-------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/afni/preprocess.py#L837>`_

Wraps command **3dmaskave**

Computes average of all voxels in the input dataset
which satisfy the criterion in the options list

For complete details, see the `3dmaskave Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dmaskave.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> maskave = afni.Maskave()
>>> maskave.inputs.in_file = 'functional.nii'
>>> maskave.inputs.mask= 'seed_mask.nii'
>>> maskave.inputs.quiet= True
>>> maskave.cmdline
'3dmaskave -mask seed_mask.nii -quiet functional.nii > functional_maskave.1D'
>>> res = maskave.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dmaskave

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        mask: (an existing file name)
                matrix to align input file
        out_file: (a file name, nipype default value: %s_maskave.1D)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        prefix: (a string)
                output image prefix
        quiet: (a boolean)
                matrix to align input file
        suffix: (a string)
                output image suffix

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.Merge:


.. index:: Merge

Merge
-----

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/afni/preprocess.py#L648>`_

Wraps command **3dmerge**

Merge or edit volumes using AFNI 3dmerge command

For complete details, see the `3dmerge Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dmerge.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> merge = afni.Merge()
>>> merge.inputs.in_files = ['functional.nii', 'functional2.nii']
>>> merge.inputs.blurfwhm = 4
>>> merge.inputs.doall = True
>>> merge.inputs.out_file = 'e7.nii'
>>> res = merge.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_files: (an existing file name)

        [Optional]
        args: (a string)
                Additional parameters to the command
        blurfwhm: (an integer)
                FWHM blur value (mm)
        doall: (a boolean)
                apply options to all sub-bricks in dataset
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        out_file: (a file name, nipype default value: %s_merge)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        prefix: (a string)
                output image prefix
        suffix: (a string)
                output image suffix

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.ROIStats:


.. index:: ROIStats

ROIStats
--------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/afni/preprocess.py#L1122>`_

Wraps command **3dROIstats**

Display statistics over masked regions

For complete details, see the `3dROIstats Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dROIstats.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> roistats = afni.ROIStats()
>>> roistats.inputs.in_file = 'functional.nii'
>>> roistats.inputs.mask = 'skeleton_mask.nii.gz'
>>> roistats.inputs.quiet=True
>>> res = roistats.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dROIstats

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        mask: (an existing file name)
                input mask
        mask_f2short: (a boolean)
                Tells the program to convert a float mask to short integers, by simple rounding.
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        quiet: (a boolean)
                execute quietly

Outputs::

        stats: (an existing file name)
                output

.. _nipype.interfaces.afni.preprocess.Refit:


.. index:: Refit

Refit
-----

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/afni/preprocess.py#L185>`_

Wraps command **3drefit**

Changes some of the information inside a 3D dataset's header

For complete details, see the `3drefit Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3drefit.html>

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> refit = afni.Refit()
>>> refit.inputs.in_file = 'structural.nii'
>>> refit.inputs.deoblique=True
>>> res = refit.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3drefit

        [Optional]
        args: (a string)
                Additional parameters to the command
        deoblique: (a boolean)
                replace current transformation matrix with cardinal matrix
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        out_file: (a file name, nipype default value: %s_refit)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        prefix: (a string)
                output image prefix
        suffix: (a string)
                output image suffix
        xorigin: (a string)
                x distance for edge voxel offset
        yorigin: (a string)
                y distance for edge voxel offset
        zorigin: (a string)
                z distance for edge voxel offset

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.Resample:


.. index:: Resample

Resample
--------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/afni/preprocess.py#L283>`_

Wraps command **3dresample**

Resample or reorient an image using AFNI 3dresample command

For complete details, see the `3dresample Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dresample.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> resample = afni.Resample()
>>> resample.inputs.in_file = 'functional.nii'
>>> resample.inputs.orientation= 'RPI'
>>> res = resample.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dresample

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        orientation: (a string)
                new orientation code
        out_file: (a file name, nipype default value: %s_resample)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        prefix: (a string)
                output image prefix
        suffix: (a string)
                output image suffix

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.SkullStrip:


.. index:: SkullStrip

SkullStrip
----------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/afni/preprocess.py#L873>`_

Wraps command **3dSkullStrip**

A program to extract the brain from surrounding
tissue from MRI T1-weighted images

For complete details, see the `3dSkullStrip Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dSkullStrip.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> skullstrip = afni.SkullStrip()
>>> skullstrip.inputs.in_file = 'functional.nii'
>>> skullstrip.inputs.args = '-o_ply'
>>> res = skullstrip.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dSkullStrip

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        out_file: (a file name, nipype default value: %s_skullstrip)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        prefix: (a string)
                output image prefix
        suffix: (a string)
                output image suffix

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.TCat:


.. index:: TCat

TCat
----

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/afni/preprocess.py#L907>`_

Wraps command **3dTcat**

Concatenate sub-bricks from input datasets into
one big 3D+time dataset

For complete details, see the `3dTcat Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dTcat.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> tcat = afni.TCat()
>>> tcat.inputs.in_files = ['functional.nii', 'functional2.nii']
>>> tcat.inputs.out_file= 'functional_tcat.nii'
>>> tcat.inputs.rlt = '+'
>>> res = tcat.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_files: (an existing file name)
                input file to 3dTcat

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        out_file: (a file name, nipype default value: %s_tcat)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        prefix: (a string)
                output image prefix
        rlt: (a string)
                options
        suffix: (a string)
                output image suffix

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.TCorrelate:


.. index:: TCorrelate

TCorrelate
----------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/afni/preprocess.py#L998>`_

Wraps command **3dTcorrelate**

Computes the correlation coefficient between corresponding voxel
time series in two input 3D+time datasets 'xset' and 'yset'

For complete details, see the `3dTcorrelate Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dTcorrelate.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> tcorrelate = afni.TCorrelate()
>>> tcorrelate.inputs.xset= 'u_rc1s1_Template.nii'
>>> tcorrelate.inputs.yset = 'u_rc1s2_Template.nii'
>>> tcorrelate.inputs.out_file = 'functional_tcorrelate.nii.gz'
>>> tcorrelate.inputs.polort = -1
>>> tcorrelate.inputs.pearson = True
>>> res = tcarrelate.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        xset: (an existing file name)
                input xset
        yset: (an existing file name)
                input yset

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        out_file: (a file name, nipype default value: %s_tcorr)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        pearson: (a boolean)
                Correlation is the normal Pearson correlation coefficient
        polort: (an integer)
                Remove polynomical trend of order m

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.TShift:


.. index:: TShift

TShift
------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/afni/preprocess.py#L134>`_

Wraps command **3dTshift**

Shifts voxel time series from input
so that seperate slices are aligned to the same
temporal origin

For complete details, see the `3dTshift Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dTshift.html>

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> tshift = afni.TShift()
>>> tshift.inputs.in_file = 'functional.nii'
>>> tshift.inputs.tpattern = 'alt+z'
>>> tshift.inputs.tzero = 0.0
>>> tshift.cmdline
'3dTshift -prefix functional_tshift+orig.BRIK -tpattern alt+z -tzero 0.0 functional.nii'
>>> res = tshift.run()   # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dTShift

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore: (an integer)
                ignore the first set of points specified
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        interp: ('Fourier' or 'linear' or 'cubic' or 'quintic' or 'heptic')
                different interpolation methods (see 3dTShift for details) default = Fourier
        out_file: (a file name, nipype default value: %s_tshift)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        prefix: (a string)
                output image prefix
        rlt: (a boolean)
                Before shifting, remove the mean and linear trend
        rltplus: (a boolean)
                Before shifting, remove the mean and linear trend and later put back the mean
        suffix: (a string)
                output image suffix
        tpattern: ('alt+z' or 'alt+z2' or 'alt-z' or 'alt-z2' or 'seq+z' or 'seq-z')
                use specified slice time pattern rather than one in header
        tr: (a string)
                manually set the TRYou can attach suffix "s" for seconds or "ms" for milliseconds.
        tslice: (an integer)
                align each slice to time offset of given slice
                mutually_exclusive: tzero
        tzero: (a float)
                align each slice to given time offset
                mutually_exclusive: tslice

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.TStat:


.. index:: TStat

TStat
-----

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/afni/preprocess.py#L371>`_

Wraps command **3dTstat**

Compute voxel-wise statistics using AFNI 3dTstat command

For complete details, see the `3dTstat Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dTstat.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> tstat = afni.TStat()
>>> tstat.inputs.in_file = 'functional.nii'
>>> tstat.inputs.args= '-mean'
>>> res = tstat.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dTstat

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        out_file: (a file name, nipype default value: %s_tstat)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        prefix: (a string)
                output image prefix
        suffix: (a string)
                output image suffix

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.To3D:


.. index:: To3D

To3D
----

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/afni/preprocess.py#L65>`_

Wraps command **to3d**

Create a 3D dataset from 2D image files using AFNI to3d command

For complete details, see the `to3d Documentation
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/to3d.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni
>>> To3D = afni.To3D()
>>> To3D.inputs.datatype = 'float'
>>> To3D.inputs.infolder = 'dicomdir'
>>> To3D.inputs.filetype = "anat"
>>> To3D.inputs.outputtype = "NIFTI"
>>> To3D.cmdline
'to3d -datum float -anat -prefix dicomdir.nii dicomdir/*.dcm'
>>> res = To3D.run() #doctest: +SKIP

Inputs::

        [Mandatory]
        in_folder: (an existing directory name)
                folder with DICOM images to convert
                mutually_exclusive: infolder, in_folder
        infolder: (an existing directory name)
                folder with DICOM images to convert
                mutually_exclusive: infolder, in_folder

        [Optional]
        args: (a string)
                Additional parameters to the command
        assumemosaic: (a boolean)
                assume that Siemens image is mosaic
        datatype: ('short' or 'float' or 'byte' or 'complex')
                set output file datatype
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        filetype: ('spgr' or 'fse' or 'epan' or 'anat' or 'ct' or 'spct' or 'pet' or 'mra' or
                 'bmap' or 'diff' or 'omri' or 'abuc' or 'fim' or 'fith' or 'fico' or 'fitt' or 'fift'
                 or 'fizt' or 'fict' or 'fibt' or 'fibn' or 'figt' or 'fipt' or 'fbuc')
                type of datafile being converted
        funcparams: (a string)
                parameters for functional data
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        out_file: (a file name, nipype default value: %s)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        prefix: (a string)
                output image prefix
        skipoutliers: (a boolean)
                skip the outliers check
        suffix: (a string)
                output image suffix

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.Volreg:


.. index:: Volreg

Volreg
------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/afni/preprocess.py#L607>`_

Wraps command **3dvolreg**

Register input volumes to a base volume using AFNI 3dvolreg command

For complete details, see the `3dvolreg Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dvolreg.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> volreg = afni.Volreg()
>>> volreg.inputs.in_file = 'functional.nii'
>>> volreg.inputs.args = '-Fourier -twopass'
>>> volreg.inputs.zpad = 4
>>> volreg.inputs.outputtype = "NIFTI"
>>> volreg.cmdline
'3dvolreg -Fourier -twopass -1Dfile functional.1D -prefix functional_volreg.nii -zpad 4 functional.nii'
>>> res = volreg.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dvolreg

        [Optional]
        args: (a string)
                Additional parameters to the command
        basefile: (an existing file name)
                base file for registration
        copyorigin: (a boolean)
                copy base file origin coords to output
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        md1dfile: (a file name)
                max displacement output file
        oned_file: (a file name, nipype default value: %s.1D)
                1D movement parameters output file
        out_file: (a file name, nipype default value: %s_volreg)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        prefix: (a string)
                output image prefix
        suffix: (a string)
                output image suffix
        timeshift: (a boolean)
                time shift to mean slice time offset
        verbose: (a boolean)
                more detailed description of the process
        zpad: (an integer)
                Zeropad around the edges by 'n' voxels during rotations

Outputs::

        md1d_file: (an existing file name)
                max displacement info file
        oned_file: (an existing file name)
                movement parameters info file
        out_file: (an existing file name)
                registered file

.. _nipype.interfaces.afni.preprocess.Warp:


.. index:: Warp

Warp
----

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/afni/preprocess.py#L246>`_

Wraps command **3dWarp**

Use 3dWarp for spatially transforming a dataset

For complete details, see the `3dWarp Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dWarp.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> warp = afni.Warp()
>>> warp.inputs.in_file = 'structural.nii'
>>> warp.inputs.deoblique = True
>>> res = warp.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dWarp

        [Optional]
        args: (a string)
                Additional parameters to the command
        deoblique: (a boolean)
                transform dataset from oblique to cardinal
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        gridset: (an existing file name)
                copy grid of specified dataset
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        interp: ('linear' or 'cubic' or 'NN' or 'quintic')
                spatial interpolation methods [default = linear]
        matparent: (an existing file name)
                apply transformation from 3dWarpDrive
        mni2tta: (a boolean)
                transform dataset from MNI152 to Talaraich
        out_file: (a file name, nipype default value: %s_warp)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        prefix: (a string)
                output image prefix
        suffix: (a string, nipype default value: _warp)
                out_file suffix
        tta2mni: (a boolean)
                transform dataset from Talairach to MNI152
        zpad: (an integer)
                pad input dataset with N planes of zero on all sides.

Outputs::

        out_file: (an existing file name)
                output file

.. _nipype.interfaces.afni.preprocess.ZCutUp:


.. index:: ZCutUp

ZCutUp
------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/afni/preprocess.py#L760>`_

Wraps command **3dZcutup**

Cut z-slices from a volume using AFNI 3dZcutup command

For complete details, see the `3dZcutup Documentation.
<http://afni.nimh.nih.gov/pub/dist/doc/program_help/3dZcutup.html>`_

Examples
~~~~~~~~

>>> from nipype.interfaces import afni as afni
>>> zcutup = afni.ZCutUp()
>>> zcutup.inputs.in_file = 'functional.nii'
>>> zcutup.inputs.out_file = 'functional_zcutup.nii'
>>> zcutup.inputs.keep= '0 10'
>>> res = zcutup.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input file to 3dZcutup

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        keep: (a string)
                slice range to keep in output
        out_file: (a file name, nipype default value: %s_zcupup)
                output image file name
        outputtype: ('NIFTI_GZ' or 'AFNI' or 'NIFTI')
                AFNI output filetype
        prefix: (a string)
                output image prefix
        suffix: (a string)
                output image suffix

Outputs::

        out_file: (an existing file name)
                output file
