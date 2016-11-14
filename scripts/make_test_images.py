#!/usr/bin/env python

from cpc.geoplot.geomap import Geomap, get_supported_domains, get_supported_projections


for proj in get_supported_projections():
    for dom in get_supported_domains():
        try:
            Geomap(projection=proj, domain=dom).save('empty-Geomap-{}-{}.png'.format(proj, dom),
						     dpi=100)
        except Exception as e:
            pass
