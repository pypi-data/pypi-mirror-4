.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.slicer.quantification.changequantification
=====================================================


.. _nipype.interfaces.slicer.quantification.changequantification.IntensityDifferenceMetric:


.. index:: IntensityDifferenceMetric

IntensityDifferenceMetric
-------------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/slicer/quantification/changequantification.py#L24>`_

Wraps command **/home/raid3/gorgolewski/software/slicer/Slicer --launch IntensityDifferenceMetric **

title:
  Intensity Difference Change Detection (FAST)


category:
  Quantification.ChangeQuantification


description:
  Quantifies the changes between two spatially aligned images based on the pixel-wise difference of image intensities.


version: 0.1

contributor: Andrey Fedorov

acknowledgements:

Inputs::

        [Mandatory]

        [Optional]
        args: (a string)
                Additional parameters to the command
        baselineSegmentationVolume: (an existing file name)
                Label volume that contains segmentation of the structure of interest in the baseline
                volume.
        baselineVolume: (an existing file name)
                Baseline volume to be compared to
        changingBandSize: (an integer)
                How far (in mm) from the boundary of the segmentation should the intensity changes be
                considered.
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        followupVolume: (an existing file name)
                Followup volume to be compare to the baseline
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        outputVolume: (a boolean or a file name)
                Output volume to keep the results of change quantification.
        reportFileName: (a boolean or a file name)
                Report file name
        sensitivityThreshold: (a float)
                This parameter should be between 0 and 1, and defines how sensitive the metric should be
                to the intensity changes.

Outputs::

        outputVolume: (an existing file name)
                Output volume to keep the results of change quantification.
        reportFileName: (an existing file name)
                Report file name
