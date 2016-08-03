"""
Defines a Map object. Maps contain a basemap, title, colorbar, etc. Fields can be plotted on a Map.
"""

# Built-ins
import reprlib
from pkg_resources import resource_filename

# Third-party
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# This package
from cpc.geoplot import MapError, FieldError

# Create reprlib
r = reprlib.Repr()
r.maxlist = 4  # max elements displayed for lists
r.maxstring = 50  # max characters displayed for strings


def get_supported_projections():
    """
    Get a list of supported projections for creating a Map

    ### Returns

    - *list of strings*: list of supported projections
    """
    return ['equal-area', 'lcc', 'mercator']


def get_supported_domains():
    """
    Get a list of supported domains for creating a Map

    ### Returns

    - *list of strings*: list of supported projections
    """
    return ['CONUS', 'global', 'NA', 'US']


class Map:
    """
    Map object
    """

    def __init__(self,
                 projection='equal-area', domain='US',
                 cbar=True, cbar_ends='triangular', cbar_type='normal',
                 cbar_color_spacing='natural', cbar_label='', cbar_tick_labels=None,
                 tercile_type=None, title=''):
        # ------------------------------------------------------------------------------------------
        # Attributes
        #
        # Basemap
        self.projection = projection
        self.domain = domain
        # Colorbar
        self.cbar = cbar
        self.cbar_ends = cbar_ends
        self.cbar_type = cbar_type
        self.cbar_color_spacing = cbar_color_spacing
        self.cbar_label = cbar_label
        self.cbar_tick_labels = cbar_tick_labels
        # Other
        self.tercile_type = tercile_type
        self.title = title

        # ------------------------------------------------------------------------------------------
        # Create Basemap
        #
        # Create the figure and axes to store the Basemap
        fig, ax = plt.subplots()
        # Mercator projection
        if self.projection == 'mercator':  # mercator projection
            if self.domain == 'US':  # U.S.
                lat_range = (25, 72)
                lon_range = (190, 300)
                latlon_line_interval = 10
            elif self.domain == 'NA':  # North America
                lat_range = (14, 72)
                lon_range = (190, 300)
                latlon_line_interval = 10
            elif self.domain == 'CONUS':  # CONUS
                lat_range = (24, 50)
                lon_range = (230, 295)
                latlon_line_interval = 5
            elif self.domain == 'global':  # global
                lat_range = (-90, 90)
                lon_range = (0, 360)
                latlon_line_interval = 30
            elif type(self.domain) is tuple and len(self.domain) == 4:  # custom box
                lat_range = self.domain[0:2]
                lon_range = self.domain[2:4]
                latlon_line_interval = 10
            else:
                raise MapError(
                    'domain must be either one of {}, or be a tuple of 4 numbers defining a custom '
                    'box (lat1, lat2, lon1, lon2)'.format(['US', 'NA', 'CONUS', 'global'])
                )
            basemap = Basemap(
                llcrnrlon=lon_range[0],
                llcrnrlat=lat_range[0],
                urcrnrlon=lon_range[1],
                urcrnrlat=lat_range[1],
                projection='mill',
                ax=ax,
                resolution='l'
            )
            basemap.drawcoastlines(linewidth=1)
            parallels = basemap.drawparallels(
                np.arange(lat_range[0], lat_range[1] + 1, latlon_line_interval),
                labels=[1, 1, 0, 0], fontsize=9
            )
            parallels[list(sorted(parallels.keys()))[0]].remove()
            basemap.drawmeridians(np.arange(lon_range[0], lon_range[1] + 1, latlon_line_interval),
                                  labels=[0, 0, 0, 1], fontsize=9)
            basemap.drawmapboundary(fill_color='#DDDDDD')
            basemap.drawcountries()
        elif self.projection in ['lcc', 'equal-area']:  # lcc or equal-area projection
            # Set the name of the projection for Basemap
            if self.projection == 'lcc':
                basemap_projection = 'lcc'
            elif self.projection == 'equal-area':
                basemap_projection = 'laea'

            if self.domain == 'US':
                basemap = Basemap(width=8000000, height=6600000, lat_0=53., lon_0=260.,
                                  projection=basemap_projection, ax=ax, resolution='l')
            elif self.domain == 'NA':
                basemap = Basemap(width=8000000, height=7500000, lat_0=48., lon_0=260.,
                                  projection=basemap_projection, ax=ax, resolution='l')
            elif self.domain == 'CONUS':
                basemap = Basemap(width=5000000, height=3200000, lat_0=39., lon_0=262.,
                                  projection=basemap_projection, ax=ax, resolution='l')
            else:
                raise MapError('When projection is set to lcc or equal-area, domain must be US, '
                               'NA, or CONUS')
            # Draw political boundaries
            basemap.drawcountries(linewidth=0.5)
            basemap.drawcoastlines(0.5)
            if self.domain in ['US', 'CONUS', 'NA']:
                basemap.readshapefile(resource_filename('cpc.geoplot', 'data/states'),
                                      name='states', drawbounds=True)
                for state in basemap.states:
                    x, y = zip(*state)
                    basemap.plot(x, y, marker=None, color='black', linewidth=0.75)
        else:
            raise MapError('projection {} not supported, must be one of {}'.format(
                self.projection, get_supported_projections()))
        # Save basemap as an attribute
        self.basemap = basemap

    def save(self, file, dpi=600):
        plt.savefig(file, dpi=dpi, bbox_inches='tight')

    def show(self):
        plt.show()

    def plot(self, field):
        # Get grid of lats and lons
        lons, lats = np.meshgrid(field.geogrid.lons, field.geogrid.lats)
        # Get data from field
        data = field.data
        # Set some plotting options based on field attributes
        contour_colors = None if field.contour_colors == 'auto' else field.contour_colors
        fill_colors = field.fill_colors
        fill_alpha = field.fill_alpha
        # Reshape data to 2-d (if currently 1-d)
        if data.ndim == 1:
            data = data.reshape((field.geogrid.num_y, field.geogrid.num_x))
        elif data.ndim == 2:
            pass
        else:
            raise FieldError('Field data must be 1- or 2-dimensional')
        # ------------------------------------------------------------------------------------------
        # Plot field on Map
        #
        # Plot filled contours (if necessary)
        if fill_colors:
            contours = self.basemap.contourf(lons, lats, data, latlon=True)
        else:
            contours = self.basemap.contour(lons, lats, data, latlon=True, colors=contour_colors)

    def __repr__(self):
        details = ''
        for key, val in sorted(vars(self).items()):
            details += eval(r.repr('- {}: {}\n'.format(key, val)))
        return 'Map:\n{}'.format(details)


if __name__ == '__main__':
    import numpy as np
    from cpc.geogrids import GeoGrid
    from cpc.geoplot import Map
    from cpc.geoplot import Field

    geogrid = GeoGrid('1deg-global')
    map = Map()
    data = np.fromfile('/Users/mike/500hgt_05d_20120515.bin', dtype='float32')
    field = Field(data, geogrid)
    map.plot(field)
    map.save('test.png')
