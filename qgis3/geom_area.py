from qgis.utils import iface


layer = iface.activeLayer()

for feature in layer.selectedFeatures():
    print(feature.geometry().area())
