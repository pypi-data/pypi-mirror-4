.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.camino.connectivity
==============================


.. _nipype.interfaces.camino.connectivity.Conmap:


.. index:: Conmap

Conmap
------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/camino/connectivity.py#L37>`_

Wraps command **conmap**

Creates a graph representing the tractographic connections between the regions in the segmented image.

This function creates 'Connectivity.png', shown in figure 1, with the graph representing the ROIs and the
connections between them. The thickness of the connections is proportional to the number of fibers
connecting those two regions. The vertices of the graph indicate the ROI and their diameter is
proportional to the number of tracts reaching that vertex or ROI. Another file, 'ConnectionMatrix.txt',
containing a matrix of the number of tracts connecting different regions, is created at the same location.

If the mapping between few segments in the brain is required, the indices of those regions can be given separately. The labels and the indices of the different segments in wmparc.mgz can be found at brain1/stats/wmparc.stats. Create a file, say indices.txt with comma-separated indices of the required segments.

1001,1002,1003,1004,1005

where 1001,1002.. are the indices of the segments for which graph has to be drawn. The labels of the different vertices can be specified, by creating a file say indices-labels.txt in the following format.

1001:lBSTS
1002:lCAC
1003:lCMF

Example
~~~~~~~

>>> import nipype.interfaces.camino as cmon
>>> mapper = cmon.Conmap()
>>> mapper.inputs.in_file = 'brain_track.Bdouble'
>>> mapper.inputs.roi_file = 'wm_undersampled.nii'
>>> mapper.inputs.index_file = 'indices.txt'
>>> mapper.inputs.index_file = 'indices-labels.txt'
>>> mapper.inputs.threshold = 100
>>> mapper.run()                  # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                tract filename
        roi_file: (an existing file name)
                roi filename

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
        threshold: (an integer)
                threshold indicates the minimum number of fiber connections that has to be drawn in the
                graph.

Outputs::

        conmap_txt: (an existing file name)
                connectivity matrix in text file
