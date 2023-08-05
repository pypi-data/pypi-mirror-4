.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.fsl.model
====================


.. _nipype.interfaces.fsl.model.Cluster:


.. index:: Cluster

Cluster
-------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/fsl/model.py#L1351>`_

Wraps command **cluster**

Uses FSL cluster to perform clustering on statistical output

Examples
~~~~~~~~

>>> cl = Cluster()
>>> cl.inputs.threshold = 2.3
>>> cl.inputs.in_file = 'zstat1.nii.gz'
>>> cl.inputs.out_localmax_txt_file = 'stats.txt'
>>> cl.cmdline
'cluster --in=zstat1.nii.gz --olmax=stats.txt --thresh=2.3000000000'

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input volume
        threshold: (a float)
                threshold for input volume

        [Optional]
        args: (a string)
                Additional parameters to the command
        connectivity: (an integer)
                the connectivity of voxels (default 26)
        cope_file: (a file name)
                cope volume
        dlh: (a float)
                smoothness estimate = sqrt(det(Lambda))
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        find_min: (a boolean)
                find minima instead of maxima
        fractional: (a boolean)
                interprets the threshold as a fraction of the robust range
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        minclustersize: (a boolean)
                prints out minimum significant cluster size
        no_table: (a boolean)
                suppresses printing of the table info
        num_maxima: (an integer)
                no of local maxima to report
        out_index_file: (a boolean or a file name)
                output of cluster index (in size order)
        out_localmax_txt_file: (a boolean or a file name)
                local maxima text file
        out_localmax_vol_file: (a boolean or a file name)
                output of local maxima volume
        out_max_file: (a boolean or a file name)
                filename for output of max image
        out_mean_file: (a boolean or a file name)
                filename for output of mean image
        out_pval_file: (a boolean or a file name)
                filename for image output of log pvals
        out_size_file: (a boolean or a file name)
                filename for output of size image
        out_threshold_file: (a boolean or a file name)
                thresholded image
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or 'NIFTI')
                FSL output type
        peak_distance: (a float)
                minimum distance between local maxima/minima, in mm (default 0)
        pthreshold: (a float)
                p-threshold for clusters
                requires: dlh, volume
        std_space_file: (a file name)
                filename for standard-space volume
        use_mm: (a boolean)
                use mm, not voxel, coordinates
        volume: (an integer)
                number of voxels in the mask
        warpfield_file: (a file name)
                file contining warpfield
        xfm_file: (a file name)
                filename for Linear: input->standard-space transform. Non-linear: input->highres
                transform

Outputs::

        index_file: (a file name)
                output of cluster index (in size order)
        localmax_txt_file: (a file name)
                local maxima text file
        localmax_vol_file: (a file name)
                output of local maxima volume
        max_file: (a file name)
                filename for output of max image
        mean_file: (a file name)
                filename for output of mean image
        pval_file: (a file name)
                filename for image output of log pvals
        size_file: (a file name)
                filename for output of size image
        threshold_file: (a file name)
                thresholded image

.. _nipype.interfaces.fsl.model.ContrastMgr:


.. index:: ContrastMgr

ContrastMgr
-----------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/fsl/model.py#L773>`_

Wraps command **contrast_mgr**

Use FSL contrast_mgr command to evaluate contrasts

In interface mode this file assumes that all the required inputs are in the
same location.

Inputs::

        [Mandatory]
        corrections: (an existing file name)
                statistical corrections used within FILM modelling
        dof_file: (an existing file name)
                degrees of freedom
        param_estimates: (an existing file name)
                Parameter estimates for each column of the design matrix
        sigmasquareds: (an existing file name)
                summary of residuals, See Woolrich, et. al., 2001
        tcon_file: (an existing file name)
                contrast file containing T-contrasts

        [Optional]
        args: (a string)
                Additional parameters to the command
        contrast_num: (an integer)
                contrast number to start labeling copes from
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        fcon_file: (an existing file name)
                contrast file containing F-contrasts
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or 'NIFTI')
                FSL output type
        suffix: (a string)
                suffix to put on the end of the cope filename before the contrast number, default is
                nothing

Outputs::

        copes: (an existing file name)
                Contrast estimates for each contrast
        fstats: (an existing file name)
                f-stat file for each contrast
        neffs: (an existing file name)
                neff file ?? for each contrast
        tstats: (an existing file name)
                t-stat file for each contrast
        varcopes: (an existing file name)
                Variance estimates for each contrast
        zfstats: (an existing file name)
                z-stat file for each F contrast
        zstats: (an existing file name)
                z-stat file for each contrast

.. _nipype.interfaces.fsl.model.FEAT:


.. index:: FEAT

FEAT
----

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/fsl/model.py#L356>`_

Wraps command **feat**

Uses FSL feat to calculate first level stats

Inputs::

        [Mandatory]
        fsf_file: (a file name)
                File specifying the feat design spec file

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or 'NIFTI')
                FSL output type

Outputs::

        feat_dir: (an existing directory name)

.. _nipype.interfaces.fsl.model.FEATModel:


.. index:: FEATModel

FEATModel
---------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/fsl/model.py#L387>`_

Wraps command **feat_model**

Uses FSL feat_model to generate design.mat files

Inputs::

        [Mandatory]
        ev_files: (a list of items which are an existing file name)
                Event spec files generated by level1design
        fsf_file: (a file name)
                File specifying the feat design spec file

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or 'NIFTI')
                FSL output type

Outputs::

        con_file: (an existing file name)
                Contrast file containing contrast vectors
        design_cov: (an existing file name)
                Graphical representation of design covariance
        design_file: (an existing file name)
                Mat file containing ascii matrix for design
        design_image: (an existing file name)
                Graphical representation of design matrix
        fcon_file: (a file name)
                Contrast file containing contrast vectors

.. _nipype.interfaces.fsl.model.FEATRegister:


.. index:: FEATRegister

FEATRegister
------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/fsl/model.py#L566>`_

Register feat directories to a specific standard

Inputs::

        [Mandatory]
        feat_dirs: (a directory name)
                Lower level feat dirs
        reg_image: (a file name)
                image to register to (will be treated as standard)

        [Optional]
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        reg_dof: (an integer, nipype default value: 12)
                registration degrees of freedom

Outputs::

        fsf_file: (an existing file name)
                FSL feat specification file

.. _nipype.interfaces.fsl.model.FILMGLS:


.. index:: FILMGLS

FILMGLS
-------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/fsl/model.py#L484>`_

Wraps command **film_gls**

Use FSL film_gls command to fit a design matrix to voxel timeseries

Examples
~~~~~~~~

Initialize with no options, assigning them when calling run:

>>> from nipype.interfaces import fsl
>>> fgls = fsl.FILMGLS()
>>> res = fgls.run('in_file', 'design_file', 'thresh', rn='stats') #doctest: +SKIP

Assign options through the ``inputs`` attribute:

>>> fgls = fsl.FILMGLS()
>>> fgls.inputs.in_file = 'functional.nii'
>>> fgls.inputs.design_file = 'design.mat'
>>> fgls.inputs.threshold = 10
>>> fgls.inputs.results_dir = 'stats'
>>> res = fgls.run() #doctest: +SKIP

Specify options when creating an instance:

>>> fgls = fsl.FILMGLS(in_file='functional.nii', design_file='design.mat', threshold=10, results_dir='stats')
>>> res = fgls.run() #doctest: +SKIP

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                input data file

        [Optional]
        args: (a string)
                Additional parameters to the command
        autocorr_estimate_only: (a boolean)
                perform autocorrelation estimatation only
                mutually_exclusive: autocorr_estimate_only, fit_armodel, tukey_window,
                 multitaper_product, use_pava, autocorr_noestimate
        autocorr_noestimate: (a boolean)
                do not estimate autocorrs
                mutually_exclusive: autocorr_estimate_only, fit_armodel, tukey_window,
                 multitaper_product, use_pava, autocorr_noestimate
        brightness_threshold: (an integer)
                susan brightness threshold, otherwise it is estimated
        design_file: (an existing file name)
                design matrix file
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        fit_armodel: (a boolean)
                fits autoregressive model - default is to use tukey with M=sqrt(numvols)
                mutually_exclusive: autocorr_estimate_only, fit_armodel, tukey_window,
                 multitaper_product, use_pava, autocorr_noestimate
        full_data: (a boolean)
                output full data
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        mask_size: (an integer)
                susan mask size
        multitaper_product: (an integer)
                multitapering with slepian tapers and num is the time-bandwidth product
                mutually_exclusive: autocorr_estimate_only, fit_armodel, tukey_window,
                 multitaper_product, use_pava, autocorr_noestimate
        output_pwdata: (a boolean)
                output prewhitened data and average design matrix
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or 'NIFTI')
                FSL output type
        results_dir: (a directory name, nipype default value: results)
                directory to store results in
        smooth_autocorr: (a boolean)
                Smooth auto corr estimates
        threshold: (a float)
                threshold
        tukey_window: (an integer)
                tukey window size to estimate autocorr
                mutually_exclusive: autocorr_estimate_only, fit_armodel, tukey_window,
                 multitaper_product, use_pava, autocorr_noestimate
        use_pava: (a boolean)
                estimates autocorr using PAVA

Outputs::

        corrections: (an existing file name)
                statistical corrections used within FILM modelling
        dof_file: (an existing file name)
                degrees of freedom
        logfile: (an existing file name)
                FILM run logfile
        param_estimates: (an existing file name)
                Parameter estimates for each column of the design matrix
        residual4d: (an existing file name)
                Model fit residual mean-squared error for each time point
        results_dir: (an existing directory name)
                directory storing model estimation output
        sigmasquareds: (an existing file name)
                summary of residuals, See Woolrich, et. al., 2001

.. _nipype.interfaces.fsl.model.FLAMEO:


.. index:: FLAMEO

FLAMEO
------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/fsl/model.py#L651>`_

Wraps command **flameo**

Use FSL flameo command to perform higher level model fits

Examples
~~~~~~~~

Initialize FLAMEO with no options, assigning them when calling run:

>>> from nipype.interfaces import fsl
>>> import os
>>> flameo = fsl.FLAMEO(cope_file='cope.nii.gz',                             var_cope_file='varcope.nii.gz',                             cov_split_file='cov_split.mat',                             design_file='design.mat',                             t_con_file='design.con',                             mask_file='mask.nii',                             run_mode='fe')
>>> flameo.cmdline
'flameo --copefile=cope.nii.gz --covsplitfile=cov_split.mat --designfile=design.mat --ld=stats --maskfile=mask.nii --runmode=fe --tcontrastsfile=design.con --varcopefile=varcope.nii.gz'

Inputs::

        [Mandatory]
        cope_file: (an existing file name)
                cope regressor data file
        cov_split_file: (an existing file name)
                ascii matrix specifying the groups the covariance is split into
        design_file: (an existing file name)
                design matrix file
        mask_file: (an existing file name)
                mask file
        run_mode: ('fe' or 'ols' or 'flame1' or 'flame12')
                inference to perform
        t_con_file: (an existing file name)
                ascii matrix specifying t-contrasts

        [Optional]
        args: (a string)
                Additional parameters to the command
        burnin: (an integer)
                number of jumps at start of mcmc to be discarded
        dof_var_cope_file: (an existing file name)
                dof data file for varcope data
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        f_con_file: (an existing file name)
                ascii matrix specifying f-contrasts
        fix_mean: (a boolean)
                fix mean for tfit
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        infer_outliers: (a boolean)
                infer outliers - not for fe
        log_dir: (a directory name, nipype default value: stats)
        n_jumps: (an integer)
                number of jumps made by mcmc
        no_pe_outputs: (a boolean)
                do not output pe files
        outlier_iter: (an integer)
                Number of max iterations to use when inferring outliers. Default is 12.
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or 'NIFTI')
                FSL output type
        sample_every: (an integer)
                number of jumps for each sample
        sigma_dofs: (an integer)
                sigma (in mm) to use for Gaussian smoothing the DOFs in FLAME 2. Default is 1mm, -1
                indicates no smoothing
        var_cope_file: (an existing file name)
                varcope weightings data file

Outputs::

        copes
                Contrast estimates for each contrast
        mrefvars
                mean random effect variances for each contrast
        pes
                Parameter estimates for each column of the design matrixfor each voxel
        res4d
                Model fit residual mean-squared error for each time point
        stats_dir: (an existing directory name)
                directory storing model estimation output
        tdof
                temporal dof file for each contrast
        tstats
                t-stat file for each contrast
        var_copes
                Variance estimates for each contrast
        weights
                weights file for each contrast
        zstats
                z-stat file for each contrast

.. _nipype.interfaces.fsl.model.L2Model:


.. index:: L2Model

L2Model
-------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/fsl/model.py#L878>`_

Generate subject specific second level model

Examples
~~~~~~~~

>>> from nipype.interfaces.fsl import L2Model
>>> model = L2Model(num_copes=3) # 3 sessions

Inputs::

        [Mandatory]
        num_copes: (an integer)
                number of copes to be combined

        [Optional]
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run

Outputs::

        design_con: (an existing file name)
                design contrast file
        design_grp: (an existing file name)
                design group file
        design_mat: (an existing file name)
                design matrix file

.. _nipype.interfaces.fsl.model.Level1Design:


.. index:: Level1Design

Level1Design
------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/fsl/model.py#L83>`_

Generate FEAT specific files

Examples
~~~~~~~~

>>> level1design = Level1Design()
>>> level1design.inputs.interscan_interval = 2.5
>>> level1design.inputs.bases = {'dgamma':{'derivs': False}}
>>> level1design.inputs.session_info = 'session_info.npz'
>>> level1design.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        bases: (a dictionary with keys which are 'dgamma' and with values which are a dictionary
                 with keys which are 'derivs' and with values which are a boolean or a dictionary with
                 keys which are 'gamma' and with values which are a dictionary with keys which are
                 'derivs' and with values which are a boolean or a dictionary with keys which are 'none'
                 and with values which are None)
                name of basis function and options e.g., {'dgamma': {'derivs': True}}
        interscan_interval: (a float)
                Interscan  interval (in secs)
        model_serial_correlations: (a boolean)
                Option to model serial correlations using an autoregressive estimator (order 1). Setting
                this option is only useful in the context of the fsf file. If you set this to False, you
                need to repeat this option for FILMGLS by setting autocorr_noestimate to True
        session_info
                Session specific information generated by ``modelgen.SpecifyModel``

        [Optional]
        contrasts: (a list of items which are a tuple of the form: (a string, 'T', a list of
                 items which are a string, a list of items which are a float) or a tuple of the form: (a
                 string, 'T', a list of items which are a string, a list of items which are a float, a
                 list of items which are a float) or a tuple of the form: (a string, 'F', a list of
                 items which are a tuple of the form: (a string, 'T', a list of items which are a
                 string, a list of items which are a float) or a tuple of the form: (a string, 'T', a
                 list of items which are a string, a list of items which are a float, a list of items
                 which are a float)))
                List of contrasts with each contrast being a list of the form - [('name', 'stat',
                [condition list], [weight list], [session list])]. if session list is None or not
                provided, all sessions are used. For F contrasts, the condition list should contain
                previously defined T-contrasts.
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run

Outputs::

        ev_files: (a list of items which are an existing file name)
                condition information files
        fsf_files: (an existing file name)
                FSL feat specification files

.. _nipype.interfaces.fsl.model.MELODIC:


.. index:: MELODIC

MELODIC
-------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/fsl/model.py#L1191>`_

Wraps command **melodic**

Multivariate Exploratory Linear Optimised Decomposition into Independent Components

Examples
~~~~~~~~

>>> melodic_setup = MELODIC()
>>> melodic_setup.inputs.approach = 'tica'
>>> melodic_setup.inputs.in_files = ['functional.nii', 'functional2.nii', 'functional3.nii']
>>> melodic_setup.inputs.no_bet = True
>>> melodic_setup.inputs.bg_threshold = 10
>>> melodic_setup.inputs.tr_sec = 1.5
>>> melodic_setup.inputs.mm_thresh = 0.5
>>> melodic_setup.inputs.out_stats = True
>>> melodic_setup.inputs.t_des = 'timeDesign.mat'
>>> melodic_setup.inputs.t_con = 'timeDesign.con'
>>> melodic_setup.inputs.s_des = 'subjectDesign.mat'
>>> melodic_setup.inputs.s_con = 'subjectDesign.con'
>>> melodic_setup.inputs.out_dir = 'groupICA.out'
>>> melodic_setup.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        in_files: (an existing file name)
                input file names (either single file name or a list)

        [Optional]
        ICs: (an existing file name)
                filename of the IC components file for mixture modelling
        approach: (a string)
                approach for decomposition, 2D: defl, symm (default),  3D: tica (default), concat
        args: (a string)
                Additional parameters to the command
        bg_image: (an existing file name)
                specify background image for report (default: mean image)
        bg_threshold: (a float)
                brain/non-brain threshold used to mask non-brain voxels, as a percentage (only if
                --nobet selected)
        cov_weight: (a float)
                voxel-wise weights for the covariance matrix (e.g. segmentation information)
        dim: (an integer)
                dimensionality reduction into #num dimensions(default: automatic estimation)
        dim_est: (a string)
                use specific dim. estimation technique: lap, bic, mdl, aic, mean (default: lap)
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        epsilon: (a float)
                minimum error change
        epsilonS: (a float)
                minimum error change for rank-1 approximation in TICA
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        log_power: (a boolean)
                calculate log of power for frequency spectrum
        mask: (an existing file name)
                file name of mask for thresholding
        max_restart: (an integer)
                maximum number of restarts
        maxit: (an integer)
                maximum number of iterations before restart
        mix: (an existing file name)
                mixing matrix for mixture modelling / filtering
        mm_thresh: (a float)
                threshold for Mixture Model based inference
        no_bet: (a boolean)
                switch off BET
        no_mask: (a boolean)
                switch off masking
        no_mm: (a boolean)
                switch off mixture modelling on IC maps
        non_linearity: (a string)
                nonlinearity: gauss, tanh, pow3, pow4
        num_ICs: (an integer)
                number of IC's to extract (for deflation approach)
        out_all: (a boolean)
                output everything
        out_dir: (a directory name)
                output directory name
        out_mean: (a boolean)
                output mean volume
        out_orig: (a boolean)
                output the original ICs
        out_pca: (a boolean)
                output PCA results
        out_stats: (a boolean)
                output thresholded maps and probability maps
        out_unmix: (a boolean)
                output unmixing matrix
        out_white: (a boolean)
                output whitening/dewhitening matrices
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or 'NIFTI')
                FSL output type
        pbsc: (a boolean)
                switch off conversion to percent BOLD signal change
        rem_cmp: (a list of items which are an integer)
                component numbers to remove
        remove_deriv: (a boolean)
                removes every second entry in paradigm file (EV derivatives)
        report: (a boolean)
                generate Melodic web report
        report_maps: (a string)
                control string for spatial map images (see slicer)
        s_con: (an existing file name)
                t-contrast matrix across subject-domain
        s_des: (an existing file name)
                design matrix across subject-domain
        sep_vn: (a boolean)
                switch off joined variance normalization
        sep_whiten: (a boolean)
                switch on separate whitening
        smode: (an existing file name)
                matrix of session modes for report generation
        t_con: (an existing file name)
                t-contrast matrix across time-domain
        t_des: (an existing file name)
                design matrix across time-domain
        tr_sec: (a float)
                TR in seconds
        update_mask: (a boolean)
                switch off mask updating
        var_norm: (a boolean)
                switch off variance normalization

Outputs::

        out_dir: (an existing directory name)
        report_dir: (an existing directory name)

.. _nipype.interfaces.fsl.model.MultipleRegressDesign:


.. index:: MultipleRegressDesign

MultipleRegressDesign
---------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/fsl/model.py#L975>`_

Generate multiple regression design

.. note::
  FSL does not demean columns for higher level analysis.

Please see `FSL documentation <http://www.fmrib.ox.ac.uk/fsl/feat5/detail.html#higher>`_
for more details on model specification for higher level analysis.

Examples
~~~~~~~~

>>> from nipype.interfaces.fsl import MultipleRegressDesign
>>> model = MultipleRegressDesign()
>>> model.inputs.contrasts = [['group mean', 'T',['reg1'],[1]]]
>>> model.inputs.regressors = dict(reg1=[1, 1, 1], reg2=[2.,-4, 3])
>>> model.run() # doctest: +SKIP

Inputs::

        [Mandatory]
        contrasts: (a list of items which are a tuple of the form: (a string, 'T', a list of
                 items which are a string, a list of items which are a float) or a tuple of the form: (a
                 string, 'F', a list of items which are a tuple of the form: (a string, 'T', a list of
                 items which are a string, a list of items which are a float)))
                List of contrasts with each contrast being a list of the form - [('name', 'stat',
                [condition list], [weight list])]. if session list is None or not provided, all sessions
                are used. For F contrasts, the condition list should contain previously defined
                T-contrasts without any weight list.
        regressors: (a dictionary with keys which are a string and with values which are a list
                 of items which are a float)
                dictionary containing named lists of regressors

        [Optional]
        groups: (a list of items which are an integer)
                list of group identifiers (defaults to single group)
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run

Outputs::

        design_con: (an existing file name)
                design t-contrast file
        design_fts: (an existing file name)
                design f-contrast file
        design_grp: (an existing file name)
                design group file
        design_mat: (an existing file name)
                design matrix file

.. _nipype.interfaces.fsl.model.Randomise:


.. index:: Randomise

Randomise
---------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/fsl/model.py#L1465>`_

Wraps command **randomise**

XXX UNSTABLE DO NOT USE

FSL Randomise: feeds the 4D projected FA data into GLM
modelling and thresholding
in order to find voxels which correlate with your model

Example
~~~~~~~
>>> import nipype.interfaces.fsl as fsl
>>> rand = fsl.Randomise(in_file='allFA.nii',     mask = 'mask.nii',     tcon='design.con',     design_mat='design.mat')
>>> rand.cmdline
'randomise -i allFA.nii -o tbss_ -d design.mat -t design.con -m mask.nii'

Inputs::

        [Mandatory]
        in_file: (an existing file name)
                4D input file

        [Optional]
        args: (a string)
                Additional parameters to the command
        base_name: (a string, nipype default value: tbss_)
                the rootname that all generated files will have
        c_thresh: (a float)
                carry out cluster-based thresholding
        cm_thresh: (a float)
                carry out cluster-mass-based thresholding
        demean: (a boolean)
                demean data temporally before model fitting
        design_mat: (an existing file name)
                design matrix file
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        f_c_thresh: (a float)
                carry out f cluster thresholding
        f_cm_thresh: (a float)
                carry out f cluster-mass thresholding
        f_only: (a boolean)
                calculate f-statistics only
        fcon: (an existing file name)
                f contrasts file
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        mask: (an existing file name)
                mask image
        num_perm: (an integer)
                number of permutations (default 5000, set to 0 for exhaustive)
        one_sample_group_mean: (a boolean)
                perform 1-sample group-mean test instead of generic permutation test
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or 'NIFTI')
                FSL output type
        p_vec_n_dist_files: (a boolean)
                output permutation vector and null distribution text files
        raw_stats_imgs: (a boolean)
                output raw ( unpermuted ) statistic images
        seed: (an integer)
                specific integer seed for random number generator
        show_info_parallel_mode: (a boolean)
                print out information required for parallel mode and exit
        show_total_perms: (a boolean)
                print out how many unique permutations would be generated and exit
        tcon: (an existing file name)
                t contrasts file
        tfce: (a boolean)
                carry out Threshold-Free Cluster Enhancement
        tfce2D: (a boolean)
                carry out Threshold-Free Cluster Enhancement with 2D optimisation
        tfce_C: (a float)
                TFCE connectivity (6 or 26; default=6)
        tfce_E: (a float)
                TFCE extent parameter (default=0.5)
        tfce_H: (a float)
                TFCE height parameter (default=2)
        var_smooth: (an integer)
                use variance smoothing (std is in mm)
        vox_p_values: (a boolean)
                output voxelwise (corrected and uncorrected) p-value images
        vxf: (a list of items which are an integer)
                list of 4D images containing voxelwise EVs(list order corresponds to numbers in vxl
                option)
        vxl: (a list of items which are an integer)
                list of numbers indicating voxelwise EVsposition in the design matrix (list order
                corresponds to files in vxf option)
        x_block_labels: (an existing file name)
                exchangeability block labels file

Outputs::

        f_corrected_p_files: (a list of items which are an existing file name)
                f contrast FWE (Family-wise error) corrected p values files
        f_p_files: (a list of items which are an existing file name)
                f contrast uncorrected p values files
        fstat_files: (a list of items which are an existing file name)
                f contrast raw statistic
        t_corrected_p_files: (a list of items which are an existing file name)
                t contrast FWE (Family-wise error) corrected p values files
        t_p_files: (a list of items which are an existing file name)
                f contrast uncorrected p values files
        tstat_files: (a list of items which are an existing file name)
                t contrast raw statistic

.. _nipype.interfaces.fsl.model.SMM:


.. index:: SMM

SMM
---

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/fsl/model.py#L1112>`_

Wraps command **mm --ld=logdir**

Spatial Mixture Modelling. For more detail on the spatial mixture modelling see
Mixture Models with Adaptive Spatial Regularisation for Segmentation with an Application to FMRI Data;
Woolrich, M., Behrens, T., Beckmann, C., and Smith, S.; IEEE Trans. Medical Imaging, 24(1):1-11, 2005.

Inputs::

        [Mandatory]
        mask: (a file name)
                mask file
        spatial_data_file: (an existing file name)
                statistics spatial map

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        no_deactivation_class: (a boolean)
                enforces no deactivation class
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or 'NIFTI')
                FSL output type

Outputs::

        activation_p_map: (an existing file name)
        deactivation_p_map: (an existing file name)
        null_p_map: (an existing file name)

.. _nipype.interfaces.fsl.model.SmoothEstimate:


.. index:: SmoothEstimate

SmoothEstimate
--------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/fsl/model.py#L1253>`_

Wraps command **smoothest**

Estimates the smoothness of an image

Examples
~~~~~~~~

>>> est = SmoothEstimate()
>>> est.inputs.zstat_file = 'zstat1.nii.gz'
>>> est.inputs.mask_file = 'mask.nii'
>>> est.cmdline
'smoothest --mask=mask.nii --zstat=zstat1.nii.gz'

Inputs::

        [Mandatory]
        dof: (an integer)
                number of degrees of freedom
                mutually_exclusive: zstat_file
        mask_file: (an existing file name)
                brain mask volume

        [Optional]
        args: (a string)
                Additional parameters to the command
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        output_type: ('NIFTI_PAIR' or 'NIFTI_PAIR_GZ' or 'NIFTI_GZ' or 'NIFTI')
                FSL output type
        residual_fit_file: (an existing file name)
                residual-fit image file
                requires: dof
        zstat_file: (an existing file name)
                zstat image file
                mutually_exclusive: dof

Outputs::

        dlh: (a float)
                smoothness estimate sqrt(det(Lambda))
        resels: (a float)
                number of resels
        volume: (an integer)
                number of voxels in mask
