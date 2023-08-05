.. AUTO-GENERATED FILE -- DO NOT EDIT!

algorithms.icc
==============


.. _nipype.algorithms.icc.ICC:


.. index:: ICC

ICC
---

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/algorithms/icc.py#L23>`_

Calculates Interclass Correlation Coefficient (3,1) as defined in
P. E. Shrout & Joseph L. Fleiss (1979). "Intraclass Correlations: Uses in
Assessing Rater Reliability". Psychological Bulletin 86 (2): 420-428. This
particular implementation is aimed at relaibility (test-retest) studies.

Inputs::

        [Mandatory]
        mask: (an existing file name)
        subjects_sessions: (a list of items which are a list of items which are an existing file
                 name)
                n subjects m sessions 3D stat files

        [Optional]
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run

Outputs::

        icc_map: (an existing file name)
        session_var_map: (an existing file name)
                variance between sessions
        subject_var_map: (an existing file name)
                variance between subjects

.. module:: nipype.algorithms.icc


.. _nipype.algorithms.icc.ICC_rep_anova:

:func:`ICC_rep_anova`
---------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/algorithms/icc.py#L76>`_



the data Y are entered as a 'table' ie subjects are in rows and repeated
measures in columns

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                   One Sample Repeated measure ANOVA
                   Y = XB + E with X = [FaTor / Subjects]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

