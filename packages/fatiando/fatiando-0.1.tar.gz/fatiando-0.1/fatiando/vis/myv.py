"""
Wrappers for calls to Mayavi2's `mlab` module for plotting
:mod:`fatiando.mesher` objects and automating common tasks.

**Objects**

* :func:`~fatiando.vis.myv.prisms`
* :func:`~fatiando.vis.myv.polyprisms`
* :func:`~fatiando.vis.myv.points`
* :func:`~fatiando.vis.myv.tesseroids`

**Misc objects**

* :func:`~fatiando.vis.myv.outline`
* :func:`~fatiando.vis.myv.axes`
* :func:`~fatiando.vis.myv.wall_north`
* :func:`~fatiando.vis.myv.wall_south`
* :func:`~fatiando.vis.myv.wall_east`
* :func:`~fatiando.vis.myv.wall_west`
* :func:`~fatiando.vis.myv.wall_top`
* :func:`~fatiando.vis.myv.wall_bottom`
* :func:`~fatiando.vis.myv.earth`
* :func:`~fatiando.vis.myv.core`
* :func:`~fatiando.vis.myv.continents`
* :func:`~fatiando.vis.myv.meridians`
* :func:`~fatiando.vis.myv.parallels`

**Helpers**

* :func:`~fatiando.vis.myv.figure`
* :func:`~fatiando.vis.myv.title`
* :func:`~fatiando.vis.myv.show`
* :func:`~fatiando.vis.myv.savefig`

----

"""
import numpy

import fatiando.logger
from fatiando import utils
from fatiando.constants import MEAN_EARTH_RADIUS


log = fatiando.logger.dummy('fatiando.vis.myv')

# Do lazy imports of mlab and tvtk to avoid the slow imports when I don't need
# 3D plotting
mlab = None
tvtk = None
BuiltinSurface = None

def _lazy_import_BuiltinSurface():
    """
    Do the lazy import of BuiltinSurface
    """
    global BuiltinSurface
    if BuiltinSurface is None:
        from mayavi.sources.builtin_surface import BuiltinSurface

def _lazy_import_mlab():
    """
    Do the lazy import of mlab
    """
    global mlab
    # For campatibility with versions of Mayavi2 < 4
    if mlab is None:
        try:
            from mayavi import mlab
        except ImportError:
            from enthought.mayavi import mlab

def _lazy_import_tvtk():
    """
    Do the lazy import of tvtk
    """
    global tvtk
    # For campatibility with versions of Mayavi2 < 4
    if tvtk is None:
        try:
            from tvtk.api import tvtk
        except ImportError:
            from enthought.tvtk.api import tvtk

def title(text, color=(0, 0, 0),  size=0.3, height=1):
    """
    Draw a title on a Mayavi figure.

    .. warning:: Must be called **after** you've plotted something (e.g.,
        prisms) to the figure. This is a bug.

    Parameters:

    * text : str
        The title
    * color : tuple = (r, g, b)
        RGB of the color of the text
    * size : float
        The size of the text
    * height : float
        The height where the title will be placed on the screen

    """
    _lazy_import_mlab()
    mlab.title(text, color=color, size=size, height=height)

def savefig(fname, magnification=None):
    """
    Save a snapshot the current Mayavi figure to a file.

    Parameters:

    * fname : str
        The name of the file. The format is deduced from the extension.
    * magnification : int or None
        If not None, then the scaling between the pixels on the screen, and the
        pixels in the file saved.

    """
    _lazy_import_mlab()
    if magnification is None:
        mlab.savefig(fname)
    else:
        mlab.savefig(fname, magnification=magnification)

def show():
    """
    Show the 3D plot of Mayavi2.

    Enters a loop until the window is closed.
    """
    _lazy_import_mlab()
    mlab.show()

def points(points, color=(0, 0, 0), opacity=1, size=200.):
    """
    Plot a series of 3D points.

    .. note:: Still doesn't plot points with physical properties.

    Parameters:

    * points : list
        The list of points to plot. Each point is an [x, y, z] list with the
        x, y, and z coordinates of the point
    * color : tuple = (r, g, b)
        RGB of the color of the points
    * opacity : float
        Decimal percentage of opacity
    * size : float
        The size of the points (relative to their spacing)

    """
    _lazy_import_mlab()
    x, y, z = numpy.transpose(points)
    mlab.points3d(x, y, z, color=color, opacity=opacity, scale_factor=size)

def polyprisms(prisms, prop=None, style='surface', opacity=1, edges=True,
    vmin=None, vmax=None, cmap='blue-red', linewidth=0.1):
    """
    Plot a list of 3D polygonal prisms using Mayavi2.

    Will not plot a value None in *prisms*.

    Parameters:

    * prisms : list of :class:`fatiando.mesher.PolygonalPrism`
        The prisms
    * prop : str or None
        The physical property of the prisms to use as the color scale. If a
        prism doesn't have *prop*, or if it is None, then it will not be plotted
    * style : str
        Either ``'surface'`` for solid prisms or ``'wireframe'`` for just the
        contour
    * opacity : float
        Decimal percentage of opacity
    * edges : True or False
        Wether or not to display the edges of the prisms in black lines. Will
        ignore this if ``style='wireframe'``
    * vmin, vmax : float
        Min and max values for the color scale. If *None* will default to
        the min and max of *prop* in the prisms.
    * cmap : Mayavi colormap
        Color map to use. See the 'Colors and Legends' menu on the Mayavi2 GUI
        for valid color maps.
    * linewidth : float
        The width of the lines (edges) of the prisms.

    Returns:

    * surface
        the last element on the pipeline

    """
    if style not in ['surface', 'wireframe']:
        raise ValueError, "Invalid style '%s'" % (style)
    if opacity > 1. or opacity < 0:
        msg = "Invalid opacity %g. Must be in range [1,0]" % (opacity)
        raise ValueError, msg
    # mlab and tvtk are really slow to import
    _lazy_import_mlab()
    _lazy_import_tvtk()

    if prop is None:
        label = 'scalar'
    else:
        label = prop
    points = []
    polygons = []
    scalars = []
    offset = 0
    for prism in prisms:
        if prism is None or (prop is not None and prop not in prism.props):
            continue
        x, y = prism.x, prism.y
        nverts = prism.nverts
        scalar = prism.props[prop]
        # The top surface
        points.extend(
            reversed(numpy.transpose([x, y, prism.z1*numpy.ones_like(x)])))
        polygons.append(range(offset, offset + nverts))
        scalars.extend(scalar*numpy.ones(nverts))
        offset += nverts
        # The bottom surface
        points.extend(
            reversed(numpy.transpose([x, y, prism.z2*numpy.ones_like(x)])))
        polygons.append(range(offset, offset + nverts))
        scalars.extend(scalar*numpy.ones(nverts))
        offset += nverts
        # The sides
        for i in xrange(nverts):
            x1, y1 = x[i], y[i]
            x2, y2 = x[(i + 1)%nverts], y[(i + 1)%nverts]
            points.extend([[x1, y1, prism.z1], [x2, y2, prism.z1],
                           [x2, y2, prism.z2], [x1, y1, prism.z2]])
            polygons.append(range(offset, offset + 4))
            scalars.extend(scalar*numpy.ones(4))
            offset += 4
    mesh = tvtk.PolyData(points=points, polys=polygons)
    mesh.point_data.scalars = numpy.array(scalars)
    mesh.point_data.scalars.name = label
    if vmin is None:
        vmin = min(scalars)
    if vmax is None:
        vmax = max(scalars)
    if style == 'wireframe':
        surf = mlab.pipeline.surface(mlab.pipeline.add_dataset(mesh),
                                     vmax=vmax, vmin=vmin, colormap=cmap)
        surf.actor.property.representation = 'wireframe'
        surf.actor.property.line_width = linewidth
    if style == 'surface':
        # The triangle filter is needed because VTK doesnt seem to handle convex
        # polygons too well
        dataset = mlab.pipeline.triangle_filter(mlab.pipeline.add_dataset(mesh))
        surf = mlab.pipeline.surface(dataset, vmax=vmax, vmin=vmin,
                                     colormap=cmap)
        surf.actor.property.representation = 'surface'
        surf.actor.property.edge_visibility = 0
        if edges:
            edge = mlab.pipeline.surface(mlab.pipeline.add_dataset(mesh))
            edge.actor.property.representation = 'wireframe'
            edge.actor.mapper.scalar_visibility = 0
            edge.actor.property.line_width = linewidth
            edge.actor.property.opacity = opacity
    surf.actor.property.opacity = opacity
    return surf

def tesseroids(tesseroids, prop=None, style='surface', opacity=1, edges=True,
    vmin=None, vmax=None, cmap='blue-red', linewidth=0.1):
    """
    Plot a list of tesseroids using Mayavi2.

    Will not plot a value None in *tesseroids*

    Parameters:

    * tesseroids : list of :class:`fatiando.mesher.Tesseroid`
        The prisms
    * prop : str or None
        The physical property of the tesseroids to use as the color scale. If a
        tesseroid doesn't have *prop*, or if it is None, then it will not be
        plotted
    * style : str
        Either ``'surface'`` for solid tesseroids or ``'wireframe'`` for just
        the contour
    * opacity : float
        Decimal percentage of opacity
    * edges : True or False
        Wether or not to display the edges of the tesseroids in black lines.
        Will ignore this if ``style='wireframe'``
    * vmin, vmax : float
        Min and max values for the color scale. If *None* will default to
        the min and max of *prop*.
    * cmap : Mayavi colormap
        Color map to use. See the 'Colors and Legends' menu on the Mayavi2 GUI
        for valid color maps.
    * linewidth : float
        The width of the lines (edges).

    Returns:

    * surface
        the last element on the pipeline

    """
    if style not in ['surface', 'wireframe']:
        raise ValueError, "Invalid style '%s'" % (style)
    if opacity > 1. or opacity < 0:
        msg = "Invalid opacity %g. Must be in range [1,0]" % (opacity)
        raise ValueError, msg

    # mlab and tvtk are really slow to import
    _lazy_import_mlab()
    _lazy_import_tvtk()

    if prop is None:
        label = 'scalar'
    else:
        label = prop
    # VTK parameters
    points = []
    cells = []
    offsets = []
    offset = 0
    mesh_size = 0
    celldata = []
    # To mark what index in the points the cell starts
    start = 0
    for tess in tesseroids:
        if tess is None or (prop is not None and prop not in tess.props):
            continue
        w, e, s, n, top, bottom = tess.get_bounds()
        if prop is None:
            scalar = 0.
        else:
            scalar = tess.props[prop]
        points.extend([
            utils.sph2cart(w, s, bottom),
            utils.sph2cart(e, s, bottom),
            utils.sph2cart(e, n, bottom),
            utils.sph2cart(w, n, bottom),
            utils.sph2cart(w, s, top),
            utils.sph2cart(e, s, top),
            utils.sph2cart(e, n, top),
            utils.sph2cart(w, n, top),
            utils.sph2cart(0.5*(w + e), s, bottom),
            utils.sph2cart(e, 0.5*(s + n), bottom),
            utils.sph2cart(0.5*(w + e), n, bottom),
            utils.sph2cart(w, 0.5*(s + n), bottom),
            utils.sph2cart(0.5*(w + e), s, top),
            utils.sph2cart(e, 0.5*(s + n), top),
            utils.sph2cart(0.5*(w + e), n, top),
            utils.sph2cart(w, 0.5*(s + n), top),
            utils.sph2cart(w, s, 0.5*(top + bottom)),
            utils.sph2cart(e, s, 0.5*(top + bottom)),
            utils.sph2cart(e, n, 0.5*(top + bottom)),
            utils.sph2cart(w, n, 0.5*(top + bottom))])
        cells.append(20)
        cells.extend(range(start, start + 20))
        start += 20
        offsets.append(offset)
        offset += 21
        celldata.append(scalar)
        mesh_size += 1
    cell_array = tvtk.CellArray()
    cell_array.set_cells(mesh_size, numpy.array(cells))
    cell_types = numpy.array([25]*mesh_size, 'i')
    vtkmesh = tvtk.UnstructuredGrid(points=numpy.array(points, 'f'))
    vtkmesh.set_cells(cell_types, numpy.array(offsets, 'i'), cell_array)
    vtkmesh.cell_data.scalars = numpy.array(celldata)
    vtkmesh.cell_data.scalars.name = label
    dataset = mlab.pipeline.threshold(mlab.pipeline.add_dataset(vtkmesh))
    if vmin is None:
        vmin = min(vtkmesh.cell_data.scalars)
    if vmax is None:
        vmax = max(vtkmesh.cell_data.scalars)
    if style == 'wireframe':
        surf = mlab.pipeline.surface(mlab.pipeline.extract_edges(dataset),
            vmax=vmax, vmin=vmin, colormap=cmap)
        surf.actor.property.representation = 'wireframe'
        surf.actor.property.line_width = linewidth
    if style == 'surface':
        surf = mlab.pipeline.surface(dataset, vmax=vmax, vmin=vmin,
            colormap=cmap)
        surf.actor.property.representation = 'surface'
        if edges:
            edge = mlab.pipeline.surface(mlab.pipeline.extract_edges(dataset),
                vmax=vmax, vmin=vmin)
            edge.actor.property.representation = 'wireframe'
            edge.actor.mapper.scalar_visibility = 0
            edge.actor.property.line_width = linewidth
            edge.actor.property.opacity = opacity
    surf.actor.property.opacity = opacity
    surf.actor.property.backface_culling = 1
    return surf

def prisms(prisms, prop=None, style='surface', opacity=1, edges=True,
    vmin=None, vmax=None, cmap='blue-red', linewidth=0.1):
    """
    Plot a list of 3D right rectangular prisms using Mayavi2.

    Will not plot a value None in *prisms*

    Parameters:

    * prisms : list of :class:`fatiando.mesher.Prism`
        The prisms
    * prop : str or None
        The physical property of the prisms to use as the color scale. If a
        prism doesn't have *prop*, or if it is None, then it will not be plotted
    * style : str
        Either ``'surface'`` for solid prisms or ``'wireframe'`` for just the
        contour
    * opacity : float
        Decimal percentage of opacity
    * edges : True or False
        Wether or not to display the edges of the prisms in black lines. Will
        ignore this if ``style='wireframe'``
    * vmin, vmax : float
        Min and max values for the color scale. If *None* will default to
        the min and max of *prop* in the prisms.
    * cmap : Mayavi colormap
        Color map to use. See the 'Colors and Legends' menu on the Mayavi2 GUI
        for valid color maps.
    * linewidth : float
        The width of the lines (edges) of the prisms.

    Returns:

    * surface
        the last element on the pipeline

    """
    if style not in ['surface', 'wireframe']:
        raise ValueError, "Invalid style '%s'" % (style)
    if opacity > 1. or opacity < 0:
        msg = "Invalid opacity %g. Must be in range [1,0]" % (opacity)
        raise ValueError, msg

    # mlab and tvtk are really slow to import
    _lazy_import_mlab()
    _lazy_import_tvtk()

    if prop is None:
        label = 'scalar'
    else:
        label = prop
    # VTK parameters
    points = []
    cells = []
    offsets = []
    offset = 0
    mesh_size = 0
    celldata = []
    # To mark what index in the points the cell starts
    start = 0
    for prism in prisms:
        if prism is None or (prop is not None and prop not in prism.props):
            continue
        x1, x2, y1, y2, z1, z2 = prism.get_bounds()
        if prop is None:
            scalar = 0.
        else:
            scalar = prism.props[prop]
        points.extend([[x1, y1, z1], [x2, y1, z1], [x2, y2, z1], [x1, y2, z1],
                       [x1, y1, z2], [x2, y1, z2], [x2, y2, z2], [x1, y2, z2]])
        cells.append(8)
        cells.extend([i for i in xrange(start, start + 8)])
        start += 8
        offsets.append(offset)
        offset += 9
        celldata.append(scalar)
        mesh_size += 1
    cell_array = tvtk.CellArray()
    cell_array.set_cells(mesh_size, numpy.array(cells))
    cell_types = numpy.array([12]*mesh_size, 'i')
    vtkmesh = tvtk.UnstructuredGrid(points=numpy.array(points, 'f'))
    vtkmesh.set_cells(cell_types, numpy.array(offsets, 'i'), cell_array)
    vtkmesh.cell_data.scalars = numpy.array(celldata)
    vtkmesh.cell_data.scalars.name = label
    dataset = mlab.pipeline.threshold(mlab.pipeline.add_dataset(vtkmesh))
    if vmin is None:
        vmin = min(vtkmesh.cell_data.scalars)
    if vmax is None:
        vmax = max(vtkmesh.cell_data.scalars)
    surf = mlab.pipeline.surface(dataset, vmax=vmax, vmin=vmin, colormap=cmap)
    if style == 'wireframe':
        surf.actor.property.representation = 'wireframe'
        surf.actor.property.line_width = linewidth
    if style == 'surface':
        surf.actor.property.representation = 'surface'
        if edges:
            surf.actor.property.edge_visibility = 1
            surf.actor.property.line_width = linewidth
    surf.actor.property.opacity = opacity
    surf.actor.property.backface_culling = 1
    return surf

def figure(size=None, zdown=True):
    """
    Create a default figure in Mayavi with white background

    Parameters:

    * size : tuple = (dx, dy)
        The size of the figure. If ``None`` will use the default size.
    * zdown : True or False
        If True, will turn the figure upside-down to make the z-axis point down

    Return:

    * fig : Mayavi figure object
        The figure

    """
    _lazy_import_mlab()
    if size is None:
        fig = mlab.figure(bgcolor=(1, 1, 1))
    else:
        fig = mlab.figure(bgcolor=(1, 1, 1), size=size)
    if zdown:
        fig.scene.camera.view_up = numpy.array([0., 0., -1.])
        fig.scene.camera.elevation(60.)
        fig.scene.camera.azimuth(180.)
    return fig

def outline(extent=None, color=(0,0,0), width=2):
    """
    Create a default outline in Mayavi2.

    Parameters:

    * extent : list = [xmin, xmax, ymin, ymax, zmin, zmax]
        Default if the objects extent.
    * color : tuple = (r, g, b)
        RGB of the color of the axes and text
    * width : float
        Line width

    Returns:

    * outline : Mayavi outline instace
        The outline in the pipeline

    """
    _lazy_import_mlab()
    outline = mlab.outline(color=color, line_width=width)
    if extent is not None:
        outline.bounds = extent
    return outline

def axes(plot, nlabels=5, extent=None, ranges=None, color=(0,0,0),
             width=2, fmt="%-#.2f"):
    """
    Add an Axes module to a Mayavi2 plot or dataset.

    Parameters:

    * plot
        Either the plot (as returned by one of the plotting functions of this
        module) or a TVTK dataset.
    * nlabels : int
        Number of labels on the axes
    * extent : list = [xmin, xmax, ymin, ymax, zmin, zmax]
        Default if the objects extent.
    * ranges : list = [xmin, xmax, ymin, ymax, zmin, zmax]
        What will be display in the axes labels. Default is *extent*
    * color : tuple = (r, g, b)
        RGB of the color of the axes and text
    * width : float
        Line width
    * fmt : str
        Label number format

    Returns:

    * axes : Mayavi axes instace
        The axes object in the pipeline

    """
    _lazy_import_mlab()
    a = mlab.axes(plot, nb_labels=nlabels, color=color)
    a.label_text_property.color = color
    a.title_text_property.color = color
    if extent is not None:
        a.axes.bounds = extent
    if ranges is not None:
        a.axes.ranges = ranges
        a.axes.use_ranges = True
    a.property.line_width = width
    a.axes.label_format = fmt
    a.axes.x_label, a.axes.y_label, a.axes.z_label = "N", "E", "Z"
    return a

def wall_north(bounds, color=(0,0,0), opacity=0.1):
    """
    Draw a 3D wall in Mayavi2 on the North side.

    .. note:: Remember that x->North, y->East and z->Down

    Parameters:

    * bounds : list = [xmin, xmax, ymin, ymax, zmin, zmax]
        The extent of the region where the wall is placed
    * color : tuple = (r, g, b)
        RGB of the color of the wall
    * opacity : float
        Decimal percentage of opacity

    .. tip:: You can use :func:`~fatiando.vis.myv.add_axes` to create and
        `axes` variable and get the bounds as ``axes.axes.bounds``

    """
    s, n, w, e, t, b = bounds
    _wall([n, n, w, e, b, t], color, opacity)

def wall_south(bounds, color=(0,0,0), opacity=0.1):
    """
    Draw a 3D wall in Mayavi2 on the South side.

    .. note:: Remember that x->North, y->East and z->Down

    Parameters:

    * bounds : list = [xmin, xmax, ymin, ymax, zmin, zmax]
        The extent of the region where the wall is placed
    * color : tuple = (r, g, b)
        RGB of the color of the wall
    * opacity : float
        Decimal percentage of opacity

    .. tip:: You can use :func:`~fatiando.vis.myv.add_axes` to create and
        `axes` variable and get the bounds as ``axes.axes.bounds``

    """
    s, n, w, e, t, b = bounds
    _wall([s, s, w, e, b, t], color, opacity)

def wall_east(bounds, color=(0,0,0), opacity=0.1):
    """
    Draw a 3D wall in Mayavi2 on the East side.

    .. note:: Remember that x->North, y->East and z->Down

    Parameters:

    * bounds : list = [xmin, xmax, ymin, ymax, zmin, zmax]
        The extent of the region where the wall is placed
    * color : tuple = (r, g, b)
        RGB of the color of the wall
    * opacity : float
        Decimal percentage of opacity

    .. tip:: You can use :func:`~fatiando.vis.myv.add_axes` to create and
        `axes` variable and get the bounds as ``axes.axes.bounds``

    """
    s, n, w, e, t, b = bounds
    _wall([s, n, e, e, b, t], color, opacity)

def wall_west(bounds, color=(0,0,0), opacity=0.1):
    """
    Draw a 3D wall in Mayavi2 on the West side.

    .. note:: Remember that x->North, y->East and z->Down

    Parameters:

    * bounds : list = [xmin, xmax, ymin, ymax, zmin, zmax]
        The extent of the region where the wall is placed
    * color : tuple = (r, g, b)
        RGB of the color of the wall
    * opacity : float
        Decimal percentage of opacity

    .. tip:: You can use :func:`~fatiando.vis.myv.add_axes` to create and
        `axes` variable and get the bounds as ``axes.axes.bounds``

    """
    s, n, w, e, t, b = bounds
    _wall([s, n, w, w, b, t], color, opacity)

def wall_top(bounds, color=(0,0,0), opacity=0.1):
    """
    Draw a 3D wall in Mayavi2 on the Top side.

    .. note:: Remember that x->North, y->East and z->Down

    Parameters:

    * bounds : list = [xmin, xmax, ymin, ymax, zmin, zmax]
        The extent of the region where the wall is placed
    * color : tuple = (r, g, b)
        RGB of the color of the wall
    * opacity : float
        Decimal percentage of opacity

    .. tip:: You can use :func:`~fatiando.vis.myv.add_axes` to create and
        `axes` variable and get the bounds as ``axes.axes.bounds``

    """
    s, n, w, e, t, b = bounds
    _wall([s, n, w, e, t, t], color, opacity)

def wall_bottom(bounds, color=(0,0,0), opacity=0.1):
    """
    Draw a 3D wall in Mayavi2 on the Bottom side.

    .. note:: Remember that x->North, y->East and z->Down

    Parameters:

    * bounds : list = [xmin, xmax, ymin, ymax, zmin, zmax]
        The extent of the region where the wall is placed
    * color : tuple = (r, g, b)
        RGB of the color of the wall
    * opacity : float
        Decimal percentage of opacity

    .. tip:: You can use :func:`~fatiando.vis.myv.add_axes` to create and
        `axes` variable and get the bounds as ``axes.axes.bounds``

    """
    s, n, w, e, t, b = bounds
    _wall([s, n, w, e, b, b], color, opacity)

def _wall(bounds, color, opacity):
    """Generate a 3D wall in Mayavi"""
    _lazy_import_mlab()
    p = mlab.pipeline.builtin_surface()
    p.source = 'outline'
    p.data_source.bounds = bounds
    p.data_source.generate_faces = 1
    su = mlab.pipeline.surface(p)
    su.actor.property.color = color
    su.actor.property.opacity = opacity

def continents(color=(0, 0, 0), linewidth=1, resolution=2, opacity=1,
    radius=MEAN_EARTH_RADIUS):
    """
    Plot the outline of the continents.

    Parameters:

    * color : tuple
        RGB color of the lines. Default = black
    * linewidth : float
        The width of the continent lines
    * resolution : float
        The data_source.on_ratio parameter that controls the resolution of the
        continents
    * opacity : float
        The opacity of the lines. Must be between 0 and 1
    * radius : float
        The radius of the sphere where the continents will be plotted. Defaults
        to the mean Earth radius

    Returns:

    * continents : Mayavi surface
        The Mayavi surface element of the continents

    """
    _lazy_import_mlab()
    _lazy_import_BuiltinSurface()
    continents_src = BuiltinSurface(source='earth', name='Continents')
    continents_src.data_source.on_ratio = resolution
    continents_src.data_source.radius = MEAN_EARTH_RADIUS
    surf = mlab.pipeline.surface(continents_src, color=color)
    surf.actor.property.line_width = linewidth
    surf.actor.property.opacity = opacity
    return surf

def earth(color=(0.4, 0.5, 1.0), opacity=1):
    """
    Draw a sphere representing the Earth.

    Parameters:

    * color : tuple
        RGB color of the sphere. Defaults to ocean blue.
    * opacity : float
        The opacity of the sphere. Must be between 0 and 1

    Returns:

    * sphere : Mayavi surface
        The Mayavi surface element of the sphere

    """
    _lazy_import_mlab()
    sphere = mlab.points3d(0, 0, 0, scale_mode='none',
        scale_factor=2*MEAN_EARTH_RADIUS, color=color, resolution=50,
        opacity=opacity, name='Earth')
    sphere.actor.property.specular = 0.45
    sphere.actor.property.specular_power = 5
    sphere.actor.property.backface_culling = True
    return sphere

def core(inner=False, color=(1, 0, 0), opacity=1):
    """
    Draw a sphere representing the Earth's core.

    Parameters:

    * inner : True or False
        If True, will use the radius of the inner core, else the outer core.
    * color : tuple
        RGB color of the sphere. Defaults to red.
    * opacity : float
        The opacity of the sphere. Must be between 0 and 1

    Returns:

    * sphere : Mayavi surface
        The Mayavi surface element of the sphere

    """
    _lazy_import_mlab()
    if inner:
        radius = 1216000.
        name = 'Inner core'
    else:
        radius = 3486000.
        name = 'Core'
    sphere = mlab.points3d(0, 0, 0, scale_mode='none',
        scale_factor=2.*radius, color=color, resolution=50,
        opacity=opacity, name=name)
    sphere.actor.property.specular = 0.45
    sphere.actor.property.specular_power = 5
    sphere.actor.property.backface_culling = True
    return sphere

def meridians(longitudes, color=(0, 0, 0), linewidth=1, opacity=1):
    """
    Draw meridians on the Earth.

    Parameters:

    * longitudes : list
        The longitudes where the meridians will be drawn.
    * color : tuple
        RGB color of the lines. Defaults to black.
    * linewidth : float
        The width of the lines
    * opacity : float
        The opacity of the lines. Must be between 0 and 1

    Returns:

    * lines : Mayavi surface
        The Mayavi surface element of the lines

    """
    lats = numpy.linspace(-90, 270., 100)
    x, y, z = [], [], []
    for lon in longitudes:
        coords = utils.sph2cart(numpy.ones_like(lats)*lon, lats, 0)
        x.extend(coords[0].tolist())
        y.extend(coords[1].tolist())
        z.extend(coords[2].tolist())
    x, y, z = numpy.array(x), numpy.array(y), numpy.array(z)
    lines = mlab.plot3d(x, y, z, color=color, opacity=opacity,
        tube_radius=None)
    lines.actor.property.line_width = linewidth
    return lines

def parallels(latitudes, color=(0, 0, 0), linewidth=1, opacity=1):
    """
    Draw parallels on the Earth.

    Parameters:

    * latitudes : list
        The latitudes where the parallels will be drawn.
    * color : tuple
        RGB color of the lines. Defaults to black.
    * linewidth : float
        The width of the lines
    * opacity : float
        The opacity of the lines. Must be between 0 and 1

    Returns:

    * lines : list
        List of the Mayavi surface elements of each line

    """
    lons = numpy.linspace(0, 360., 100)
    parallels = []
    for lat in latitudes:
        x, y, z = utils.sph2cart(lons, numpy.ones_like(lons)*lat, 0)
        lines = mlab.plot3d(x, y, z, color=color, opacity=opacity,
            tube_radius=None)
        lines.actor.property.line_width = linewidth
        parallels.append(lines)
    return parallels
