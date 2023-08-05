.. AUTO-GENERATED FILE -- DO NOT EDIT!

workflows.smri.ants.ANTSBuildTemplate
=====================================


.. module:: nipype.workflows.smri.ants.ANTSBuildTemplate


.. _nipype.workflows.smri.ants.ANTSBuildTemplate.ANTSTemplateBuildSingleIterationWF:

:func:`ANTSTemplateBuildSingleIterationWF`
------------------------------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/workflows/smri/ants/ANTSBuildTemplate.py#L95>`_



Inputs::

       inputspec.images :
       inputspec.fixed_image :
       inputspec.ListOfPassiveImagesDictionaries :

Outputs::

       outputspec.template :
       outputspec.transforms_list :
       outputspec.passive_deformed_templates :


Graph
~~~~~

.. graphviz::

	digraph ANTSTemplateBuildSingleIterationWF_{

	  label="ANTSTemplateBuildSingleIterationWF_";

	  ANTSTemplateBuildSingleIterationWF__inputspec[label="inputspec (utility)"];

	  ANTSTemplateBuildSingleIterationWF__BeginANTS[label="BeginANTS (ants)"];

	  ANTSTemplateBuildSingleIterationWF__MakeTransformsLists[label="MakeTransformsLists (utility)"];

	  ANTSTemplateBuildSingleIterationWF__99_FlattenTransformAndImagesList[label="99_FlattenTransformAndImagesList (utility)"];

	  ANTSTemplateBuildSingleIterationWF__AvgAffineTransform[label="AvgAffineTransform (ants)"];

	  ANTSTemplateBuildSingleIterationWF__wimtdeformed[label="wimtdeformed (ants)"];

	  ANTSTemplateBuildSingleIterationWF__AvgDeformedImages[label="AvgDeformedImages (ants)"];

	  ANTSTemplateBuildSingleIterationWF__wimtPassivedeformed[label="wimtPassivedeformed (ants)"];

	  ANTSTemplateBuildSingleIterationWF__99_RenestDeformedPassiveImages[label="99_RenestDeformedPassiveImages (utility)"];

	  ANTSTemplateBuildSingleIterationWF__AvgDeformedPassiveImages[label="AvgDeformedPassiveImages (ants)"];

	  ANTSTemplateBuildSingleIterationWF__AvgWarpImages[label="AvgWarpImages (ants)"];

	  ANTSTemplateBuildSingleIterationWF__GradientStepWarpImage[label="GradientStepWarpImage (ants)"];

	  ANTSTemplateBuildSingleIterationWF__UpdateTemplateShape[label="UpdateTemplateShape (ants)"];

	  ANTSTemplateBuildSingleIterationWF__MakeTransformListWithGradientWarps[label="MakeTransformListWithGradientWarps (utility)"];

	  ANTSTemplateBuildSingleIterationWF__ReshapeAveragePassiveImageWithShapeUpdate[label="ReshapeAveragePassiveImageWithShapeUpdate (ants)"];

	  ANTSTemplateBuildSingleIterationWF__ReshapeAverageImageWithShapeUpdate[label="ReshapeAverageImageWithShapeUpdate (ants)"];

	  ANTSTemplateBuildSingleIterationWF__outputspec[label="outputspec (utility)"];

	  ANTSTemplateBuildSingleIterationWF__inputspec -> ANTSTemplateBuildSingleIterationWF__99_FlattenTransformAndImagesList;

	  ANTSTemplateBuildSingleIterationWF__inputspec -> ANTSTemplateBuildSingleIterationWF__BeginANTS;

	  ANTSTemplateBuildSingleIterationWF__inputspec -> ANTSTemplateBuildSingleIterationWF__BeginANTS;

	  ANTSTemplateBuildSingleIterationWF__inputspec -> ANTSTemplateBuildSingleIterationWF__wimtdeformed;

	  ANTSTemplateBuildSingleIterationWF__BeginANTS -> ANTSTemplateBuildSingleIterationWF__AvgAffineTransform;

	  ANTSTemplateBuildSingleIterationWF__BeginANTS -> ANTSTemplateBuildSingleIterationWF__MakeTransformsLists;

	  ANTSTemplateBuildSingleIterationWF__BeginANTS -> ANTSTemplateBuildSingleIterationWF__MakeTransformsLists;

	  ANTSTemplateBuildSingleIterationWF__BeginANTS -> ANTSTemplateBuildSingleIterationWF__AvgWarpImages;

	  ANTSTemplateBuildSingleIterationWF__MakeTransformsLists -> ANTSTemplateBuildSingleIterationWF__wimtdeformed;

	  ANTSTemplateBuildSingleIterationWF__MakeTransformsLists -> ANTSTemplateBuildSingleIterationWF__99_FlattenTransformAndImagesList;

	  ANTSTemplateBuildSingleIterationWF__99_FlattenTransformAndImagesList -> ANTSTemplateBuildSingleIterationWF__wimtPassivedeformed;

	  ANTSTemplateBuildSingleIterationWF__99_FlattenTransformAndImagesList -> ANTSTemplateBuildSingleIterationWF__wimtPassivedeformed;

	  ANTSTemplateBuildSingleIterationWF__99_FlattenTransformAndImagesList -> ANTSTemplateBuildSingleIterationWF__99_RenestDeformedPassiveImages;

	  ANTSTemplateBuildSingleIterationWF__AvgAffineTransform -> ANTSTemplateBuildSingleIterationWF__MakeTransformListWithGradientWarps;

	  ANTSTemplateBuildSingleIterationWF__AvgAffineTransform -> ANTSTemplateBuildSingleIterationWF__UpdateTemplateShape;

	  ANTSTemplateBuildSingleIterationWF__wimtdeformed -> ANTSTemplateBuildSingleIterationWF__AvgDeformedImages;

	  ANTSTemplateBuildSingleIterationWF__AvgDeformedImages -> ANTSTemplateBuildSingleIterationWF__wimtPassivedeformed;

	  ANTSTemplateBuildSingleIterationWF__AvgDeformedImages -> ANTSTemplateBuildSingleIterationWF__UpdateTemplateShape;

	  ANTSTemplateBuildSingleIterationWF__AvgDeformedImages -> ANTSTemplateBuildSingleIterationWF__ReshapeAverageImageWithShapeUpdate;

	  ANTSTemplateBuildSingleIterationWF__AvgDeformedImages -> ANTSTemplateBuildSingleIterationWF__ReshapeAverageImageWithShapeUpdate;

	  ANTSTemplateBuildSingleIterationWF__wimtPassivedeformed -> ANTSTemplateBuildSingleIterationWF__99_RenestDeformedPassiveImages;

	  ANTSTemplateBuildSingleIterationWF__99_RenestDeformedPassiveImages -> ANTSTemplateBuildSingleIterationWF__ReshapeAveragePassiveImageWithShapeUpdate;

	  ANTSTemplateBuildSingleIterationWF__99_RenestDeformedPassiveImages -> ANTSTemplateBuildSingleIterationWF__AvgDeformedPassiveImages;

	  ANTSTemplateBuildSingleIterationWF__99_RenestDeformedPassiveImages -> ANTSTemplateBuildSingleIterationWF__AvgDeformedPassiveImages;

	  ANTSTemplateBuildSingleIterationWF__AvgDeformedPassiveImages -> ANTSTemplateBuildSingleIterationWF__ReshapeAveragePassiveImageWithShapeUpdate;

	  ANTSTemplateBuildSingleIterationWF__AvgDeformedPassiveImages -> ANTSTemplateBuildSingleIterationWF__ReshapeAveragePassiveImageWithShapeUpdate;

	  ANTSTemplateBuildSingleIterationWF__AvgWarpImages -> ANTSTemplateBuildSingleIterationWF__GradientStepWarpImage;

	  ANTSTemplateBuildSingleIterationWF__GradientStepWarpImage -> ANTSTemplateBuildSingleIterationWF__UpdateTemplateShape;

	  ANTSTemplateBuildSingleIterationWF__UpdateTemplateShape -> ANTSTemplateBuildSingleIterationWF__MakeTransformListWithGradientWarps;

	  ANTSTemplateBuildSingleIterationWF__MakeTransformListWithGradientWarps -> ANTSTemplateBuildSingleIterationWF__ReshapeAveragePassiveImageWithShapeUpdate;

	  ANTSTemplateBuildSingleIterationWF__MakeTransformListWithGradientWarps -> ANTSTemplateBuildSingleIterationWF__ReshapeAverageImageWithShapeUpdate;

	  ANTSTemplateBuildSingleIterationWF__ReshapeAveragePassiveImageWithShapeUpdate -> ANTSTemplateBuildSingleIterationWF__outputspec;

	  ANTSTemplateBuildSingleIterationWF__ReshapeAverageImageWithShapeUpdate -> ANTSTemplateBuildSingleIterationWF__outputspec;

	}


.. _nipype.workflows.smri.ants.ANTSBuildTemplate.FlattenTransformAndImagesList:

:func:`FlattenTransformAndImagesList`
-------------------------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/workflows/smri/ants/ANTSBuildTemplate.py#L68>`_






.. _nipype.workflows.smri.ants.ANTSBuildTemplate.GetFirstListElement:

:func:`GetFirstListElement`
---------------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/workflows/smri/ants/ANTSBuildTemplate.py#L23>`_






.. _nipype.workflows.smri.ants.ANTSBuildTemplate.MakeListsOfTransformLists:

:func:`MakeListsOfTransformLists`
---------------------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/workflows/smri/ants/ANTSBuildTemplate.py#L64>`_






.. _nipype.workflows.smri.ants.ANTSBuildTemplate.MakeTransformListWithGradientWarps:

:func:`MakeTransformListWithGradientWarps`
------------------------------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/workflows/smri/ants/ANTSBuildTemplate.py#L26>`_






.. _nipype.workflows.smri.ants.ANTSBuildTemplate.RenestDeformedPassiveImages:

:func:`RenestDeformedPassiveImages`
-----------------------------------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/workflows/smri/ants/ANTSBuildTemplate.py#L28>`_





