
from qgis.utils import iface
from qgis.core import QgsWkbTypes
layer = iface.activeLayer()
print(QgsWkbTypes.displayString(int(layer.wkbType())))

for feature in layer.getFeatures():
    geom = feature.geometry()
    print(geom.isMultipart())
    print(len(geom.asGeometryCollection()))
    if len(geom.asGeometryCollection()) > 1:
        print("geom collect > 1")