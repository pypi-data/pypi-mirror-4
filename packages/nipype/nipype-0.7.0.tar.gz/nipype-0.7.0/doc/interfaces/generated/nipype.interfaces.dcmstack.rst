.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.dcmstack
===================


.. _nipype.interfaces.dcmstack.CopyMeta:


.. index:: CopyMeta

CopyMeta
--------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/dcmstack.py#L255>`_

Copy meta data from one Nifti file to another. Useful for preserving
meta data after some processing steps.

Inputs::

        [Mandatory]
        dest_file: (a file name)
        src_file: (a file name)

        [Optional]
        exclude_classes: (a list of items which are any value)
                List of meta data classifications to exclude
        include_classes: (a list of items which are any value)
                List of specific meta data classifications to include. If not specified include
                everything.

Outputs::

        dest_file: (a file name)

.. _nipype.interfaces.dcmstack.DcmStack:


.. index:: DcmStack

DcmStack
--------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/dcmstack.py#L88>`_

Create one Nifti file from a set of DICOM files. Can optionally embed
meta data.

Example
~~~~~~~

>>> from nipype.interfaces.dcmstack import DcmStack
>>> stacker = DcmStack()
>>> stacker.inputs.dicom_files = 'path/to/series/'
>>> stacker.run() # doctest: +SKIP
>>> result.outputs.out_file # doctest: +SKIP
'/path/to/cwd/sequence.nii.gz'

Inputs::

        [Mandatory]
        dicom_files: (a list of items which are an existing file name or an existing directory
                 name or a string)

        [Optional]
        embed_meta: (a boolean)
                Embed DICOM meta data into result
        exclude_regexes: (a list of items which are any value)
                Meta data to exclude, suplementing any default exclude filters
        include_regexes: (a list of items which are any value)
                Meta data to include, overriding any exclude filters
        out_ext: (a string, nipype default value: .nii.gz)
                Determines output file type
        out_format: (a string)
                String which can be formatted with meta data to create the output filename(s)

Outputs::

        out_file: (a file name)

.. _nipype.interfaces.dcmstack.GroupAndStack:


.. index:: GroupAndStack

GroupAndStack
-------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/dcmstack.py#L145>`_

Create (potentially) multiple Nifti files for a set of DICOM files.

Inputs::

        [Mandatory]
        dicom_files: (a list of items which are an existing file name or an existing directory
                 name or a string)

        [Optional]
        embed_meta: (a boolean)
                Embed DICOM meta data into result
        exclude_regexes: (a list of items which are any value)
                Meta data to exclude, suplementing any default exclude filters
        include_regexes: (a list of items which are any value)
                Meta data to include, overriding any exclude filters
        out_ext: (a string, nipype default value: .nii.gz)
                Determines output file type
        out_format: (a string)
                String which can be formatted with meta data to create the output filename(s)

Outputs::

        out_list: (a list of items which are any value)
                List of output nifti files

.. _nipype.interfaces.dcmstack.LookupMeta:


.. index:: LookupMeta

LookupMeta
----------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/dcmstack.py#L184>`_

Lookup meta data values from a Nifti with embeded meta data.

Example
~~~~~~~

>>> from nipype.interfaces import dcmstack
>>> lookup = dcmstack.LookupMeta()
>>> lookup.inputs.in_file = 'functional.nii'
>>> lookup.inputs.meta_keys = {'RepetitionTime' : 'TR',                                    'EchoTime' : 'TE'}
>>> result = lookup.run() # doctest: +SKIP
>>> result.outputs.TR # doctest: +SKIP
9500.0
>>> result.outputs.TE # doctest: +SKIP
95.0

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                The input Nifti file
        meta_keys: (a list of items which are any value or a dictionary with keys which are any
                 value and with values which are any value)
                List of meta data keys to lookup, or a dict where keys specify the meta data keys to
                lookup and the values specify the output names

        [Optional]

Outputs::

        None

.. _nipype.interfaces.dcmstack.MergeNifti:


.. index:: MergeNifti

MergeNifti
----------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/dcmstack.py#L315>`_

Merge multiple Nifti files into one. Merges together meta data
extensions as well.

Inputs::

        [Mandatory]
        in_files: (a list of items which are any value)
                List of Nifti files to merge

        [Optional]
        merge_dim: (an integer)
                Dimension to merge along. If not specified, the last singular or non-existant dimension
                is used.
        out_ext: (a string, nipype default value: .nii.gz)
                Determines output file type
        out_format: (a string)
                String which can be formatted with meta data to create the output filename(s)
        sort_order: (a string or a list of items which are any value)
                One or more meta data keys to sort files by.

Outputs::

        out_file: (a file name)
                Merged Nifti file

.. _nipype.interfaces.dcmstack.NiftiGeneratorBase:


.. index:: NiftiGeneratorBase

NiftiGeneratorBase
------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/dcmstack.py#L50>`_

Base class for interfaces that produce Nifti files, potentially with
embeded meta data.

Inputs::

        [Mandatory]

        [Optional]
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run

Outputs::

        None

.. _nipype.interfaces.dcmstack.SplitNifti:


.. index:: SplitNifti

SplitNifti
----------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/dcmstack.py#L359>`_

Split one Nifti file into many along the specified dimension. Each
result has an updated meta data extension as well.

Inputs::

        [Mandatory]
        in_file: (a file name)
                Nifti file to split

        [Optional]
        out_ext: (a string, nipype default value: .nii.gz)
                Determines output file type
        out_format: (a string)
                String which can be formatted with meta data to create the output filename(s)
        split_dim: (an integer)
                Dimension to split along. If not specified, the last dimension is used.

Outputs::

        out_list: (a list of items which are any value)
                Split Nifti files

.. module:: nipype.interfaces.dcmstack


.. _nipype.interfaces.dcmstack.make_key_func:

:func:`make_key_func`
---------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/dcmstack.py#L308>`_






.. _nipype.interfaces.dcmstack.sanitize_path_comp:

:func:`sanitize_path_comp`
--------------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/dcmstack.py#L34>`_





