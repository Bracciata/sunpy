"""A Composite Map class

Author: `Keith Hughitt <keith.hughitt@nasa.gov>`
"""
import matplotlib.pyplot as plt

import astropy.units as u

from sunpy.map import GenericMap
from sunpy.util import expand_list
from sunpy.visualization import axis_labels_from_ctype, peek_show, wcsaxes_compat

__all__ = ['CompositeMap']

__author__ = "Keith Hughitt"
__email__ = "keith.hughitt@nasa.gov"


class CompositeMap:
    """
    CompositeMap(map1 [,map2,..])

    A Composite Map class

    Parameters
    ----------
    args : [`~sunpy.map.Map` | string]
        One or more map of filepaths

    Examples
    --------
    >>> import sunpy.map
    >>> import sunpy.data.sample  # doctest: +REMOTE_DATA
    >>> comp_map = sunpy.map.Map(sunpy.data.sample.AIA_171_IMAGE,
    ...                          sunpy.data.sample.EIT_195_IMAGE,
    ...                          composite=True)  # doctest: +REMOTE_DATA
    >>> comp_map.add_map(sunpy.map.Map(sunpy.data.sample.RHESSI_IMAGE))  # doctest: +REMOTE_DATA
    >>> comp_map.peek()  # doctest: +SKIP

    """

    def __init__(self, *args, **kwargs):
        self._maps = expand_list(args)

        for m in self._maps:
            if not isinstance(m, GenericMap):
                raise ValueError(
                    'CompositeMap expects pre-constructed map objects.')

        # Default alpha and zorder values
        alphas = [1] * len(self._maps)
        zorders = list(range(0, 10 * len(self._maps), 10))
        levels = [False] * len(self._maps)

        # Set z-order and alpha values for the map
        for i, m in enumerate(self._maps):
            m.zorder = zorders[i]
            m.alpha = alphas[i]
            m.levels = levels[i]

    def add_map(self, amap, zorder=None, alpha=1, levels=False):
        """Adds a map to the CompositeMap.

        Parameters
        ----------
        amap : `~sunpy.map.GenericMap` or subclass
            Map instance to be added
        zorder : `int`
            The index to use when determining where the map should lie along
            the z-axis; maps with higher z-orders appear above maps with lower
            z-orders.
        alpha : `float`
            Opacity at which the map should be displayed. An alpha value of 0
            results in a fully transparent image while an alpha value of 1
            results in a fully opaque image. Values between result in semi-
            transparent images.
        """
        if zorder is None:
            zorder = max([m.zorder for m in self._maps]) + 10

        amap.zorder = zorder
        amap.alpha = alpha
        amap.levels = levels

        self._maps.append(amap)

    def remove_map(self, index):
        """Removes and returns the map with the given index.

        Parameters
        ----------
        index : `int`
            The index of the map in the composite map.

        Returns
        -------
        `sunpy.map.CompositeMap`
            A composite map with the map indexed by 'index' removed from the
            composite map.
        """
        return self._maps.pop(index)

    def list_maps(self):
        """Prints a list of the currently included maps."""
        print([m.__class__ for m in self._maps])

    def get_map(self, index):
        """Returns the map with given index """
        return self._maps[index]

    def get_alpha(self, index=None):
        """
        Returns the alpha-channel value for a layer in the composite image.
        """
        if index is None:
            return [_map.alpha for _map in self._maps]
        else:
            return self._maps[index].alpha

    def get_levels(self, index=None):
        """Returns the list of contour levels for a map within the
        composite.

        Parameters
        ----------
        index : {`int` | None}
            The index of the map in the composite map.

        Returns
        -------
        `list`
            A list of the contour levels of map at index 'index' in the
            composite map.  If index is None, then the contour levels of all
            the maps are returned as a list of lists.
        """
        if index is None:
            return [_map.levels for _map in self._maps]
        else:
            return self._maps[index].levels

    def get_plot_settings(self, index=None):
        """Returns the plot settings for a map within the composite map.

        Parameters
        ----------
        index : {`int` | None}
            The index of the map in the composite map.

        Returns
        -------
        {`dict` | `list`}
            The plot settings of the map(s) in the composite map.  If None
            then the plot settings of all the maps are returned in a list.
        """

        if index is None:
            return [_map.plot_settings for _map in self._maps]
        else:
            return self._maps[index].plot_settings

    def get_zorder(self, index=None):
        """Returns the layering preference (z-order) for a map within the
        composite.

        Parameters
        ----------
        index : {`int` | None}
            The index of the map in the composite map.

        Returns
        -------
        {`float` | `list`}
            The layering order (z-order) of the map(s) in the composite
            map.  If None then the layering order of all the maps is returned in
            a list.
        """
        if index is None:
            return [_map.zorder for _map in self._maps]
        else:
            return self._maps[index].zorder

    def set_alpha(self, index, alpha):
        """Sets the alpha-channel value for a layer in the composite image.

        Parameters
        ----------
        index : `int`
            The index of the map in the composite map.

        alpha : `float`
            A float in the range 0 to 1.  Increasing values of alpha decrease
            the transparency of the layer (0 is complete transparency, 1
            indicates the layer will be completely opaque).

        Returns
        -------
        `~sunpy.map.CompositeMap`
            A composite map with alpha-channel value 'alpha' at layer 'index'.
        """
        if 0 <= alpha <= 1:
            self._maps[index].alpha = alpha
        else:
            raise OutOfRangeAlphaValue("Alpha value must be between 0 and 1.")

    def set_levels(self, index, levels, percent=False):
        """
        Sets the contour levels for a layer in the composite image.

        Parameters
        ----------
        index : `int`
            The index of the map in the composite map.

        levels : array-like
            The contour levels.

        percent : `bool`
            If True, the input 'levels' are interpreted as percentages relative
            to the maximum value of the data in layer 'index' of the composite
            map.  If False, the contour levels are set directly from 'levels'.

        Returns
        -------
        `~sunpy.map.CompositeMap`
            A composite map with contour levels 'levels' at layer 'index'.
        """
        if percent is False:
            self._maps[index].levels = levels
        else:
            self._maps[index].levels = u.Quantity(levels, u.percent)

    def set_plot_settings(self, index, plot_settings):
        """Sets the plot settings for a layer in the composite image.

        Parameters
        ----------
        index : `int`
            The index of the map in the composite map.

        plot_settings : `dict`
            A dictionary of the form

        Returns
        -------
        `~sunpy.map.CompositeMap`
            A composite map with plot settings 'plot_settings' at layer
            'index'.
        """
        self._maps[index].plot_settings = plot_settings

    def set_zorder(self, index, zorder):
        """Set the layering order (z-order) for a map within the
        composite.

        Parameters
        ----------
        index : `int`
            The index of the map in the composite map.

        zorder : `int`
            The layer order.

        Returns
        -------
        `~sunpy.map.CompositeMap`
            A composite map with the map at layer 'index' having layering order
            'zorder'.
        """
        self._maps[index].zorder = zorder

    def draw_limb(self, index=None, axes=None, **kwargs):
        """Draws a circle representing the solar limb.

        Parameters
        ----------
        index : `int`
            Map index to use to plot limb.

        axes : `matplotlib.axes.Axes` or None
            Axes to plot limb on or None to use current axes.

        Returns
        -------
        `matplotlib.axes.Axes`

        Notes
        -----
        Keyword arguments are passed onto `sunpy.map.mapbase.GenericMap.draw_limb`.
        """
        if index is None:
            for i, amap in enumerate(self._maps):
                if hasattr(amap, 'rsun_obs'):
                    index = i
                    break

        index_check = hasattr(self._maps[index], 'rsun_obs')
        if not index_check or index is None:
            raise ValueError("Specified index does not have all"
                             " the required attributes to draw limb.")

        return self._maps[index].draw_limb(axes=axes, **kwargs)

    @u.quantity_input
    def draw_grid(self, index=None, axes=None, grid_spacing: u.deg = 20*u.deg, **kwargs):
        """Draws a grid over the surface of the Sun.

        Parameters
        ----------
        index: int
            Index to determine which map to use to draw grid.
        axes: `~matplotlib.axes.Axes` or None
            Axes to plot limb on or None to use current axes.
        grid_spacing : `float`
            Spacing (in degrees) for longitude and latitude grid.

        Returns
        -------
        `matplotlib.axes.Axes` object

        Notes
        -----
        Keyword arguments are passed onto `sunpy.map.mapbase.GenericMap.draw_grid`.
        """
        needed_attrs = ['rsun_meters', 'dsun', 'heliographic_latitude',
                        'heliographic_longitude']
        if index is None:
            for i, amap in enumerate(self._maps):
                if all([hasattr(amap, k) for k in needed_attrs]):
                    index = i
                    break

        index_check = all([hasattr(self._maps[index], k) for k in needed_attrs])
        if not index_check or index is None:
            raise ValueError("Specified index does not have all"
                             " the required attributes to draw grid.")

        ax = self._maps[index].draw_grid(axes=axes, grid_spacing=grid_spacing, **kwargs)
        return ax

    def plot(self, axes=None, annotate=True,
             title="SunPy Composite Plot", **matplot_args):
        """Plots the composite map object by calling :meth:`~sunpy.map.GenericMap.plot`
        or :meth:`~sunpy.map.GenericMap.draw_contours`.

        By default, each map is plotted as an image.  If a given map has levels
        defined (via :meth:`~sunpy.map.CompositeMap.set_levels`), that map will instead
        be plotted as contours.

        Parameters
        ----------

        axes: `~matplotlib.axes.Axes` or None
            If provided the image will be plotted on the given axes. Else the
            current matplotlib axes will be used.

        annotate : `bool`
            If true, the data is plotted at it's natural scale; with
            title and axis labels.

        title : `str`
            Title of the composite map.

        **matplot_args : `dict`
            Any additional Matplotlib arguments that should be used
            when plotting.

        Returns
        -------
        ret : `list`
            List of axes image or quad contour sets that have been plotted.

        Notes
        -----
        Matplotlib arguments for setting the line width (``linewidths``), line style
        (``linestyles``) or line color (``colors``) will apply only to those maps
        that are plotted as contours. Similar arguments (i.e., ``linewidth``,
        ``lw``, ``color``, ``c``, ``linestyle`` and ``ls``) will also be ignored
        for maps plotted as images.

        If a transformation is required to overlay the maps with the correct
        alignment, the plot limits may need to be manually set because
        Matplotlib autoscaling may not work as intended.
        """

        # If axes are not provided, create a WCSAxes based on the first map
        if not axes:
            axes = wcsaxes_compat.gca_wcs(self._maps[0].wcs)

        if annotate:
            axes.set_xlabel(axis_labels_from_ctype(self._maps[0].coordinate_system[0],
                                                   self._maps[0].spatial_units[0]))
            axes.set_ylabel(axis_labels_from_ctype(self._maps[0].coordinate_system[1],
                                                   self._maps[0].spatial_units[1]))
            axes.set_title(title)

        # Define a list of plotted objects
        ret = []
        # Plot layers of composite map
        for m in self._maps:
            # Parameters for plotting
            params = {
                "alpha": m.alpha,
                "zorder": m.zorder,
            }
            params.update(matplot_args)

            # The request to show a map layer rendered as a contour is indicated by a
            # non False levels property.
            if m.levels is False:
                # Check if any linewidth, color, or linestyle arguments are provided,
                # if so, then delete them from params.
                for item in ['linewidth', 'linewidths', 'lw',
                             'color', 'colors', 'c',
                             'linestyle', 'linestyles', 'ls']:
                    if item in matplot_args:
                        del params[item]

                # We tell GenericMap.plot() that we need to autoalign the map
                if wcsaxes_compat.is_wcsaxes(axes):
                    params['autoalign'] = True

                params['annotate'] = False
                ret.append(m.plot(**params))
            else:
                ret.append(m.draw_contours(m.levels, **params))

                # Set the label of the first line so a legend can be created
                ret[-1].collections[0].set_label(m.name)

        # Adjust axes extents to include all data
        axes.axis('image')

        # Set current image (makes colorbar work)
        plt.sci(ret[0])
        return ret

    @peek_show
    def peek(self, colorbar=True, draw_limb=True, draw_grid=False, **matplot_args):
        """
        Displays a graphical overview of the data in this object for user evaluation.
        For the creation of plots, users should instead use the `~sunpy.map.CompositeMap.plot`
        method and Matplotlib's pyplot framework.

        Parameters
        ----------
        colorbar : `bool` or `int`
            Whether to display a colorbar next to the plot.
            If specified as an integer a colorbar is plotted for that index.

        draw_limb : `bool`
            If true, draws a circle representing the solar limb.

        draw_grid :  `bool`
            If true, draws a grid over the surface of the Sun.

        **matplot_args : dict
            Matplotlib Any additional imshow arguments that should be used
            when plotting.
        """

        # Create a figure and add title and axes
        figure = plt.figure()

        axes = figure.add_subplot(111, projection=self._maps[0])

        ret = self.plot(axes=axes, **matplot_args)

        if not isinstance(colorbar, bool) and isinstance(colorbar, int):
            figure.colorbar(ret[colorbar])
        elif colorbar:
            plt.colorbar()
        if draw_limb:
            self.draw_limb(axes=axes)

        if isinstance(draw_grid, bool):
            if draw_grid:
                self.draw_grid(axes=axes)

        elif isinstance(draw_grid, (int, float)):
            self.draw_grid(axes=axes, grid_spacing=draw_grid)
        else:
            raise TypeError("draw_grid should be bool, int, long or float")

        return figure


class OutOfRangeAlphaValue(ValueError):
    """Exception to raise when an alpha value outside of the range 0-1 is
    requested.
    """
