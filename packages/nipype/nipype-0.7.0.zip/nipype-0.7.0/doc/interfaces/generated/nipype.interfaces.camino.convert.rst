.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.camino.convert
=========================


.. _nipype.interfaces.camino.convert.AnalyzeHeader:


.. index:: AnalyzeHeader

AnalyzeHeader
-------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/camino/convert.py#L528>`_

Wraps command **analyzeheader**

Create or read an Analyze 7.5 header file.

Analyze image header, provides support for the most common header fields.
Some fields, such as patient_id, are not currently supported. The program allows
three nonstandard options: the field image_dimension.funused1 is the image scale.
The intensity of each pixel in the associated .img file is (image value from file) * scale.
Also, the origin of the Talairach coordinates (midline of the anterior commisure) are encoded
in the field data_history.originator. These changes are included for compatibility with SPM.

All headers written with this program are big endian by default.

Example
~~~~~~~

>>> import nipype.interfaces.camino as cmon
>>> hdr = cmon.AnalyzeHeader()
>>> hdr.inputs.in_file = 'tensor_fitted_data.Bfloat'
>>> hdr.inputs.scheme_file = 'A.scheme'
>>> hdr.inputs.data_dims = [256,256,256]
>>> hdr.inputs.voxel_dims = [1,1,1]
>>> hdr.run()                  # doctest: +SKIP

Inputs::

        [Mandatory]
        datatype: ('byte' or 'char' or '[u]short' or '[u]int' or 'float' or 'complex' or
                 'double')
                The char datatype is 8 bit (not the 16 bit char of Java), as specified by the Analyze
                7.5 standard.      The byte, ushort and uint types are not part of the Analyze
                specification but are supported by SPM.
        in_file: (an existing file name)
                Tensor-fitted data filename

        [Optional]
        args: (a string)
                Additional parameters to the command
        centre: (a list of from 3 to 3 items which are an integer)
                Voxel specifying origin of Talairach coordinate system for SPM, default         [0 0 0].
        data_dims: (a list of from 3 to 3 items which are an integer)
                data dimensions in voxels
        description: (a string)
                Short description - No spaces, max length 79 bytes. Will be null terminated
                automatically.
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        greylevels: (a list of from 2 to 2 items which are an integer)
                Minimum and maximum greylevels. Stored as shorts in the header.
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        intelbyteorder: (a boolean)
                Write header in intel byte order (little-endian).
        networkbyteorder: (a boolean)
                Write header in network byte order (big-endian). This is the default for new headers.
        nimages: (an integer)
                Number of images in the img file. Default 1.
        offset: (an integer)
                According to the Analyze 7.5 standard, this is the byte offset in the .img fileat which
                voxels start. This value can be negative to specify that the absolute value isapplied
                for every image in the file.
        out_file: (a file name)
        picoseed: (a list of from 3 to 3 items which are an integer)
                Voxel specifying the seed (for PICo maps), default [0 0 0].
        scaleinter: (a float)
                Constant to add to the image intensities. Used by SPM and MRIcro.
        scaleslope: (a float)
                Intensities in the image are scaled by this factor by SPM and MRICro. Default is 1.0.
        voxel_dims: (a list of from 3 to 3 items which are a float)
                voxel dimensions in mm

Outputs::

        header: (an existing file name)
                Analyze header

.. _nipype.interfaces.camino.convert.DT2NIfTI:


.. index:: DT2NIfTI

DT2NIfTI
--------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/camino/convert.py#L344>`_

Wraps command **dt2nii**

Converts camino tensor data to NIfTI format

Reads Camino diffusion tensors, and converts them to NIFTI format as three .nii files.

Inputs::

        [Mandatory]
        header_file: (an existing file name)
                 A Nifti .nii or .hdr file containing the header information
        in_file: (an existing file name)
                tract file

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        output_root: (a file name)
                filename root prepended onto the names of three output files.

Outputs::

        dt: (an existing file name)
                diffusion tensors in NIfTI format
        exitcode: (an existing file name)
                exit codes from Camino reconstruction in NIfTI format
        lns0: (an existing file name)
                estimated lns0 from Camino reconstruction in NIfTI format

.. _nipype.interfaces.camino.convert.Image2Voxel:


.. index:: Image2Voxel

Image2Voxel
-----------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/camino/convert.py#L34>`_

Wraps command **image2voxel**

Converts Analyze / NIFTI / MHA files to voxel order.

Converts scanner-order data in a supported image format to voxel-order data.
Either takes a 4D file (all measurements in single image)
or a list of 3D images.

Examples
~~~~~~~~

>>> import nipype.interfaces.camino as cmon
>>> img2vox = cmon.Image2Voxel()
>>> img2vox.inputs.in_file = '4d_dwi.nii'
>>> img2vox.run()                  # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                4d image file

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        out_file: (a file name)
        out_type: ('float' or 'char' or 'short' or 'int' or 'long' or 'double', nipype default
                 value: float)
                "i.e. Bfloat". Can be "char", "short", "int", "long", "float" or "double"

Outputs::

        voxel_order: (an existing file name)
                path/name of 4D volume in voxel order

.. _nipype.interfaces.camino.convert.NIfTIDT2Camino:


.. index:: NIfTIDT2Camino

NIfTIDT2Camino
--------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/camino/convert.py#L409>`_

Wraps command **niftidt2camino**

Converts NIFTI-1 diffusion tensors to Camino format. The program reads the
NIFTI header but does not apply any spatial transformations to the data. The
NIFTI intensity scaling parameters are applied.

The output is the tensors in Camino voxel ordering: [exit, ln(S0), dxx, dxy,
dxz, dyy, dyz, dzz].

The exit code is set to 0 unless a background mask is supplied, in which case
the code is 0 in brain voxels and -1 in background voxels.

The value of ln(S0) in the output is taken from a file if one is supplied,
otherwise it is set to 0.

NOTE FOR FSL USERS - FSL's dtifit can output NIFTI tensors, but they are not
stored in the usual way (which is using NIFTI_INTENT_SYMMATRIX). FSL's
tensors follow the ITK / VTK "upper-triangular" convention, so you will need
to use the -uppertriangular option to convert these correctly.

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                A NIFTI-1 dataset containing diffusion tensors. The tensors are assumed to be in lower-
                triangular order as specified by the NIFTI standard for the storage of symmetric
                matrices. This file should be either a .nii or a .hdr file.

        [Optional]
        args: (a string)
                Additional parameters to the command
        bgmask: (an existing file name)
                Binary valued brain / background segmentation, may be a raw binary file (specify type
                with -maskdatatype) or a supported image file.
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        lns0_file: (an existing file name)
                File containing the log of the unweighted signal for each voxel, may be a raw binary
                file (specify type with -inputdatatype) or a supported image file.
        out_file: (a file name)
        s0_file: (an existing file name)
                File containing the unweighted signal for each voxel, may be a raw binary file (specify
                type with -inputdatatype) or a supported image file.
        scaleinter: (a float)
                A value v in the diffusion tensor is scaled to v * s + i. This is applied after any
                scaling specified by the input image. Default is 0.0.
        scaleslope: (a float)
                A value v in the diffusion tensor is scaled to v * s + i. This is applied after any
                scaling specified by the input image. Default is 1.0.
        uppertriangular: (a boolean)
                Specifies input in upper-triangular (VTK style) order.

Outputs::

        out_file: (a file name)
                diffusion tensors data in Camino format

.. _nipype.interfaces.camino.convert.ProcStreamlines:


.. index:: ProcStreamlines

ProcStreamlines
---------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/camino/convert.py#L248>`_

Wraps command **procstreamlines**

Process streamline data

This program does post-processing of streamline output from track. It can either output streamlines or connection probability maps.
 * http://web4.cs.ucl.ac.uk/research/medic/camino/pmwiki/pmwiki.php?n=Man.procstreamlines

Examples
~~~~~~~~

>>> import nipype.interfaces.camino as cmon
>>> proc = cmon.ProcStreamlines()
>>> proc.inputs.in_file = 'tract_data.Bfloat'
>>> proc.inputs.outputtracts = 'oogl'
>>> proc.run()                  # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                data file

        [Optional]
        allowmultitargets: (a boolean)
                Allows streamlines to connect to multiple target volumes.
        args: (a string)
                Additional parameters to the command
        datadims: (a list of from 3 to 3 items which are an integer)
                data dimensions in voxels
        directional: (a list of from 3 to 3 items which are an integer)
                Splits the streamlines at the seed point and computes separate connection probabilities
                for each segment. Streamline segments are grouped according to their dot product with
                the vector (X, Y, Z). The ideal vector will be tangential to the streamline trajectory
                at the seed, such that the streamline projects from the seed along (X, Y, Z) and -(X, Y,
                Z). However, it is only necessary for the streamline trajectory to not be orthogonal to
                (X, Y, Z).
        discardloops: (a boolean)
                This option allows streamlines to enter a waypoint exactly once. After the streamline
                leaves the waypoint, the entire streamline is discarded upon a second entry to the
                waypoint.
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        gzip: (a boolean)
                save the output image in gzip format
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        inputmodel: ('raw' or 'voxels', nipype default value: raw)
                input model type (raw or voxels)
        iterations: (a float)
                Number of streamlines generated for each seed. Not required when outputting streamlines,
                but needed to create PICo images. The default is 1 if the output is streamlines, and
                5000 if the output is connection probability images.
        maxtractlength: (an integer)
                maximum length of tracts
        maxtractpoints: (an integer)
                maximum number of tract points
        mintractlength: (an integer)
                minimum length of tracts
        mintractpoints: (an integer)
                minimum number of tract points
        noresample: (a boolean)
                Disables resampling of input streamlines. Resampling is automatically disabled if the
                input model is voxels.
        out_file: (a file name)
        outputacm: (a boolean)
                output all tracts in a single connection probability map (Analyze image)
        outputcbs: (a boolean)
                outputs connectivity-based segmentation maps; requires target outputfile
        outputcp: (a boolean)
                output the connection probability map (Analyze image, float)
        outputsc: (a boolean)
                output the connection probability map (raw streamlines, int)
        outputtracts: ('raw' or 'voxels' or 'oogl', nipype default value: raw)
                output tract file type
        regionindex: (an integer)
                index of specific region to process
        resamplestepsize: (a float)
                Each point on a streamline is tested for entry into target, exclusion or waypoint
                volumes. If the length between points on a tract is not much smaller than the voxel
                length, then streamlines may pass through part of a voxel without being counted. To
                avoid this, the program resamples streamlines such that the step size is one tenth of
                the smallest voxel dimension in the image. This increases the size of raw or oogl
                streamline output and incurs some performance penalty. The resample resolution can be
                controlled with this option or disabled altogether by passing a negative step size or by
                passing the -noresample option.
        seedpointmm: (a list of from 3 to 3 items which are an integer)
                The coordinates of a single seed point for tractography in mm
        seedpointvox: (a list of from 3 to 3 items which are an integer)
                The coordinates of a single seed point for tractography in voxels
        truncateinexclusion: (a boolean)
                Retain segments of a streamline before entry to an exclusion ROI.
        truncateloops: (a boolean)
                This option allows streamlines to enter a waypoint exactly once. After the streamline
                leaves the waypoint, it is truncated upon a second entry to the waypoint.
        voxeldims: (a list of from 3 to 3 items which are an integer)
                voxel dimensions in mm

Outputs::

        proc: (an existing file name)
                Processed Streamlines

.. _nipype.interfaces.camino.convert.TractShredder:


.. index:: TractShredder

TractShredder
-------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/camino/convert.py#L292>`_

Wraps command **tractshredder**

Extracts bunches of streamlines.

tractshredder works in a similar way to shredder, but processes streamlines instead of scalar data.
The input is raw streamlines, in the format produced by track or procstreamlines.

The program first makes an initial offset of offset tracts.  It then reads and outputs a group of
bunchsize tracts, skips space tracts, and repeats until there is no more input.

Examples
~~~~~~~~

>>> import nipype.interfaces.camino as cmon
>>> shred = cmon.TractShredder()
>>> shred.inputs.in_file = 'tract_data.Bfloat'
>>> shred.inputs.offset = 0
>>> shred.inputs.bunchsize = 1
>>> shred.inputs.space = 2
>>> shred.run()                  # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                tract file

        [Optional]
        args: (a string)
                Additional parameters to the command
        bunchsize: (an integer)
                reads and outputs a group of bunchsize tracts
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        offset: (an integer)
                initial offset of offset tracts
        out_file: (a file name)
        space: (an integer)
                skips space tracts

Outputs::

        shredded: (an existing file name)
                Shredded tract file

.. _nipype.interfaces.camino.convert.VtkStreamlines:


.. index:: VtkStreamlines

VtkStreamlines
--------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/camino/convert.py#L148>`_

Wraps command **vtkstreamlines**

Use vtkstreamlines to convert raw or voxel format streamlines to VTK polydata

Examples
~~~~~~~~

>>> import nipype.interfaces.camino as cmon
>>> vtk = cmon.VtkStreamlines()
>>> vtk.inputs.in_file = 'tract_data.Bfloat'
>>> vtk.inputs.voxeldims = [1,1,1]
>>> vtk.run()                  # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                data file

        [Optional]
        args: (a string)
                Additional parameters to the command
        colourorient: (a boolean)
                Each point on the streamline is coloured by the local orientation.
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        inputmodel: ('raw' or 'voxels', nipype default value: raw)
                input model type (raw or voxels)
        interpolate: (a boolean)
                the scalar value at each point on the streamline is calculated by trilinear
                interpolation
        interpolatescalars: (a boolean)
                the scalar value at each point on the streamline is calculated by trilinear
                interpolation
        out_file: (a file name)
        voxeldims: (a list of from 3 to 3 items which are an integer)
                voxel dimensions in mm

Outputs::

        vtk: (an existing file name)
                Streamlines in VTK format
