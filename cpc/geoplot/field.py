"""
Defines a Field object. Fields can be plotted on a Map, and store certain properties,
such as contour levels, contour colors,  contour labels, etc.
"""


class Field:
    """
    Field object
    """
    def __init__(self, data, geogrid, levels='auto', contour_colors='auto', contour_labels=False,
                 smoothing_factor=0, fill_colors='auto', fill_alpha=1):
        # ------------------------------------------------------------------------------------------
        # Attributes
        #
        # Positional args
        self.data = data
        self.geogrid = geogrid
        # Kwargs
        self.levels = levels
        self.contour_colors = contour_colors
        self.contour_labels = contour_labels
        self.smoothing_factor = smoothing_factor
        self.fill_colors = fill_colors
        self.fill_alpha = fill_alpha


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
