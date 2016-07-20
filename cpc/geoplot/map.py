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
        if self.projection == 'mercator':
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
            basemap.drawparallels(np.arange(lat_range[0], lat_range[1] + 1, latlon_line_interval),
                                  labels=[1, 1, 0, 0], fontsize=9)
            basemap.drawmeridians(np.arange(lon_range[0], lon_range[1] + 1, latlon_line_interval),
                                  labels=[0, 0, 0, 1], fontsize=9)
            basemap.drawmapboundary(fill_color='#DDDDDD')
            basemap.drawcountries()
        elif self.projection in ['lcc', 'equal-area']:
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
                basemap.readshapefile(resource_filename('data_utils', 'lib/states'),
                                      name='states', drawbounds=True)
                for state in basemap.states:
                    x, y = zip(*state)
                    basemap.plot(x, y, marker=None, color='black', linewidth=0.75)

    def plot(self, file=None, dpi=600):
        if file is None:
            plt.show()
        else:
            plt.savefig(file, dpi=dpi, bbox_inches='tight')

    def __repr__(self):
        details = ''
        for key, val in sorted(vars(self).items()):
            details += eval(r.repr('- {}: {}\n'.format(key, val)))
        return 'Map:\n{}'.format(details)


if __name__ == '__main__':
    from cpc.geoplot import Map
    map = Map()
    print(map)
    map.plot()
