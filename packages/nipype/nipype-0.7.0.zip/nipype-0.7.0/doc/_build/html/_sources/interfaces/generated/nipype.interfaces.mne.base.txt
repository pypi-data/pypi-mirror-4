.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.mne.base
===================


.. _nipype.interfaces.mne.base.WatershedBEM:


.. index:: WatershedBEM

WatershedBEM
------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/mne/base.py#L44>`_

Wraps command **mne_watershed_bem**

Uses mne_watershed_bem to get information from dicom directories

Examples
~~~~~~~~

>>> from nipype.interfaces.mne import WatershedBEM
>>> bem = WatershedBEM()
>>> bem.inputs.subject_id = 'subj1'
>>> bem.inputs.subjects_dir = '.'
>>> bem.cmdline
'mne_watershed_bem --overwrite --subject subj1 --volume T1'
>>> bem.run()                               # doctest: +SKIP

Inputs::

        [Mandatory]
        subject_id: (a string)
                Subject ID (must have a complete Freesurfer directory)
        subjects_dir: (an existing directory name, nipype default value: )
                Path to Freesurfer subjects directory

        [Optional]
        args: (a string)
                Additional parameters to the command
        atlas_mode: (a boolean)
                Use atlas mode for registration (default: no rigid alignment)
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        overwrite: (a boolean, nipype default value: True)
                Overwrites the existing files
        volume: ('T1' or 'aparc+aseg' or 'aseg' or 'brain' or 'orig' or 'brainmask' or 'ribbon',
                 nipype default value: T1)
                The volume from the "mri" directory to use (defaults to T1)

Outputs::

        brain_surface: (an existing file name)
                Brain surface (in Freesurfer format)
        cor_files: (an existing file name)
                "COR" format files
        fif_file: (an existing file name)
                "fif" format file for EEG processing in MNE
        inner_skull_surface: (an existing file name)
                Inner skull surface (in Freesurfer format)
        mesh_files: (an existing file name)
                Paths to the output meshes (brain, inner skull, outer skull, outer skin)
        outer_skin_surface: (an existing file name)
                Outer skin surface (in Freesurfer format)
        outer_skull_surface: (an existing file name)
                Outer skull surface (in Freesurfer format)
