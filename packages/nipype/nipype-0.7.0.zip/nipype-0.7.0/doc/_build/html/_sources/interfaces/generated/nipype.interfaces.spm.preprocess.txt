.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.spm.preprocess
=========================


.. _nipype.interfaces.spm.preprocess.ApplyDeformations:


.. index:: ApplyDeformations

ApplyDeformations
-----------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/spm/preprocess.py#L1057>`_

Inputs::

        [Mandatory]
        deformation_field: (an existing file name)
        in_files: (an existing file name)
        reference_volume: (an existing file name)

        [Optional]
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        interp: (0 <= an integer <= 7)
                degree of b-spline used for interpolation
        matlab_cmd: (a string)
                matlab command to use
        mfile: (a boolean, nipype default value: True)
                Run m-code using m-file
        paths: (a directory name)
                Paths to add to matlabpath
        use_mcr: (a boolean)
                Run m-code using SPM MCR

Outputs::

        out_files: (an existing file name)

.. _nipype.interfaces.spm.preprocess.Coregister:


.. index:: Coregister

Coregister
----------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/spm/preprocess.py#L263>`_

Use spm_coreg for estimating cross-modality rigid body alignment

http://www.fil.ion.ucl.ac.uk/spm/doc/manual.pdf#page=39

Examples
~~~~~~~~

>>> import nipype.interfaces.spm as spm
>>> coreg = spm.Coregister()
>>> coreg.inputs.target = 'functional.nii'
>>> coreg.inputs.source = 'structural.nii'
>>> coreg.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        source: (an existing file name)
                file to register to target
        target: (an existing file name)
                reference file to register to

        [Optional]
        apply_to_files: (an existing file name)
                files to apply transformation to
        cost_function: ('mi' or 'nmi' or 'ecc' or 'ncc')
                cost function, one of: 'mi' - Mutual Information,
                                'nmi' - Normalised Mutual Information,
                                'ecc' - Entropy Correlation Coefficient,
                                'ncc' - Normalised Cross Correlation
        fwhm: (a float)
                gaussian smoothing kernel width (mm)
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        jobtype: ('estwrite' or 'estimate' or 'write', nipype default value: estwrite)
                one of: estimate, write, estwrite
        matlab_cmd: (a string)
                matlab command to use
        mfile: (a boolean, nipype default value: True)
                Run m-code using m-file
        out_prefix: (a string, nipype default value: r)
                coregistered output prefix
        paths: (a directory name)
                Paths to add to matlabpath
        separation: (a list of items which are a float)
                sampling separation in mm
        tolerance: (a list of items which are a float)
                acceptable tolerance for each of 12 params
        use_mcr: (a boolean)
                Run m-code using SPM MCR
        write_interp: (an integer >= 0)
                degree of b-spline used for interpolation
        write_mask: (a boolean)
                True/False mask output image
        write_wrap: (a list of from 3 to 3 items which are an integer)
                Check if interpolation should wrap in [x,y,z]

Outputs::

        coregistered_files: (an existing file name)
                Coregistered other files
        coregistered_source: (an existing file name)
                Coregistered source files

.. _nipype.interfaces.spm.preprocess.CreateWarped:


.. index:: CreateWarped

CreateWarped
------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/spm/preprocess.py#L1005>`_

Apply a flow field estimated by DARTEL to create warped images

http://www.fil.ion.ucl.ac.uk/spm/doc/manual.pdf#page=202

Examples
~~~~~~~~
>>> import nipype.interfaces.spm as spm
>>> create_warped = spm.CreateWarped()
>>> create_warped.inputs.image_files = ['rc1s1.nii', 'rc1s2.nii']
>>> create_warped.inputs.flowfield_files = ['u_rc1s1_Template.nii', 'u_rc1s2_Template.nii']
>>> create_warped.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        flowfield_files: (an existing file name)
                DARTEL flow fields u_rc1*
        image_files: (an existing file name)
                A list of files to be warped

        [Optional]
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        interp: (0 <= an integer <= 7)
                degree of b-spline used for interpolation
        iterations: (0 <= an integer <= 9)
                The number of iterations: log2(number of time steps)
        matlab_cmd: (a string)
                matlab command to use
        mfile: (a boolean, nipype default value: True)
                Run m-code using m-file
        paths: (a directory name)
                Paths to add to matlabpath
        use_mcr: (a boolean)
                Run m-code using SPM MCR

Outputs::

        warped_files: (a list of items which are an existing file name)

.. _nipype.interfaces.spm.preprocess.DARTEL:


.. index:: DARTEL

DARTEL
------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/spm/preprocess.py#L831>`_

Use spm DARTEL to create a template and flow fields

http://www.fil.ion.ucl.ac.uk/spm/doc/manual.pdf#page=197

Examples
~~~~~~~~
>>> import nipype.interfaces.spm as spm
>>> dartel = spm.DARTEL()
>>> dartel.inputs.image_files = [['rc1s1.nii','rc1s2.nii'],['rc2s1.nii', 'rc2s2.nii']]
>>> dartel.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        image_files: (a list of items which are a list of items which are an existing file name)
                A list of files to be segmented

        [Optional]
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        iteration_parameters: (a list of from 3 to 12 items which are a tuple of the form: (1 <=
                 an integer <= 10, a tuple of the form: (a float, a float, a float), 1 or 2 or 4 or 8 or
                 16 or 32 or 64 or 128 or 256 or 512, 0 or 0.5 or 1 or 2 or 4 or 8 or 16 or 32))
                List of tuples for each iteration
                                                       - Inner iterations
                                                       - Regularization parameters
                                                       - Time points for deformation model
                                                       - smoothing parameter
        matlab_cmd: (a string)
                matlab command to use
        mfile: (a boolean, nipype default value: True)
                Run m-code using m-file
        optimization_parameters: (a tuple of the form: (a float, 1 <= an integer <= 8, 1 <= an
                 integer <= 8))
                Optimization settings a tuple
                                                           - LM regularization
                                                           - cycles of multigrid solver
                                                           - relaxation iterations
        paths: (a directory name)
                Paths to add to matlabpath
        regularization_form: ('Linear' or 'Membrane' or 'Bending')
                Form of regularization energy term
        template_prefix: (a string, nipype default value: Template)
                Prefix for template
        use_mcr: (a boolean)
                Run m-code using SPM MCR

Outputs::

        dartel_flow_fields: (a list of items which are an existing file name)
                DARTEL flow fields
        final_template_file: (an existing file name)
                final DARTEL template
        template_files: (a list of items which are an existing file name)
                Templates from different stages of iteration

.. _nipype.interfaces.spm.preprocess.DARTELNorm2MNI:


.. index:: DARTELNorm2MNI

DARTELNorm2MNI
--------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/spm/preprocess.py#L922>`_

Use spm DARTEL to normalize data to MNI space

http://www.fil.ion.ucl.ac.uk/spm/doc/manual.pdf#page=200

Examples
~~~~~~~~
>>> import nipype.interfaces.spm as spm
>>> nm = spm.DARTELNorm2MNI()
>>> nm.inputs.template_file = 'Template_6.nii'
>>> nm.inputs.flowfield_files = ['u_rc1s1_Template.nii', 'u_rc1s3_Template.nii']
>>> nm.inputs.apply_to_files = ['c1s1.nii', 'c1s3.nii']
>>> nm.inputs.modulate = True
>>> nm.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        apply_to_files: (an existing file name)
                Files to apply the transform to
        flowfield_files: (an existing file name)
                DARTEL flow fields u_rc1*
        template_file: (an existing file name)
                DARTEL template

        [Optional]
        bounding_box: (a tuple of the form: (a float, a float, a float, a float, a float, a
                 float))
                Voxel sizes for output file
        fwhm: (a list of from 3 to 3 items which are a float or a float)
                3-list of fwhm for each dimension
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        matlab_cmd: (a string)
                matlab command to use
        mfile: (a boolean, nipype default value: True)
                Run m-code using m-file
        modulate: (a boolean)
                Modulate out images - no modulation preserves concentrations
        paths: (a directory name)
                Paths to add to matlabpath
        use_mcr: (a boolean)
                Run m-code using SPM MCR
        voxel_size: (a tuple of the form: (a float, a float, a float))
                Voxel sizes for output file

Outputs::

        normalization_parameter_file: (an existing file name)
                Transform parameters to MNI space
        normalized_files: (an existing file name)
                Normalized files in MNI space

.. _nipype.interfaces.spm.preprocess.NewSegment:


.. index:: NewSegment

NewSegment
----------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/spm/preprocess.py#L626>`_

Use spm_preproc8 (New Segment) to separate structural images into different
tissue classes. Supports multiple modalities.

NOTE: This interface currently supports single channel input only

http://www.fil.ion.ucl.ac.uk/spm/doc/manual.pdf#page=185

Examples
~~~~~~~~
>>> import nipype.interfaces.spm as spm
>>> seg = spm.NewSegment()
>>> seg.inputs.channel_files = 'structural.nii'
>>> seg.inputs.channel_info = (0.0001, 60, (True, True))
>>> seg.run() # doctest: +SKIP

For VBM pre-processing [http://www.fil.ion.ucl.ac.uk/~john/misc/VBMclass10.pdf],
TPM.nii should be replaced by /path/to/spm8/toolbox/Seg/TPM.nii

>>> seg = NewSegment()
>>> seg.inputs.channel_files = 'structural.nii'
>>> tissue1 = (('TPM.nii', 1), 2, (True,True), (False, False))
>>> tissue2 = (('TPM.nii', 2), 2, (True,True), (False, False))
>>> tissue3 = (('TPM.nii', 3), 2, (True,False), (False, False))
>>> tissue4 = (('TPM.nii', 4), 2, (False,False), (False, False))
>>> tissue5 = (('TPM.nii', 5), 2, (False,False), (False, False))
>>> seg.inputs.tissues = [tissue1, tissue2, tissue3, tissue4, tissue5]
>>> seg.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        channel_files: (an existing file name)
                A list of files to be segmented

        [Optional]
        affine_regularization: ('mni' or 'eastern' or 'subj' or 'none')
                mni, eastern, subj, none
        channel_info: (a tuple of the form: (a float, a float, a tuple of the form: (a boolean, a
                 boolean)))
                A tuple with the following fields:
                            - bias reguralisation (0-10)
                            - FWHM of Gaussian smoothness of bias
                            - which maps to save (Corrected, Field) - a tuple of two boolean values
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        matlab_cmd: (a string)
                matlab command to use
        mfile: (a boolean, nipype default value: True)
                Run m-code using m-file
        paths: (a directory name)
                Paths to add to matlabpath
        sampling_distance: (a float)
                Sampling distance on data for parameter estimation
        tissues: (a list of items which are a tuple of the form: (a tuple of the form: (an
                 existing file name, an integer), an integer, a tuple of the form: (a boolean, a
                 boolean), a tuple of the form: (a boolean, a boolean)))
                A list of tuples (one per tissue) with the following fields:
                            - tissue probability map (4D), 1-based index to frame
                            - number of gaussians
                            - which maps to save [Native, DARTEL] - a tuple of two boolean values
                            - which maps to save [Modulated, Unmodualted] - a tuple of two boolean
                values
        use_mcr: (a boolean)
                Run m-code using SPM MCR
        warping_regularization: (a float)
                Aproximate distance between sampling points.
        write_deformation_fields: (a list of from 2 to 2 items which are a boolean)
                Which deformation fields to write:[Inverse, Forward]

Outputs::

        bias_corrected_images: (an existing file name)
                bias corrected images
        bias_field_images: (an existing file name)
                bias field images
        dartel_input_images: (a list of items which are a list of items which are an existing
                 file name)
                dartel imported class images
        forward_deformation_field: (an existing file name)
        inverse_deformation_field: (an existing file name)
        modulated_class_images: (a list of items which are a list of items which are an existing
                 file name)
                modulated+normalized class images
        native_class_images: (a list of items which are a list of items which are an existing
                 file name)
                native space probability maps
        normalized_class_images: (a list of items which are a list of items which are an existing
                 file name)
                normalized class images
        transformation_mat: (an existing file name)
                Normalization transformation

.. _nipype.interfaces.spm.preprocess.Normalize:


.. index:: Normalize

Normalize
---------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/spm/preprocess.py#L379>`_

use spm_normalise for warping an image to a template

http://www.fil.ion.ucl.ac.uk/spm/doc/manual.pdf#page=51

Examples
~~~~~~~~
>>> import nipype.interfaces.spm as spm
>>> norm = spm.Normalize()
>>> norm.inputs.source = 'functional.nii'
>>> norm.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        parameter_file: (a file name)
                normalization parameter file*_sn.mat
                mutually_exclusive: source, template
        source: (an existing file name)
                file to normalize to template
                mutually_exclusive: parameter_file
        template: (an existing file name)
                template file to normalize to
                mutually_exclusive: parameter_file

        [Optional]
        DCT_period_cutoff: (a float)
                Cutoff of for DCT bases (opt)
        affine_regularization_type: ('mni' or 'size' or 'none')
                mni, size, none (opt)
        apply_to_files: (an existing file name)
                files to apply transformation to (opt)
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        jobtype: ('estwrite' or 'est' or 'write', nipype default value: estwrite)
                one of: est, write, estwrite (opt, estwrite)
        matlab_cmd: (a string)
                matlab command to use
        mfile: (a boolean, nipype default value: True)
                Run m-code using m-file
        nonlinear_iterations: (an integer)
                Number of iterations of nonlinear warping (opt)
        nonlinear_regularization: (a float)
                the amount of the regularization for the nonlinear part of the normalization (opt)
        out_prefix: (a string, nipype default value: w)
                normalized output prefix
        paths: (a directory name)
                Paths to add to matlabpath
        source_image_smoothing: (a float)
                source smoothing (opt)
        source_weight: (a file name)
                name of weighting image for source (opt)
        template_image_smoothing: (a float)
                template smoothing (opt)
        template_weight: (a file name)
                name of weighting image for template (opt)
        use_mcr: (a boolean)
                Run m-code using SPM MCR
        write_bounding_box: (a list of from 2 to 2 items which are a list of from 3 to 3 items
                 which are a float)
                3x2-element list of lists (opt)
        write_interp: (an integer >= 0)
                degree of b-spline used for interpolation
        write_preserve: (a boolean)
                True/False warped images are modulated (opt,)
        write_voxel_sizes: (a list of from 3 to 3 items which are a float)
                3-element list (opt)
        write_wrap: (a list of items which are an integer)
                Check if interpolation should wrap in [x,y,z] - list of bools (opt)

Outputs::

        normalization_parameters: (an existing file name)
                MAT files containing the normalization parameters
        normalized_files: (an existing file name)
                Normalized other files
        normalized_source: (an existing file name)
                Normalized source files

.. _nipype.interfaces.spm.preprocess.Realign:


.. index:: Realign

Realign
-------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/spm/preprocess.py#L151>`_

Use spm_realign for estimating within modality rigid body alignment

http://www.fil.ion.ucl.ac.uk/spm/doc/manual.pdf#page=25

Examples
~~~~~~~~

>>> import nipype.interfaces.spm as spm
>>> realign = spm.Realign()
>>> realign.inputs.in_files = 'functional.nii'
>>> realign.inputs.register_to_mean = True
>>> realign.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_files: (a list of items which are an existing file name or an existing file name)
                list of filenames to realign

        [Optional]
        fwhm: (a floating point number >= 0.0)
                gaussian smoothing kernel width
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        interp: (0 <= an integer <= 7)
                degree of b-spline used for interpolation
        jobtype: ('estwrite' or 'estimate' or 'write', nipype default value: estwrite)
                one of: estimate, write, estwrite
        matlab_cmd: (a string)
                matlab command to use
        mfile: (a boolean, nipype default value: True)
                Run m-code using m-file
        out_prefix: (a string, nipype default value: r)
                realigned output prefix
        paths: (a directory name)
                Paths to add to matlabpath
        quality: (0.0 <= a floating point number <= 1.0)
                0.1 = fast, 1.0 = precise
        register_to_mean: (a boolean)
                Indicate whether realignment is done to the mean image
        separation: (a floating point number >= 0.0)
                sampling separation in mm
        use_mcr: (a boolean)
                Run m-code using SPM MCR
        weight_img: (an existing file name)
                filename of weighting image
        wrap: (a list of from 3 to 3 items which are an integer)
                Check if interpolation should wrap in [x,y,z]
        write_interp: (0 <= an integer <= 7)
                degree of b-spline used for interpolation
        write_mask: (a boolean)
                True/False mask output image
        write_which: (a tuple of the form: (an integer, an integer))
                determines which images to reslice
        write_wrap: (a list of from 3 to 3 items which are an integer)
                Check if interpolation should wrap in [x,y,z]

Outputs::

        mean_image: (an existing file name)
                Mean image file from the realignment
        realigned_files: (a list of items which are an existing file name or an existing file
                 name)
                Realigned files
        realignment_parameters: (an existing file name)
                Estimated translation and rotation parameters

.. _nipype.interfaces.spm.preprocess.Segment:


.. index:: Segment

Segment
-------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/spm/preprocess.py#L528>`_

use spm_segment to separate structural images into different
tissue classes.

http://www.fil.ion.ucl.ac.uk/spm/doc/manual.pdf#page=43

Examples
~~~~~~~~
>>> import nipype.interfaces.spm as spm
>>> seg = spm.Segment()
>>> seg.inputs.data = 'structural.nii'
>>> seg.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        data: (an existing file name)
                one scan per subject

        [Optional]
        affine_regularization: ('mni' or 'eastern' or 'subj' or 'none' or '')
                Possible options: "mni", "eastern", "subj", "none" (no reguralisation), "" (no affine
                registration)
        bias_fwhm: (30 or 40 or 50 or 60 or 70 or 80 or 90 or 100 or 110 or 120 or 130 or 'Inf')
                FWHM of Gaussian smoothness of bias
        bias_regularization: (0 or 1e-05 or 0.0001 or 0.001 or 0.01 or 0.1 or 1 or 10)
                no(0) - extremely heavy (10)
        clean_masks: ('no' or 'light' or 'thorough')
                clean using estimated brain mask ('no','light','thorough')
        csf_output_type: (a list of from 3 to 3 items which are a boolean)
                Options to produce CSF images: c3*.img, wc3*.img and mwc3*.img.
                            None: [False,False,False],
                            Native Space: [False,False,True],
                            Unmodulated Normalised: [False,True,False],
                            Modulated Normalised: [True,False,False],
                            Native + Unmodulated Normalised: [False,True,True],
                            Native + Modulated Normalised: [True,False,True],
                            Native + Modulated + Unmodulated: [True,True,True],
                            Modulated + Unmodulated Normalised: [True,True,False]
        gaussians_per_class: (a list of items which are an integer)
                num Gaussians capture intensity distribution
        gm_output_type: (a list of from 3 to 3 items which are a boolean)
                Options to produce grey matter images: c1*.img, wc1*.img and mwc1*.img.
                            None: [False,False,False],
                            Native Space: [False,False,True],
                            Unmodulated Normalised: [False,True,False],
                            Modulated Normalised: [True,False,False],
                            Native + Unmodulated Normalised: [False,True,True],
                            Native + Modulated Normalised: [True,False,True],
                            Native + Modulated + Unmodulated: [True,True,True],
                            Modulated + Unmodulated Normalised: [True,True,False]
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        mask_image: (an existing file name)
                Binary image to restrict parameter estimation
        matlab_cmd: (a string)
                matlab command to use
        mfile: (a boolean, nipype default value: True)
                Run m-code using m-file
        paths: (a directory name)
                Paths to add to matlabpath
        sampling_distance: (a float)
                Sampling distance on data for parameter estimation
        save_bias_corrected: (a boolean)
                True/False produce a bias corrected image
        tissue_prob_maps: (a list of items which are an existing file name)
                list of gray, white & csf prob. (opt,)
        use_mcr: (a boolean)
                Run m-code using SPM MCR
        warp_frequency_cutoff: (a float)
                Cutoff of DCT bases
        warping_regularization: (a float)
                Controls balance between parameters and data
        wm_output_type: (a list of from 3 to 3 items which are a boolean)
                Options to produce white matter images: c2*.img, wc2*.img and mwc2*.img.
                            None: [False,False,False],
                            Native Space: [False,False,True],
                            Unmodulated Normalised: [False,True,False],
                            Modulated Normalised: [True,False,False],
                            Native + Unmodulated Normalised: [False,True,True],
                            Native + Modulated Normalised: [True,False,True],
                            Native + Modulated + Unmodulated: [True,True,True],
                            Modulated + Unmodulated Normalised: [True,True,False]

Outputs::

        inverse_transformation_mat: (an existing file name)
                Inverse normalization info
        modulated_csf_image: (an existing file name)
                modulated, normalized csf probability map
        modulated_gm_image: (an existing file name)
                modulated, normalized grey probability map
        modulated_input_image: (an existing file name)
                modulated version of input image
        modulated_wm_image: (an existing file name)
                modulated, normalized white probability map
        native_csf_image: (an existing file name)
                native space csf probability map
        native_gm_image: (an existing file name)
                native space grey probability map
        native_wm_image: (an existing file name)
                native space white probability map
        normalized_csf_image: (an existing file name)
                normalized csf probability map
        normalized_gm_image: (an existing file name)
                normalized grey probability map
        normalized_wm_image: (an existing file name)
                normalized white probability map
        transformation_mat: (an existing file name)
                Normalization transformation

.. _nipype.interfaces.spm.preprocess.SliceTiming:


.. index:: SliceTiming

SliceTiming
-----------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/spm/preprocess.py#L57>`_

Use spm to perform slice timing correction.

http://www.fil.ion.ucl.ac.uk/spm/doc/manual.pdf#page=19

Examples
~~~~~~~~

>>> from nipype.interfaces.spm import SliceTiming
>>> st = SliceTiming()
>>> st.inputs.in_files = 'functional.nii'
>>> st.inputs.num_slices = 32
>>> st.inputs.time_repetition = 6.0
>>> st.inputs.time_acquisition = 6. - 6./32.
>>> st.inputs.slice_order = range(32,0,-1)
>>> st.inputs.ref_slice = 1
>>> st.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_files: (a list of items which are an existing file name or an existing file name)
                list of filenames to apply slice timing
        num_slices: (an integer)
                number of slices in a volume
        ref_slice: (an integer)
                1-based Number of the reference slice
        slice_order: (a list of items which are an integer)
                1-based order in which slices are acquired
        time_acquisition: (a float)
                time of volume acquisition. usually calculated as TR-(TR/num_slices)
        time_repetition: (a float)
                time between volume acquisitions (start to start time)

        [Optional]
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        matlab_cmd: (a string)
                matlab command to use
        mfile: (a boolean, nipype default value: True)
                Run m-code using m-file
        out_prefix: (a string, nipype default value: a)
                slicetimed output prefix
        paths: (a directory name)
                Paths to add to matlabpath
        use_mcr: (a boolean)
                Run m-code using SPM MCR

Outputs::

        timecorrected_files: (a file name)

.. _nipype.interfaces.spm.preprocess.Smooth:


.. index:: Smooth

Smooth
------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/spm/preprocess.py#L754>`_

Use spm_smooth for 3D Gaussian smoothing of image volumes.

http://www.fil.ion.ucl.ac.uk/spm/doc/manual.pdf#page=57

Examples
~~~~~~~~
>>> import nipype.interfaces.spm as spm
>>> smooth = spm.Smooth()
>>> smooth.inputs.in_files = 'functional.nii'
>>> smooth.inputs.fwhm = [4, 4, 4]
>>> smooth.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_files: (an existing file name)
                list of files to smooth

        [Optional]
        data_type: (an integer)
                Data type of the output images (opt)
        fwhm: (a list of from 3 to 3 items which are a float or a float)
                3-list of fwhm for each dimension (opt)
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        implicit_masking: (a boolean)
                A mask implied by a particular voxel value
        matlab_cmd: (a string)
                matlab command to use
        mfile: (a boolean, nipype default value: True)
                Run m-code using m-file
        out_prefix: (a string, nipype default value: s)
                smoothed output prefix
        paths: (a directory name)
                Paths to add to matlabpath
        use_mcr: (a boolean)
                Run m-code using SPM MCR

Outputs::

        smoothed_files: (an existing file name)
                smoothed files
