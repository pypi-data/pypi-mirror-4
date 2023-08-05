.. AUTO-GENERATED FILE -- DO NOT EDIT!

interfaces.meshfix
==================


.. _nipype.interfaces.meshfix.MeshFix:


.. index:: MeshFix

MeshFix
-------

`Link to code <http://github.com/nipy/nipype/tree/99796c15f2e157774a3f54f878fdd06ad981a80b/nipype/interfaces/meshfix.py#L65>`_

Wraps command **meshfix**

MeshFix v1.2-alpha - by Marco Attene, Mirko Windhoff, Axel Thielscher.

.. seealso::

    http://jmeshlib.sourceforge.net
        Sourceforge page

    http://simnibs.de/installation/meshfixandgetfem
        Ubuntu installation instructions

If MeshFix is used for research purposes, please cite the following paper:
M. Attene - A lightweight approach to repairing digitized polygon meshes.
The Visual Computer, 2010. (c) Springer.

Accepted input formats are OFF, PLY and STL.
Other formats (like .msh for gmsh) are supported only partially.

Example
~~~~~~~

>>> import nipype.interfaces.meshfix as mf
>>> fix = mf.MeshFix()
>>> fix.inputs.in_file1 = 'lh-pial.stl'
>>> fix.inputs.in_file2 = 'rh-pial.stl'
>>> fix.run()                                    # doctest: +SKIP

Inputs::

        [Mandatory]
        in_file1: (an existing file name)

        [Optional]
        args: (a string)
                Additional parameters to the command
        cut_inner: (an integer)
                Remove triangles of 1st that are inside of the 2nd shell. Dilate 2nd by N; Fill holes
                and keep only 1st afterwards.
        cut_outer: (an integer)
                Remove triangles of 1st that are outside of the 2nd shell.
        decouple_inin: (an integer)
                Treat 1st file as inner, 2nd file as outer component.Resolve overlaps by moving inners
                triangles inwards. Constrain the min distance between the components > d.
        decouple_outin: (an integer)
                Treat 1st file as outer, 2nd file as inner component.Resolve overlaps by moving outers
                triangles inwards. Constrain the min distance between the components > d.
        decouple_outout: (an integer)
                Treat 1st file as outer, 2nd file as inner component.Resolve overlaps by moving outers
                triangles outwards. Constrain the min distance between the components > d.
        dilation: (an integer)
                Dilate the surface by d. d < 0 means shrinking.
        dont_clean: (a boolean)
                Don't Clean
        environ: (a dictionary with keys which are a value of type 'str' and with values which
                 are a value of type 'str', nipype default value: {})
                Environment variables
        epsilon_angle: (a float)
                Epsilon angle in degrees (must be between 0 and 2)
        finetuning_distance: (a float)
                Used to fine-tune the minimal distance between surfaces.A minimal distance d is ensured,
                and reached in n substeps. When using the surfaces for subsequent volume meshing by
                gmsh, this step prevent too flat tetrahedra2)
        finetuning_inwards: (a boolean)
        finetuning_outwards: (a boolean)
                Similar to finetuning_inwards, but ensures minimal distance in the other direction
                mutually_exclusive: finetuning_inwards
        finetuning_substeps: (an integer)
                Used to fine-tune the minimal distance between surfaces.A minimal distance d is ensured,
                and reached in n substeps. When using the surfaces for subsequent volume meshing by
                gmsh, this step prevent too flat tetrahedra2)
        ignore_exception: (a boolean, nipype default value: False)
                Print an error message instead of throwing an exception in case the interface fails to
                run
        in_file2: (an existing file name)
        join_closest_components: (a boolean)
                Join the closest pair of components.
                mutually_exclusive: join_closest_components
        join_overlapping_largest_components: (a boolean)
                Join 2 biggest components if they overlap, remove the rest.
                mutually_exclusive: join_closest_components
        laplacian_smoothing_steps: (an integer)
                The number of laplacian smoothing steps to apply
        number_of_biggest_shells: (an integer)
                Only the N biggest shells are kept
        out_filename: (a file name)
                The output filename for the fixed mesh file
        output_type: ('stl' or 'msh' or 'wrl' or 'vrml' or 'fs' or 'off', nipype default value:
                 off)
                The output type to save the file as.
        quiet_mode: (a boolean)
                Quiet mode, don't write much to stdout.
        remove_handles: (a boolean)
                Remove handles
        save_as_freesurfer_mesh: (a boolean)
                Result is saved in freesurfer mesh format
                mutually_exclusive: save_as_vrml, save_as_stl
        save_as_stl: (a boolean)
                Result is saved in stereolithographic format (.stl)
                mutually_exclusive: save_as_vmrl, save_as_freesurfer_mesh
        save_as_vmrl: (a boolean)
                Result is saved in VRML1.0 format (.wrl)
                mutually_exclusive: save_as_stl, save_as_freesurfer_mesh
        set_intersections_to_one: (a boolean)
                If the mesh contains intersections, return value = 1.If saved in gmsh format,
                intersections will be highlighted.
        uniform_remeshing_steps: (an integer)
                Number of steps for uniform remeshing of the whole mesh
        uniform_remeshing_vertices: (an integer)
                Constrains the number of vertices.Must be used with uniform_remeshing_steps
        x_shift: (an integer)
                Shifts the coordinates of the vertices when saving. Output must be in FreeSurfer format

Outputs::

        mesh_file: (an existing file name)
                The output mesh file
