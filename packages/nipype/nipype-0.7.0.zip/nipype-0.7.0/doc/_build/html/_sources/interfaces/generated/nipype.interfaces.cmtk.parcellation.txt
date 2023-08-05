.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.cmtk.parcellation
============================


.. _nipype.interfaces.cmtk.parcellation.Parcellate:


.. index:: Parcellate

Parcellate
----------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/cmtk/parcellation.py#L374>`_

Subdivides segmented ROI file into smaller subregions

This interface implements the same procedure as in the ConnectomeMapper's
parcellation stage (cmp/stages/parcellation/maskcreation.py) for a single
parcellation scheme (e.g. 'scale500').

Example
~~~~~~~

>>> import nipype.interfaces.cmtk as cmtk
>>> parcellate = cmtk.Parcellate()
>>> parcellate.inputs.freesurfer_dir = '.'
>>> parcellate.inputs.subjects_dir = '.'
>>> parcellate.inputs.subject_id = 'subj1'
>>> parcellate.inputs.parcellation_name = 'scale500'
>>> parcellate.run()                 # doctest: +SKIP

Inputs::

        [Mandatory]
        subject_id: (a string)
                Subject ID

        [Optional]
        freesurfer_dir: (an existing directory name)
                Freesurfer main directory
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        out_roi_file: (a file name)
                Region of Interest file for connectivity mapping
        parcellation_name: ('scale33' or 'scale60' or 'scale125' or 'scale250' or 'scale500',
                 nipype default value: scale500)
        subjects_dir: (an existing directory name)
                Freesurfer subjects directory

Outputs::

        aseg_file: (an existing file name)
                Automated segmentation file converted from Freesurfer "subjects" directory
        cc_unknown_file: (an existing file name)
                Image file with regions labelled as unknown cortical structures
        ribbon_file: (an existing file name)
                Image file detailing the cortical ribbon
        roi_file: (an existing file name)
                Region of Interest file for connectivity mapping
        roi_file_in_structural_space: (an existing file name)
                ROI image resliced to the dimensions of the original structural image
        white_matter_mask_file: (an existing file name)
                White matter mask file

.. module:: nipype.interfaces.cmtk.parcellation


.. _nipype.interfaces.cmtk.parcellation.create_annot_label:

:func:`create_annot_label`
--------------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/cmtk/parcellation.py#L35>`_






.. _nipype.interfaces.cmtk.parcellation.create_roi:

:func:`create_roi`
------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/cmtk/parcellation.py#L105>`_



Creates the ROI_%s.nii.gz files using the given parcellation information
from networks. Iteratively create volume.


.. _nipype.interfaces.cmtk.parcellation.create_wm_mask:

:func:`create_wm_mask`
----------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/cmtk/parcellation.py#L189>`_






.. _nipype.interfaces.cmtk.parcellation.crop_and_move_datasets:

:func:`crop_and_move_datasets`
------------------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/cmtk/parcellation.py#L325>`_





