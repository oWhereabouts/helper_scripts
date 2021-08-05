from qgis.utils import iface
from qgis.core import QgsWkbTypes
lyr = iface.activeLayer()

# lyr = QgsProject.instance().mapLayersByName('Soils_091201')[0]
fieldname1 = 't50_fid'
fieldname2 = 'fid'
data = [(f[fieldname1], f[fieldname2]) for f in lyr.getFeatures()]
print(data)
