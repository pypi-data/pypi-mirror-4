.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.ants.resampling
==========================


.. _nipype.interfaces.ants.resampling.ApplyTransforms:


.. index:: ApplyTransforms

ApplyTransforms
---------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/ants/resampling.py#L245>`_

Wraps command **antsApplyTransforms**

ApplyTransforms, applied to an input image, transforms it according to a
reference image and a transform (or a set of transforms).

Examples
~~~~~~~~

>>> from nipype.interfaces.ants import ApplyTransforms
>>> at = ApplyTransforms()
>>> at.inputs.dimension = 3
>>> at.inputs.input_image = 'moving1.nii'
>>> at.inputs.reference_image = 'fixed1.nii'
>>> at.inputs.output_image = 'deformed_moving1.nii'
>>> at.inputs.interpolation = 'Linear'
>>> at.inputs.default_value = 0
>>> at.inputs.transforms = ['trans.mat', 'ants_Warp.nii.gz']
>>> at.inputs.invert_transform_flags = [False, False]
>>> at.cmdline
'antsApplyTransforms --default-value 0 --dimensionality 3 --input moving1.nii --interpolation Linear --output deformed_moving1.nii --reference-image fixed1.nii --transform [trans.mat,0] --transform [ants_Warp.nii.gz,0]'

Inputs::

        [Mandatory]
        input_image: (an existing file name)
                image to apply transformation to (generally a coregistered functional)
        reference_image: (an existing file name)
                reference image space that you wish to warp INTO
        transforms: (a list of items which are an existing file name)

        [Optional]
        args: (a string)
                Additional parameters to the command
        default_value: (a float, nipype default value: 0.0)
        dimension: (3 or 2, nipype default value: 3)
                image dimension (2 or 3)
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        interpolation: ('Linear' or 'NearestNeighbor' or 'CosineWindowedSinc' or
                 'WelchWindowedSinc' or 'HammingWindowedSinc' or 'LanczosWindowedSinc' or 'MultiLabel'
                 or 'Gaussian' or 'BSpline', nipype default value: Linear)
        invert_transform_flags: (a list of items which are a boolean)
        num_threads: (an integer, nipype default value: -1)
                Number of ITK threads to use
        output_image: (a string)
                output file name
        print_out_composite_warp_file: (0 or 1)
                requires: output_image

Outputs::

        output_image: (an existing file name)
                Warped image

.. _nipype.interfaces.ants.resampling.WarpImageMultiTransform:


.. index:: WarpImageMultiTransform

WarpImageMultiTransform
-----------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/ants/resampling.py#L145>`_

Wraps command **WarpImageMultiTransform**

Warps an image from one space to another

Examples
~~~~~~~~

>>> from nipype.interfaces.ants import WarpImageMultiTransform
>>> wimt = WarpImageMultiTransform()
>>> wimt.inputs.input_image = 'structural.nii'
>>> wimt.inputs.reference_image = 'ants_deformed.nii.gz'
>>> wimt.inputs.transformation_series = ['ants_Warp.nii.gz','ants_Affine.txt']
>>> wimt.cmdline
'WarpImageMultiTransform 3 structural.nii structural_wimt.nii -R ants_deformed.nii.gz ants_Warp.nii.gz ants_Affine.txt'

>>> wimt = WarpImageMultiTransform()
>>> wimt.inputs.input_image = 'diffusion_weighted.nii'
>>> wimt.inputs.reference_image = 'functional.nii'
>>> wimt.inputs.transformation_series = ['func2anat_coreg_Affine.txt','func2anat_InverseWarp.nii.gz','dwi2anat_Warp.nii.gz','dwi2anat_coreg_Affine.txt']
>>> wimt.inputs.invert_affine = [1]
>>> wimt.cmdline
'WarpImageMultiTransform 3 diffusion_weighted.nii diffusion_weighted_wimt.nii -R functional.nii -i func2anat_coreg_Affine.txt func2anat_InverseWarp.nii.gz dwi2anat_Warp.nii.gz dwi2anat_coreg_Affine.txt'

Inputs::

        [Mandatory]
        input_image: (a file name)
                image to apply transformation to (generally a coregistered functional)
        transformation_series: (an existing file name)
                transformation file(s) to be applied

        [Optional]
        args: (a string)
                Additional parameters to the command
        dimension: (3 or 2, nipype default value: 3)
                image dimension (2 or 3)
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        invert_affine: (a list of items which are an integer)
                List of Affine transformations to invert.E.g.: [1,4,5] inverts the 1st, 4th, and 5th
                Affines found in transformation_series. Note that indexing starts with 1 and does not
                include warp fields. Affine transformations are distinguished from warp fields by the
                word "affine" included in their filenames.
        num_threads: (an integer, nipype default value: -1)
                Number of ITK threads to use
        out_postfix: (a file name, nipype default value: _wimt)
                Postfix that is prepended to all output files (default = _wimt)
                mutually_exclusive: output_image
        output_image: (a file name)
                name of the output warped image
                mutually_exclusive: out_postfix
        reference_image: (a file name)
                reference image space that you wish to warp INTO
                mutually_exclusive: tightest_box
        reslice_by_header: (a boolean)
                Uses orientation matrix and origin encoded in reference image file header. Not typically
                used with additional transforms
        tightest_box: (a boolean)
                computes tightest bounding box (overrided by reference_image if given)
                mutually_exclusive: reference_image
        use_bspline: (a boolean)
                Use 3rd order B-Spline interpolation
        use_nearest: (a boolean)
                Use nearest neighbor interpolation

Outputs::

        output_image: (an existing file name)
                Warped image

.. _nipype.interfaces.ants.resampling.WarpTimeSeriesImageMultiTransform:


.. index:: WarpTimeSeriesImageMultiTransform

WarpTimeSeriesImageMultiTransform
---------------------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/ants/resampling.py#L56>`_

Wraps command **WarpTimeSeriesImageMultiTransform**

Warps a time-series from one space to another

Examples
~~~~~~~~

>>> from nipype.interfaces.ants import WarpTimeSeriesImageMultiTransform
>>> wtsimt = WarpTimeSeriesImageMultiTransform()
>>> wtsimt.inputs.input_image = 'resting.nii'
>>> wtsimt.inputs.reference_image = 'ants_deformed.nii.gz'
>>> wtsimt.inputs.transformation_series = ['ants_Warp.nii.gz','ants_Affine.txt']
>>> wtsimt.cmdline
'WarpTimeSeriesImageMultiTransform 4 resting.nii resting_wtsimt.nii -R ants_deformed.nii.gz ants_Warp.nii.gz ants_Affine.txt'

Inputs::

        [Mandatory]
        input_image: (a file name)
                image to apply transformation to (generally a coregistered functional)
        transformation_series: (an existing file name)
                transformation file(s) to be applied

        [Optional]
        args: (a string)
                Additional parameters to the command
        dimension: (4 or 3, nipype default value: 4)
                image dimension (3 or 4)
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        invert_affine: (a list of items which are an integer)
                List of Affine transformations to invert. E.g.: [1,4,5] inverts the 1st, 4th, and 5th
                Affines found in transformation_series
        num_threads: (an integer, nipype default value: -1)
                Number of ITK threads to use
        out_postfix: (a string, nipype default value: _wtsimt)
                Postfix that is prepended to all output files (default = _wtsimt)
        reference_image: (a file name)
                reference image space that you wish to warp INTO
                mutually_exclusive: tightest_box
        reslice_by_header: (a boolean)
                Uses orientation matrix and origin encoded in reference image file header. Not typically
                used with additional transforms
        tightest_box: (a boolean)
                computes tightest bounding box (overrided by reference_image if given)
                mutually_exclusive: reference_image
        use_bspline: (a boolean)
                Use 3rd order B-Spline interpolation
        use_nearest: (a boolean)
                Use nearest neighbor interpolation

Outputs::

        output_image: (an existing file name)
                Warped image
