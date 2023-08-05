.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.ants.utils
=====================


.. _nipype.interfaces.ants.utils.AverageAffineTransform:


.. index:: AverageAffineTransform

AverageAffineTransform
----------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/ants/utils.py#L31>`_

Wraps command **AverageAffineTransform**

Examples
~~~~~~~~
>>> from nipype.interfaces.ants import AverageAffineTransform
>>> avg = AverageAffineTransform()
>>> avg.inputs.dimension = 3
>>> avg.inputs.transforms = ['trans.mat', 'func_to_struct.mat']
>>> avg.inputs.output_affine_transform = 'MYtemplatewarp.mat'
>>> avg.cmdline
'AverageAffineTransform 3 MYtemplatewarp.mat trans.mat func_to_struct.mat'

Inputs::

        [Mandatory]
        dimension: (3 or 2)
                image dimension (2 or 3)
        output_affine_transform: (a file name)
                Outputfname.txt: the name of the resulting transform.
        transforms: (an existing file name)
                transforms to average

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        num_threads: (an integer, nipype default value: -1)
                Number of ITK threads to use

Outputs::

        affine_transform: (an existing file name)
                average transform file

.. _nipype.interfaces.ants.utils.AverageImages:


.. index:: AverageImages

AverageImages
-------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/ants/utils.py#L70>`_

Wraps command **AverageImages**

Examples
~~~~~~~~
>>> from nipype.interfaces.ants import AverageImages
>>> avg = AverageImages()
>>> avg.inputs.dimension = 3
>>> avg.inputs.output_average_image = "average.nii.gz"
>>> avg.inputs.normalize = True
>>> avg.inputs.images = ['rc1s1.nii', 'rc1s1.nii']
>>> avg.cmdline
'AverageImages 3 average.nii.gz 1 rc1s1.nii rc1s1.nii'

Inputs::

        [Mandatory]
        dimension: (3 or 2)
                image dimension (2 or 3)
        images: (an existing file name)
                image to apply transformation to (generally a coregistered functional)
        normalize: (a boolean)
                Normalize: if true, the 2nd imageis divided by its mean. This will select the largest
                image to average into.

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        num_threads: (an integer, nipype default value: -1)
                Number of ITK threads to use
        output_average_image: (a file name, nipype default value: average.nii)
                the name of the resulting image.

Outputs::

        output_average_image: (an existing file name)
                average image file

.. _nipype.interfaces.ants.utils.JacobianDeterminant:


.. index:: JacobianDeterminant

JacobianDeterminant
-------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/ants/utils.py#L153>`_

Wraps command **ANTSJacobian**

Examples
~~~~~~~~
>>> from nipype.interfaces.ants import JacobianDeterminant
>>> jacobian = JacobianDeterminant()
>>> jacobian.inputs.dimension = 3
>>> jacobian.inputs.warp_file = 'ants_Warp.nii.gz'
>>> jacobian.inputs.output_prefix = 'Sub001_'
>>> jacobian.inputs.use_log = 1
>>> jacobian.cmdline
'ANTSJacobian 3 ants_Warp.nii.gz Sub001_ 1'

Inputs::

        [Mandatory]
        dimension: (3 or 2)
                image dimension (2 or 3)
        warp_file: (an existing file name)
                input warp file

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        num_threads: (an integer, nipype default value: -1)
                Number of ITK threads to use
        output_prefix: (a file name)
                prefix of the output image filename: PREFIX(log)jacobian.nii.gz

Outputs::

        jacobian_image: (an existing file name)
                (log transformed) jacobian image

.. _nipype.interfaces.ants.utils.MultiplyImages:


.. index:: MultiplyImages

MultiplyImages
--------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/ants/utils.py#L109>`_

Wraps command **MultiplyImages**

Examples
~~~~~~~~
>>> from nipype.interfaces.ants import MultiplyImages
>>> test = MultiplyImages()
>>> test.inputs.dimension = 3
>>> test.inputs.first_input = 'moving2.nii'
>>> test.inputs.second_input = 0.25
>>> test.inputs.output_product_image = "out.nii"
>>> test.cmdline
'MultiplyImages 3 moving2.nii 0.25 out.nii'

Inputs::

        [Mandatory]
        dimension: (3 or 2)
                image dimension (2 or 3)
        first_input: (an existing file name)
                image 1
        output_product_image: (a file name)
                Outputfname.nii.gz: the name of the resulting image.
        second_input: (an existing file name or a float)
                image 2 or multiplication weight

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        num_threads: (an integer, nipype default value: -1)
                Number of ITK threads to use

Outputs::

        output_product_image: (an existing file name)
                average image file
