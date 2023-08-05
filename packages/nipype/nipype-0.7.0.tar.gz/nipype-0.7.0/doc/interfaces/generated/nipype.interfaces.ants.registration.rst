.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.ants.registration
============================


.. _nipype.interfaces.ants.registration.Registration:


.. index:: Registration

Registration
------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/ants/registration.py#L279>`_

Wraps command **antsRegistration**

    Examples
    ~~~~~~~~
    >>> import copy
    >>> from nipype.interfaces.ants import Registration
    >>> reg = Registration()
    >>> reg.inputs.fixed_image = ['fixed1.nii', 'fixed2.nii']
    >>> reg.inputs.moving_image = ['moving1.nii', 'moving2.nii']
    >>> reg.inputs.output_transform_prefix = "output_"
    >>> reg.inputs.initial_moving_transform = 'trans.mat'
    >>> reg.inputs.transforms = ['Affine', 'SyN']
    >>> reg.inputs.transform_parameters = [(2.0,), (0.25, 3.0, 0.0)]
    >>> reg.inputs.number_of_iterations = [[1500, 200], [100, 50, 30]]
    >>> reg.inputs.dimension = 3
    >>> reg.inputs.write_composite_transform = True
    >>> reg.inputs.collapse_output_transforms = False
    >>> reg.inputs.metric = ['Mattes']*2
    >>> reg.inputs.metric_weight = [1]*2 # Default (value ignored currently by ANTs)
    >>> reg.inputs.radius_or_number_of_bins = [32]*2
    >>> reg.inputs.sampling_strategy = ['Random', None]
    >>> reg.inputs.sampling_percentage = [0.05, None]
    >>> reg.inputs.convergence_threshold = [1.e-8, 1.e-9]
    >>> reg.inputs.convergence_window_size = [20]*2
    >>> reg.inputs.smoothing_sigmas = [[1,0], [2,1,0]]
    >>> reg.inputs.shrink_factors = [[2,1], [3,2,1]]
    >>> reg.inputs.use_estimate_learning_rate_once = [True, True]
    >>> reg.inputs.use_histogram_matching = [True, True] # This is the default
    >>> reg.inputs.output_warped_image = 'output_warped_image.nii.gz'

    >>> reg1 = copy.deepcopy(reg)
    >>> reg1.inputs.winsorize_lower_quantile = 0.025
    >>> reg1.inputs.collapse_linear_transforms_to_fixed_image_header = False
    >>> reg1.cmdline
    'antsRegistration --collapse-linear-transforms-to-fixed-image-header 0 --collapse-output-transforms 0 --dimensionality 3 --initial-moving-transform [ trans.mat, 0 ] --interpolation Linear --output [ output_, output_warped_image.nii.gz ] --transform Affine[ 2.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32 ,Random,0.05 ] --convergence [ 1500x200, 1e-08, 20 ] --smoothing-sigmas 1x0 --shrink-factors 2x1 --use-estimate-learning-rate-once 1 --use-histogram-matching 1 --transform SyN[ 0.25, 3.0, 0.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32  ] --convergence [ 100x50x30, 1e-09, 20 ] --smoothing-sigmas 2x1x0 --shrink-factors 3x2x1 --use-estimate-learning-rate-once 1 --use-histogram-matching 1 --winsorize-image-intensities [ 0.025, 1.0 ]  --write-composite-transform 1'
    >>> reg1.run()  #doctest: +SKIP

    >>> reg2 = copy.deepcopy(reg)
    >>> reg2.inputs.winsorize_upper_quantile = 0.975
    >>> reg2.cmdline
    'antsRegistration --collapse-linear-transforms-to-fixed-image-header 0 --collapse-output-transforms 0 --dimensionality 3 --initial-moving-transform [ trans.mat, 0 ] --interpolation Linear --output [ output_, output_warped_image.nii.gz ] --transform Affine[ 2.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32 ,Random,0.05 ] --convergence [ 1500x200, 1e-08, 20 ] --smoothing-sigmas 1x0 --shrink-factors 2x1 --use-estimate-learning-rate-once 1 --use-histogram-matching 1 --transform SyN[ 0.25, 3.0, 0.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32  ] --convergence [ 100x50x30, 1e-09, 20 ] --smoothing-sigmas 2x1x0 --shrink-factors 3x2x1 --use-estimate-learning-rate-once 1 --use-histogram-matching 1 --winsorize-image-intensities [ 0.0, 0.975 ]  --write-composite-transform 1'

    >>> reg3 = copy.deepcopy(reg)
    >>> reg3.inputs.winsorize_lower_quantile = 0.025
    >>> reg3.inputs.winsorize_upper_quantile = 0.975
    >>> reg3.cmdline
    'antsRegistration --collapse-linear-transforms-to-fixed-image-header 0 --collapse-output-transforms 0 --dimensionality 3 --initial-moving-transform [ trans.mat, 0 ] --interpolation Linear --output [ output_, output_warped_image.nii.gz ] --transform Affine[ 2.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32 ,Random,0.05 ] --convergence [ 1500x200, 1e-08, 20 ] --smoothing-sigmas 1x0 --shrink-factors 2x1 --use-estimate-learning-rate-once 1 --use-histogram-matching 1 --transform SyN[ 0.25, 3.0, 0.0 ] --metric Mattes[ fixed1.nii, moving1.nii, 1, 32  ] --convergence [ 100x50x30, 1e-09, 20 ] --smoothing-sigmas 2x1x0 --shrink-factors 3x2x1 --use-estimate-learning-rate-once 1 --use-histogram-matching 1 --winsorize-image-intensities [ 0.025, 0.975 ]  --write-composite-transform 1'

Test collapse transforms flag
    >>> reg4 = copy.deepcopy(reg)
    >>> reg4.inputs.collapse_output_transforms = True
    >>> outputs = reg4._list_outputs()
    >>> print outputs #doctest: +ELLIPSIS
    {'reverse_invert_flags': [True, False], 'inverse_composite_transform': ['.../nipype/testing/data/output_InverseComposite.h5'], 'forward_invert_flags': [False, False], 'reverse_transforms': ['.../nipype/testing/data/output_0GenericAffine.mat', '.../nipype/testing/data/output_1InverseWarp.nii.gz'], 'composite_transform': ['.../nipype/testing/data/output_Composite.h5'], 'forward_transforms': ['.../nipype/testing/data/output_0GenericAffine.mat', '.../nipype/testing/data/output_1Warp.nii.gz']}
    >>> reg4.aggregate_outputs() #doctest: +SKIP

Inputs::

        [Mandatory]
        fixed_image: (an existing file name)
                image to apply transformation to (generally a coregistered functional)
        metric: (a list of items which are 'CC' or 'MeanSquares' or 'Demons' or 'GC' or 'MI' or
                 'Mattes')
        metric_weight: (a list of items which are a float, nipype default value: [])
                Note that the metricWeight is currently not used. Rather, it is a temporary place
                holder until multivariate metrics are available for a single stage.
                requires: metric
        moving_image: (an existing file name)
                image to apply transformation to (generally a coregistered functional)
        transforms: (a list of items which are 'Rigid' or 'Affine' or 'CompositeAffine' or
                 'Similarity' or 'Translation' or 'BSpline' or 'GaussianDisplacementField' or
                 'TimeVaryingVelocityField' or 'TimeVaryingBSplineVelocityField' or 'SyN' or
                 'BSplineSyN' or 'Exponential' or 'BSplineExponential')

        [Optional]
        args: (a string)
                Additional parameters to the command
        collapse_linear_transforms_to_fixed_image_header: (a boolean, nipype default value:
                 False)
        collapse_output_transforms: (a boolean)
                Collapse output transforms. Specifically, enabling this option combines all adjacent
                linear transforms and composes all adjacent displacement field transforms before writing
                the results to disk.
        convergence_threshold: (a list of at least 1 items which are a float, nipype default
                 value: [1e-06])
                requires: number_of_iterations
        convergence_window_size: (a list of at least 1 items which are an integer, nipype default
                 value: [10])
                requires: convergence_threshold
        dimension: (3 or 2, nipype default value: 3)
                image dimension (2 or 3)
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        interpolation: ('Linear' or 'NearestNeighbor' or 'CosineWindowedSinc' or
                 'WelchWindowedSinc' or 'HammingWindowedSinc' or 'LanczosWindowedSinc', nipype default
                 value: Linear)
        num_threads: (an integer, nipype default value: -1)
                Number of ITK threads to use
        number_of_iterations: (a list of items which are a list of items which are an integer)
        output_inverse_warped_image: (a boolean or a file name)
                requires: output_warped_image
        output_transform_prefix: (a string, nipype default value: transform)
        output_warped_image: (a boolean or a file name)
        radius_or_number_of_bins: (a list of items which are an integer, nipype default value:
                 [])
                requires: metric_weight
        sampling_percentage: (a list of at least 1 items which are 0.0 <= a floating point number
                 <= 1.0 or None)
                requires: sampling_strategy
        sampling_strategy: (a list of at least 1 items which are 'Dense' or 'Regular' or 'Random'
                 or None, nipype default value: ['Dense'])
                requires: metric_weight
        shrink_factors: (a list of items which are a list of items which are an integer)
        smoothing_sigmas: (a list of items which are a list of items which are an integer)
        transform_parameters: (a list of items which are a float or a tuple of the form: (a
                 float) or a tuple of the form: (a float, a float, a float))
        use_estimate_learning_rate_once: (a list of items which are a boolean)
        use_histogram_matching: (a list of items which are a boolean, nipype default value: [])
        winsorize_lower_quantile: (0.0 <= a floating point number <= 1.0, nipype default value:
                 0.0)
                The Lower quantile to clip image ranges
        winsorize_upper_quantile: (0.0 <= a floating point number <= 1.0, nipype default value:
                 1.0)
                The Upper quantile to clip image ranges
        write_composite_transform: (a boolean, nipype default value: False)

Outputs::

        composite_transform: (a list of items which are a file name)
                Composite transform file
        forward_invert_flags: (a list of items which are a boolean)
                List of flags corresponding to the forward transforms
        forward_transforms: (a list of items which are a file name)
                List of output transforms for forward registration
        inverse_composite_transform: (a list of items which are a file name)
                Inverse composite transform file
        reverse_invert_flags: (a list of items which are a boolean)
                List of flags corresponding to the reverse transforms
        reverse_transforms: (a list of items which are a file name)
                List of output transforms for reverse registration
