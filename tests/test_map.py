# Built-ins
from pkg_resources import resource_filename
from tempfile import NamedTemporaryFile
import os

# Third-party
from img_percent_diff import img_percent_diff

# This package
from cpc.geoplot import Map
from cpc.geoplot.map import get_supported_projections


def test_create_empty_Map():
    """Create empty Map images and compare them to pregenerated Mmap images"""
    # Loop over supported projections
    for proj in get_supported_projections():
        # Create a Map object with the given projection
        map = Map(projection=proj)
        # Plot the Map to a file and compare it to a pregenerated Map
        with NamedTemporaryFile(suffix='.png', dir='.') as temp_file:
            test_img = temp_file.name
            map.save(test_img, dpi=100)
            # Compare the resulting Map plot to a pregenerated plot
            real_img = resource_filename('cpc.geoplot', 'images/empty-Basemap-{}.png'.format(proj))
            assert img_percent_diff(test_img, real_img) < 0.001
