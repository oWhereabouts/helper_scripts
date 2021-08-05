from qgis.utils import iface
from qgis.core import (
    QgsProject
)

input_layer = iface.activeLayer()
rivers = QgsProject.instance().mapLayersByName("arapuni_river")[-1]

for layer_name in ("test_polygon", "test_average_line"):
    layers = QgsProject.instance().mapLayersByName(layer_name)
    for layer in layers:
        QgsProject.instance().removeMapLayer(layer)

QgsProject.instance().addMapLayer(input_layer)
