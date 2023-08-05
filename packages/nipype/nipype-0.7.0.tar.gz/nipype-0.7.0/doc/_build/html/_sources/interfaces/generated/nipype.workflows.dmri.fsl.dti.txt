.. AUTO-GENERATED FILE -- DO NOT EDIT!

workflows.dmri.fsl.dti
======================


.. module:: nipype.workflows.dmri.fsl.dti


.. _nipype.workflows.dmri.fsl.dti.create_bedpostx_pipeline:

:func:`create_bedpostx_pipeline`
--------------------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/workflows/dmri/fsl/dti.py#L13>`_



Creates a pipeline that does the same as bedpostx script from FSL -
calculates diffusion model parameters (distributions not MLE) voxelwise for
the whole volume (by splitting it slicewise).

Example
~~~~~~~

>>> nipype_bedpostx = create_bedpostx_pipeline("nipype_bedpostx")
>>> nipype_bedpostx.inputs.inputnode.dwi = 'diffusion.nii'
>>> nipype_bedpostx.inputs.inputnode.mask = 'mask.nii'
>>> nipype_bedpostx.inputs.inputnode.bvecs = 'bvecs'
>>> nipype_bedpostx.inputs.inputnode.bvals = 'bvals'
>>> nipype_bedpostx.inputs.xfibres.n_fibres = 2
>>> nipype_bedpostx.inputs.xfibres.fudge = 1
>>> nipype_bedpostx.inputs.xfibres.burn_in = 1000
>>> nipype_bedpostx.inputs.xfibres.n_jumps = 1250
>>> nipype_bedpostx.inputs.xfibres.sample_every = 25
>>> nipype_bedpostx.run() # doctest: +SKIP

Inputs::

    inputnode.dwi
    inputnode.mask

Outputs::

    outputnode.thsamples
    outputnode.phsamples
    outputnode.fsamples
    outputnode.mean_thsamples
    outputnode.mean_phsamples
    outputnode.mean_fsamples
    outputnode.dyads
    outputnode.dyads_dispersion


Graph
~~~~~

.. graphviz::

	digraph bedpostx{

	  label="bedpostx";

	  bedpostx_inputnode[label="inputnode (utility)"];

	  bedpostx_xfibres[label="xfibres (fsl)"];

	  bedpostx_outputnode[label="outputnode (utility)"];

	  bedpostx_inputnode -> bedpostx_xfibres;

	  bedpostx_inputnode -> bedpostx_xfibres;

	  subgraph cluster_bedpostx_preproc {

	      label="preproc";

	    bedpostx_preproc_inputnode[label="inputnode (utility)"];

	    bedpostx_preproc_mask_dwi[label="mask_dwi (fsl)"];

	    bedpostx_preproc_slice_dwi[label="slice_dwi (fsl)"];

	    bedpostx_preproc_slice_mask[label="slice_mask (fsl)"];

	    bedpostx_preproc_inputnode -> bedpostx_preproc_mask_dwi;

	    bedpostx_preproc_inputnode -> bedpostx_preproc_mask_dwi;

	    bedpostx_preproc_inputnode -> bedpostx_preproc_slice_mask;

	    bedpostx_preproc_mask_dwi -> bedpostx_preproc_slice_dwi;

	  }

	  subgraph cluster_bedpostx_postproc {

	      label="postproc";

	    bedpostx_postproc_inputnode[label="inputnode (utility)"];

	    bedpostx_postproc_merge_mean_dsamples[label="merge_mean_dsamples (fsl)"];

	    bedpostx_postproc_merge_thsamples[label="merge_thsamples (fsl)"];

	    bedpostx_postproc_mean_thsamples[label="mean_thsamples (fsl)"];

	    bedpostx_postproc_merge_fsamples[label="merge_fsamples (fsl)"];

	    bedpostx_postproc_mean_fsamples[label="mean_fsamples (fsl)"];

	    bedpostx_postproc_merge_phsamples[label="merge_phsamples (fsl)"];

	    bedpostx_postproc_mean_phsamples[label="mean_phsamples (fsl)"];

	    bedpostx_postproc_make_dyads[label="make_dyads (fsl)"];

	    bedpostx_postproc_inputnode -> bedpostx_postproc_merge_mean_dsamples;

	    bedpostx_postproc_inputnode -> bedpostx_postproc_merge_thsamples;

	    bedpostx_postproc_inputnode -> bedpostx_postproc_make_dyads;

	    bedpostx_postproc_inputnode -> bedpostx_postproc_merge_fsamples;

	    bedpostx_postproc_inputnode -> bedpostx_postproc_merge_phsamples;

	    bedpostx_postproc_merge_thsamples -> bedpostx_postproc_mean_thsamples;

	    bedpostx_postproc_merge_thsamples -> bedpostx_postproc_make_dyads;

	    bedpostx_postproc_merge_fsamples -> bedpostx_postproc_mean_fsamples;

	    bedpostx_postproc_merge_phsamples -> bedpostx_postproc_mean_phsamples;

	    bedpostx_postproc_merge_phsamples -> bedpostx_postproc_make_dyads;

	  }

	  bedpostx_xfibres -> bedpostx_postproc_inputnode;

	  bedpostx_xfibres -> bedpostx_postproc_inputnode;

	  bedpostx_xfibres -> bedpostx_postproc_inputnode;

	  bedpostx_xfibres -> bedpostx_postproc_inputnode;

	  bedpostx_xfibres -> bedpostx_postproc_inputnode;

	  bedpostx_inputnode -> bedpostx_preproc_inputnode;

	  bedpostx_inputnode -> bedpostx_preproc_inputnode;

	  bedpostx_inputnode -> bedpostx_postproc_inputnode;

	  bedpostx_postproc_merge_thsamples -> bedpostx_outputnode;

	  bedpostx_postproc_merge_phsamples -> bedpostx_outputnode;

	  bedpostx_postproc_merge_fsamples -> bedpostx_outputnode;

	  bedpostx_postproc_mean_thsamples -> bedpostx_outputnode;

	  bedpostx_postproc_mean_phsamples -> bedpostx_outputnode;

	  bedpostx_postproc_mean_fsamples -> bedpostx_outputnode;

	  bedpostx_postproc_make_dyads -> bedpostx_outputnode;

	  bedpostx_postproc_make_dyads -> bedpostx_outputnode;

	  bedpostx_preproc_slice_dwi -> bedpostx_xfibres;

	  bedpostx_preproc_slice_mask -> bedpostx_xfibres;

	}


.. _nipype.workflows.dmri.fsl.dti.create_eddy_correct_pipeline:

:func:`create_eddy_correct_pipeline`
------------------------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/workflows/dmri/fsl/dti.py#L169>`_



Creates a pipeline that replaces eddy_correct script in FSL. It takes a
series of diffusion weighted images and linearly corregisters them to one
reference image.

Example
~~~~~~~

>>> nipype_eddycorrect = create_eddy_correct_pipeline("nipype_eddycorrect")
>>> nipype_eddycorrect.inputs.inputnode.in_file = 'diffusion.nii'
>>> nipype_eddycorrect.inputs.inputnode.ref_num = 0
>>> nipype_eddycorrect.run() # doctest: +SKIP

Inputs::

    inputnode.in_file
    inputnode.ref_num

Outputs::

    outputnode.eddy_corrected


Graph
~~~~~

.. graphviz::

	digraph eddy_correct{

	  label="eddy_correct";

	  eddy_correct_inputnode[label="inputnode (utility)"];

	  eddy_correct_split[label="split (fsl)"];

	  eddy_correct_pick_ref[label="pick_ref (utility)"];

	  eddy_correct_coregistration[label="coregistration (fsl)"];

	  eddy_correct_merge[label="merge (fsl)"];

	  eddy_correct_outputnode[label="outputnode (utility)"];

	  eddy_correct_inputnode -> eddy_correct_split;

	  eddy_correct_inputnode -> eddy_correct_pick_ref;

	  eddy_correct_split -> eddy_correct_pick_ref;

	  eddy_correct_split -> eddy_correct_coregistration;

	  eddy_correct_pick_ref -> eddy_correct_coregistration;

	  eddy_correct_coregistration -> eddy_correct_merge;

	  eddy_correct_merge -> eddy_correct_outputnode;

	}


.. _nipype.workflows.dmri.fsl.dti.transpose:

:func:`transpose`
-----------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/workflows/dmri/fsl/dti.py#L6>`_





