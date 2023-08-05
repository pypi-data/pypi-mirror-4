.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.slicer.quantification.petstandarduptakevaluecomputation
==================================================================


.. _nipype.interfaces.slicer.quantification.petstandarduptakevaluecomputation.PETStandardUptakeValueComputation:


.. index:: PETStandardUptakeValueComputation

PETStandardUptakeValueComputation
---------------------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/slicer/quantification/petstandarduptakevaluecomputation.py#L26>`_

Wraps command **/home/raid3/gorgolewski/software/slicer/Slicer --launch PETStandardUptakeValueComputation **

title: PET Standard Uptake Value Computation

category: Quantification

description: Computes the standardized uptake value based on body weight. Takes an input PET image in DICOM and NRRD format (DICOM header must contain Radiopharmaceutical parameters). Produces a CSV file that contains patientID, studyDate, dose, labelID, suvmin, suvmax, suvmean, labelName for each volume of interest. It also displays some of the information as output strings in the GUI, the CSV file is optional in that case. The CSV file is appended to on each execution of the CLI.

version: 0.1.0.$Revision: 8595 $(alpha)

documentation-url: http://www.slicer.org/slicerWiki/index.php/Documentation/4.1/Modules/ComputeSUVBodyWeight

contributor: Wendy Plesniak (SPL, BWH), Nicole Aucoin (SPL, BWH), Ron Kikinis (SPL, BWH)

acknowledgements: This work is funded by the Harvard Catalyst, and the National Alliance for Medical Image Computing (NAMIC), funded by the National Institutes of Health through the NIH Roadmap for Medical Research, Grant U54 EB005149.

Inputs::

        [Mandatory]

        [Optional]
        OutputLabel: (a string)
                List of labels for which SUV values were computed
        OutputLabelValue: (a string)
                List of label values for which SUV values were computed
        SUVMax: (a string)
                SUV max for each label
        SUVMean: (a string)
                SUV mean for each label
        SUVMin: (a string)
                SUV minimum for each label
        args: (a string)
                Additional parameters to the command
        color: (an existing file name)
                Color table to to map labels to colors and names
        csvFile: (a boolean or a file name)
                A file holding the output SUV values in comma separated lines, one per label. Optional.
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        labelMap: (an existing file name)
                Input label volume containing the volumes of interest
        petDICOMPath: (an existing directory name)
                Input path to a directory containing a PET volume containing DICOM header information
                for SUV computation
        petVolume: (an existing file name)
                Input PET volume for SUVbw computation (must be the same volume as pointed to by the
                DICOM path!).

Outputs::

        csvFile: (an existing file name)
                A file holding the output SUV values in comma separated lines, one per label. Optional.
