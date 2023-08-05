.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.slicer.legacy.segmentation
=====================================


.. _nipype.interfaces.slicer.legacy.segmentation.OtsuThresholdSegmentation:


.. index:: OtsuThresholdSegmentation

OtsuThresholdSegmentation
-------------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/slicer/legacy/segmentation.py#L22>`_

Wraps command **/home/raid3/gorgolewski/software/slicer/Slicer --launch OtsuThresholdSegmentation **

title: Otsu Threshold Segmentation

category: Legacy.Segmentation

description: This filter creates a labeled image from a grayscale image. First, it calculates an optimal threshold that separates the image into foreground and background. This threshold separates those two classes so that their intra-class variance is minimal (see http://en.wikipedia.org/wiki/Otsu%27s_method). Then the filter runs a connected component algorithm to generate unique labels for each connected region of the foreground. Finally, the resulting image is relabeled to provide consecutive numbering.

version: 1.0

documentation-url: http://wiki.slicer.org/slicerWiki/index.php/Documentation/4.1/Modules/OtsuThresholdSegmentation

contributor: Bill Lorensen (GE)

acknowledgements: This work is part of the National Alliance for Medical Image Computing (NAMIC), funded by the National Institutes of Health through the NIH Roadmap for Medical Research, Grant U54 EB005149.

Inputs::

        [Mandatory]

        [Optional]
        args: (a string)
                Additional parameters to the command
        brightObjects: (a boolean)
                Segmenting bright objects on a dark background or dark objects on a bright background.
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        faceConnected: (a boolean)
                This is an advanced parameter. Adjacent voxels are face connected. This affects the
                connected component algorithm. If this parameter is false, more regions are likely to be
                identified.
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        inputVolume: (an existing file name)
                Input volume to be segmented
        minimumObjectSize: (an integer)
                Minimum size of object to retain. This parameter can be used to get rid of small regions
                in noisy images.
        numberOfBins: (an integer)
                This is an advanced parameter. The number of bins in the histogram used to model the
                probability mass function of the two intensity distributions. Small numbers of bins may
                result in a more conservative threshold. The default should suffice for most
                applications. Experimentation is the only way to see the effect of varying this
                parameter.
        outputVolume: (a boolean or a file name)
                Output filtered

Outputs::

        outputVolume: (an existing file name)
                Output filtered
