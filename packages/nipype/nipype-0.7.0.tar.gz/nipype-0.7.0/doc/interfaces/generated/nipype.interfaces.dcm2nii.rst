.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.dcm2nii
==================


.. _nipype.interfaces.dcm2nii.Dcm2nii:


.. index:: Dcm2nii

Dcm2nii
-------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/dcm2nii.py#L30>`_

Wraps command **dcm2nii**


Inputs::

        [Mandatory]
        source_names: (an existing file name)

        [Optional]
        anonymize: (a boolean)
        args: (a string)
                Additional parameters to the command
        config_file: (an existing file name)
        convert_all_pars: (a boolean)
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        gzip_output: (a boolean, nipype default value: False)
        id_in_filename: (a boolean, nipype default value: False)
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        nii_output: (a boolean, nipype default value: True)
        output_dir: (an existing directory name)
        reorient: (a boolean)
        reorient_and_crop: (a boolean)

Outputs::

        bvals: (an existing file name)
        bvecs: (an existing file name)
        converted_files: (an existing file name)
        reoriented_and_cropped_files: (an existing file name)
        reoriented_files: (an existing file name)
