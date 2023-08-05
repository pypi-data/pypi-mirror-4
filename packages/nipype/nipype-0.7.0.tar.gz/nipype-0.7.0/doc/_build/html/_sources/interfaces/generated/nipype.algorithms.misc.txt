.. AUTO-GENERATED FILE -- DO NOT EDIT!

algorithms.misc
===============


.. _nipype.algorithms.misc.AddCSVColumn:


.. index:: AddCSVColumn

AddCSVColumn
------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/algorithms/misc.py#L861>`_

Short interface to add an extra column and field to a text file

Example
~~~~~~~

>>> import nipype.algorithms.misc as misc
>>> addcol = misc.AddCSVColumn()
>>> addcol.inputs.in_file = 'degree.csv'
>>> addcol.inputs.extra_column_heading = 'group'
>>> addcol.inputs.extra_field = 'male'
>>> addcol.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                Input comma-separated value (CSV) files

        [Optional]
        extra_column_heading: (a string)
                New heading to add for the added field.
        extra_field: (a string)
                New field to add to each row. This is useful for saving the group or subject ID in the
                file.
        out_file: (a file name, nipype default value: extra_heading.csv)
                Output filename for merged CSV file

Outputs::

        csv_file: (a file name)
                Output CSV file containing columns

.. _nipype.algorithms.misc.CreateNifti:


.. index:: CreateNifti

CreateNifti
-----------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/algorithms/misc.py#L419>`_

Inputs::

        [Mandatory]
        data_file: (an existing file name)
                ANALYZE img file
        header_file: (an existing file name)
                corresponding ANALYZE hdr file

        [Optional]
        affine: (an array)
                affine transformation array
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run

Outputs::

        nifti_file: (an existing file name)

.. _nipype.algorithms.misc.Distance:


.. index:: Distance

Distance
--------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/algorithms/misc.py#L202>`_

Calculates distance between two volumes.

Inputs::

        [Mandatory]
        volume1: (an existing file name)
                Has to have the same dimensions as volume2.
        volume2: (an existing file name)
                Has to have the same dimensions as volume1.

        [Optional]
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        mask_volume: (an existing file name)
                calculate overlap only within this mask.
        method: ('eucl_min' or 'eucl_cog' or 'eucl_mean' or 'eucl_wmean' or 'eucl_max', nipype
                 default value: eucl_min)
                ""eucl_min": Euclidean distance between two closest points    "eucl_cog": mean Euclidian
                distance between the Center of Gravity of volume1 and CoGs of volume2    "eucl_mean":
                mean Euclidian minimum distance of all volume2 voxels to volume1    "eucl_wmean": mean
                Euclidian minimum distance of all volume2 voxels to volume1 weighted by their values
                "eucl_max": maximum over minimum Euclidian distances of all volume2 voxels to volume1
                (also known as the Hausdorff distance)

Outputs::

        distance: (a float)
        histogram: (a file name)
        point1: (an array with shape (3,))
        point2: (an array with shape (3,))

.. _nipype.algorithms.misc.Gunzip:


.. index:: Gunzip

Gunzip
------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/algorithms/misc.py#L531>`_

Inputs::

        [Mandatory]
        in_file: (an existing file name)

        [Optional]
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run

Outputs::

        out_file: (an existing file name)

.. _nipype.algorithms.misc.Matlab2CSV:


.. index:: Matlab2CSV

Matlab2CSV
----------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/algorithms/misc.py#L583>`_

Simple interface to save the components of a MATLAB .mat file as a text file with comma-separated values (CSVs).

CSV files are easily loaded in R, for use in statistical processing.
For further information, see cran.r-project.org/doc/manuals/R-data.pdf

Example
~~~~~~~

>>> import nipype.algorithms.misc as misc
>>> mat2csv = misc.Matlab2CSV()
>>> mat2csv.inputs.in_file = 'cmatrix.mat'
>>> mat2csv.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                Input MATLAB .mat file

        [Optional]
        reshape_matrix: (a boolean, nipype default value: True)
                The output of this interface is meant for R, so matrices will be reshaped to vectors by
                default.

Outputs::

        csv_files: (a file name)

.. _nipype.algorithms.misc.MergeCSVFiles:


.. index:: MergeCSVFiles

MergeCSVFiles
-------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/algorithms/misc.py#L741>`_

This interface is designed to facilitate data loading in the R environment.
It takes input CSV files and merges them into a single CSV file.
If provided, it will also incorporate column heading names into the resulting CSV file.

CSV files are easily loaded in R, for use in statistical processing.
For further information, see cran.r-project.org/doc/manuals/R-data.pdf

Example
~~~~~~~

>>> import nipype.algorithms.misc as misc
>>> mat2csv = misc.MergeCSVFiles()
>>> mat2csv.inputs.in_files = ['degree.mat','clustering.mat']
>>> mat2csv.inputs.column_headings = ['degree','clustering']
>>> mat2csv.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_files: (an existing file name)
                Input comma-separated value (CSV) files

        [Optional]
        column_headings: (a list of items which are a string)
                List of column headings to save in merged CSV file (must be equal to number of input
                files). If left undefined, these will be pulled from the input filenames.
        extra_column_heading: (a string)
                New heading to add for the added field.
        extra_field: (a string)
                New field to add to each row. This is useful for saving the group or subject ID in the
                file.
        out_file: (a file name, nipype default value: merged.csv)
                Output filename for merged CSV file
        row_heading_title: (a string, nipype default value: label)
                Column heading for the row headings added
        row_headings: (a list of items which are a string)
                List of row headings to save in merged CSV file (must be equal to number of rows in the
                input files).

Outputs::

        csv_file: (a file name)
                Output CSV file containing columns

.. _nipype.algorithms.misc.ModifyAffine:


.. index:: ModifyAffine

ModifyAffine
------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/algorithms/misc.py#L153>`_

Left multiplies the affine matrix with a specified values. Saves the volume as a nifti file.

Inputs::

        [Mandatory]
        volumes: (an existing file name)
                volumes which affine matrices will be modified

        [Optional]
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        transformation_matrix: (an array with shape (4, 4), nipype default value: (<bound method
                 Array.copy_default_value of <traits.trait_numeric.Array object at 0x3633e50>>,
                 (array([[ 1.,  0.,  0.,  0.],        [ 0.,  1.,  0.,  0.],        [ 0.,  0.,  1.,  0.],
                 [ 0.,  0.,  0.,  1.]]),), None))
                transformation matrix that will be left multiplied by the affine matrix

Outputs::

        transformed_volumes: (a file name)

.. _nipype.algorithms.misc.Overlap:


.. index:: Overlap

Overlap
-------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/algorithms/misc.py#L352>`_

Calculates various overlap measures between two maps.

Example
~~~~~~~

>>> overlap = Overlap()
>>> overlap.inputs.volume1 = 'cont1.nii'
>>> overlap.inputs.volume1 = 'cont2.nii'
>>> res = overlap.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        volume1: (an existing file name)
                Has to have the same dimensions as volume2.
        volume2: (an existing file name)
                Has to have the same dimensions as volume1.

        [Optional]
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        mask_volume: (an existing file name)
                calculate overlap only within this mask.
        out_file: (a file name, nipype default value: diff.nii)

Outputs::

        dice: (a float)
        diff_file: (an existing file name)
        jaccard: (a float)
        volume_difference: (an integer)

.. _nipype.algorithms.misc.PickAtlas:


.. index:: PickAtlas

PickAtlas
---------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/algorithms/misc.py#L55>`_

Returns ROI masks given an atlas and a list of labels. Supports dilation
and left right masking (assuming the atlas is properly aligned).

Inputs::

        [Mandatory]
        atlas: (an existing file name)
                Location of the atlas that will be used.

        [Optional]
        dilation_size: (an integer, nipype default value: 0)
                Defines how much the mask will be dilated (expanded in 3D).
        hemi: ('both' or 'left' or 'right', nipype default value: both)
                Restrict the mask to only one hemisphere: left or right
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        labels: (an integer or a list of items which are an integer)
                Labels of regions that will be included inthe mask. Must be compatible with the atlas
                used.
        output_file: (a file name)
                Where to store the output mask.

Outputs::

        mask_file: (an existing file name)
                output mask file

.. _nipype.algorithms.misc.SimpleThreshold:


.. index:: SimpleThreshold

SimpleThreshold
---------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/algorithms/misc.py#L115>`_

Inputs::

        [Mandatory]
        threshold: (a float)
                volumes to be thresholdedeverything below this value will be set to zero
        volumes: (an existing file name)
                volumes to be thresholded

        [Optional]
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run

Outputs::

        thresholded_volumes: (an existing file name)
                thresholded volumes

.. _nipype.algorithms.misc.TSNR:


.. index:: TSNR

TSNR
----

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/algorithms/misc.py#L460>`_

Computes the time-course SNR for a time series

Typically you want to run this on a realigned time-series.

Example
~~~~~~~

>>> tsnr = TSNR()
>>> tsnr.inputs.in_file = 'functional.nii'
>>> res = tsnr.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                realigned 4D file or a list of 3D files

        [Optional]
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        regress_poly: (an integer)
                Remove polynomials

Outputs::

        detrended_file: (a file name)
                detrended input file
        mean_file: (an existing file name)
                mean image file
        stddev_file: (an existing file name)
                std dev image file
        tsnr_file: (an existing file name)
                tsnr image file

.. module:: nipype.algorithms.misc


.. _nipype.algorithms.misc.makefmtlist:

:func:`makefmtlist`
-------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/algorithms/misc.py#L710>`_






.. _nipype.algorithms.misc.maketypelist:

:func:`maketypelist`
--------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/algorithms/misc.py#L695>`_






.. _nipype.algorithms.misc.matlab2csv:

:func:`matlab2csv`
------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/algorithms/misc.py#L566>`_






.. _nipype.algorithms.misc.merge_csvs:

:func:`merge_csvs`
------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/algorithms/misc.py#L651>`_






.. _nipype.algorithms.misc.remove_identical_paths:

:func:`remove_identical_paths`
------------------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/algorithms/misc.py#L676>`_






.. _nipype.algorithms.misc.replaceext:

:func:`replaceext`
------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/algorithms/misc.py#L558>`_





