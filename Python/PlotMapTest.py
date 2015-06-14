from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
import pylab
 
#map = Basemap(projection='merc', lat_0 = 18.4239, lon_0 = -33.9253,
#    resolution = 'h', area_thresh = 0.1,
#    llcrnrlon=-33.9, llcrnrlat=-18.4,
 #   urcrnrlon=-34, urcrnrlat=-18.5)
map = Basemap(projection='merc',
    resolution = 'h', area_thresh = 0.1,
    llcrnrlon=18.203659, llcrnrlat=-34.180906,
    urcrnrlon=18.746109, urcrnrlat=-33.841677)
 
map.drawcoastlines()
map.drawcountries()
map.drawrivers()
map.drawstates()
map.fillcontinents(color = 'coral')
map.drawmapboundary()
lon = -33.924868
lat = 18.424055
x,y = map(lon, lat)
map.plot(x, y, 'bo', markersize=24)
#pylab.savefig('foo.png', bbox_inches='tight')
print("Done")
plt.show()
