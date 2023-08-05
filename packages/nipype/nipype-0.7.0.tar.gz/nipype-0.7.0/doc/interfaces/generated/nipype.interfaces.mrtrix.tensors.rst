.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.mrtrix.tensors
=========================


.. _nipype.interfaces.mrtrix.tensors.ConstrainedSphericalDeconvolution:


.. index:: ConstrainedSphericalDeconvolution

ConstrainedSphericalDeconvolution
---------------------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/mrtrix/tensors.py#L113>`_

Wraps command **csdeconv**

Perform non-negativity constrained spherical deconvolution.

Note that this program makes use of implied symmetries in the diffusion profile.
First, the fact the signal attenuation profile is real implies that it has conjugate symmetry,
i.e. Y(l,-m) = Y(l,m)* (where * denotes the complex conjugate). Second, the diffusion profile should be
antipodally symmetric (i.e. S(x) = S(-x)), implying that all odd l components should be zero.
Therefore, this program only computes the even elements.    Note that the spherical harmonics equations used here
differ slightly from those conventionally used, in that the (-1)^m factor has been omitted. This should be taken
into account in all subsequent calculations. Each volume in the output image corresponds to a different spherical
harmonic component, according to the following convention:

* [0] Y(0,0)
* [1] Im {Y(2,2)}
* [2] Im {Y(2,1)}
* [3] Y(2,0)
* [4] Re {Y(2,1)}
* [5] Re {Y(2,2)}
* [6] Im {Y(4,4)}
* [7] Im {Y(4,3)}

Example
~~~~~~~

>>> import nipype.interfaces.mrtrix as mrt
>>> csdeconv = mrt.ConstrainedSphericalDeconvolution()
>>> csdeconv.inputs.in_file = 'dwi.mif'
>>> csdeconv.inputs.encoding_file = 'encoding.txt'
>>> csdeconv.run()                                          # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                diffusion-weighted image
        response_file: (an existing file name)
                the diffusion-weighted signal response function for a single fibre population (see
                EstimateResponse)

        [Optional]
        args: (a string)
                Additional parameters to the command
        debug: (a boolean)
                Display debugging messages.
        directions_file: (an existing file name)
                a text file containing the [ el az ] pairs for the directions: Specify the directions
                over which to apply the non-negativity constraint (by default, the built-in 300
                direction set is used)
        encoding_file: (an existing file name)
                Gradient encoding, supplied as a 4xN text file with each line is in the format [ X Y Z b
                ], where [ X Y Z ] describe the direction of the applied gradient, and b gives the
                b-value in units (1000 s/mm^2). See FSL2MRTrix
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        filter_file: (an existing file name)
                a text file containing the filtering coefficients for each even harmonic order.the
                linear frequency filtering parameters used for the initial linear spherical
                deconvolution step (default = [ 1 1 1 0 0 ]).
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        iterations: (an integer)
                the maximum number of iterations to perform for each voxel (default = 50)
        lambda_value: (a float)
                the regularisation parameter lambda that controls the strength of the constraint
                (default = 1.0).
        mask_image: (an existing file name)
                only perform computation within the specified binary brain mask image
        maximum_harmonic_order: (an integer)
                set the maximum harmonic order for the output series. By default, the program will use
                the highest possible lmax given the number of diffusion-weighted images.
        normalise: (a boolean)
                normalise the DW signal to the b=0 image
        out_filename: (a file name)
                Output filename
        threshold_value: (a float)
                the threshold below which the amplitude of the FOD is assumed to be zero, expressed as a
                fraction of the mean value of the initial FOD (default = 0.1)

Outputs::

        spherical_harmonics_image: (an existing file name)
                Spherical harmonics image

.. _nipype.interfaces.mrtrix.tensors.DWI2SphericalHarmonicsImage:


.. index:: DWI2SphericalHarmonicsImage

DWI2SphericalHarmonicsImage
---------------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/mrtrix/tensors.py#L32>`_

Wraps command **dwi2SH**

Convert base diffusion-weighted images to their spherical harmonic representation.

This program outputs the spherical harmonic decomposition for the set measured signal attenuations.
The signal attenuations are calculated by identifying the b-zero images from the diffusion encoding supplied
(i.e. those with zero as the b-value), and dividing the remaining signals by the mean b-zero signal intensity.
The spherical harmonic decomposition is then calculated by least-squares linear fitting.
Note that this program makes use of implied symmetries in the diffusion profile.

First, the fact the signal attenuation profile is real implies that it has conjugate symmetry,
i.e. Y(l,-m) = Y(l,m)* (where * denotes the complex conjugate). Second, the diffusion profile should be
antipodally symmetric (i.e. S(x) = S(-x)), implying that all odd l components should be zero. Therefore,
this program only computes the even elements.

Note that the spherical harmonics equations used here differ slightly from those conventionally used,
in that the (-1)^m factor has been omitted. This should be taken into account in all subsequent calculations.

Each volume in the output image corresponds to a different spherical harmonic component, according to the following convention:

* [0] Y(0,0)
* [1] Im {Y(2,2)}
* [2] Im {Y(2,1)}
* [3] Y(2,0)
* [4] Re {Y(2,1)}
* [5] Re {Y(2,2)}
* [6] Im {Y(4,4)}
* [7] Im {Y(4,3)}

Example
~~~~~~~

>>> import nipype.interfaces.mrtrix as mrt
>>> dwi2SH = mrt.DWI2SphericalHarmonicsImage()
>>> dwi2SH.inputs.in_file = 'diffusion.nii'
>>> dwi2SH.inputs.encoding_file = 'encoding.txt'
>>> dwi2SH.run()                                    # doctest: +SKIP

Inputs::

        [Mandatory]
        encoding_file: (an existing file name)
                Gradient encoding, supplied as a 4xN text file with each line is in the format [ X Y Z b
                ], where [ X Y Z ] describe the direction of the applied gradient, and b gives the
                b-value in units (1000 s/mm^2). See FSL2MRTrix
        in_file: (an existing file name)
                Diffusion-weighted images

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        maximum_harmonic_order: (a float)
                set the maximum harmonic order for the output series. By default, the program will use
                the highest possible lmax given the number of diffusion-weighted images.
        normalise: (a boolean)
                normalise the DW signal to the b=0 image
        out_filename: (a file name)
                Output filename

Outputs::

        spherical_harmonics_image: (an existing file name)
                Spherical harmonics image

.. _nipype.interfaces.mrtrix.tensors.EstimateResponseForSH:


.. index:: EstimateResponseForSH

EstimateResponseForSH
---------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/mrtrix/tensors.py#L177>`_

Wraps command **estimate_response**

Estimates the fibre response function for use in spherical deconvolution.

Example
~~~~~~~

>>> import nipype.interfaces.mrtrix as mrt
>>> estresp = mrt.EstimateResponseForSH()
>>> estresp.inputs.in_file = 'dwi.mif'
>>> estresp.inputs.mask_image = 'dwi_WMProb.mif'
>>> estresp.inputs.encoding_file = 'encoding.txt'
>>> estresp.run()                                   # doctest: +SKIP

Inputs::

        [Mandatory]
        encoding_file: (an existing file name)
                Gradient encoding, supplied as a 4xN text file with each line is in the format [ X Y Z b
                ], where [ X Y Z ] describe the direction of the applied gradient, and b gives the
                b-value in units (1000 s/mm^2). See FSL2MRTrix
        in_file: (an existing file name)
                Diffusion-weighted images
        mask_image: (an existing file name)
                only perform computation within the specified binary brain mask image

        [Optional]
        args: (a string)
                Additional parameters to the command
        debug: (a boolean)
                Display debugging messages.
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        maximum_harmonic_order: (an integer)
                set the maximum harmonic order for the output series. By default, the program will use
                the highest possible lmax given the number of diffusion-weighted images.
        normalise: (a boolean)
                normalise the DW signal to the b=0 image
        out_filename: (a file name)
                Output filename
        quiet: (a boolean)
                Do not display information messages or progress status.

Outputs::

        response: (an existing file name)
                Spherical harmonics image

.. module:: nipype.interfaces.mrtrix.tensors


.. _nipype.interfaces.mrtrix.tensors.concat_files:

:func:`concat_files`
--------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/mrtrix/tensors.py#L209>`_





