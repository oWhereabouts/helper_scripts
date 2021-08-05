from qgis.core import QgsFeature, QgsProject, QgsVectorDataProvider, QgsVectorLayer, QgsWkbTypes
from qgis.utils import iface


input_layer = iface.activeLayer()

# make vector layer in memory with the same geom type
wkbtype = QgsWkbTypes.displayString(int(input_layer.wkbType()))
crs = input_layer.sourceCrs().authid()
output_layer = QgsVectorLayer(
    "{}?crs=epsg:2193&index=yes".format(wkbtype), "incremented_layer", "memory",
)

# copy fields
attributeList = input_layer.dataProvider().fields().toList()
output_layer.dataProvider().addAttributes(attributeList)
output_layer.updateFields()

for feature in input_layer.getFeatures():
    rect = feature.geometry().boundingBox()
    xmin = rect.xMinimum()
    xmax = rect.xMaximum()
    ymin = rect.yMinimum()
    ymax = rect.yMaximum()
    x_list = sorted([xmin, xmax])
    y_list = sorted([ymin, ymax])
    xhalf = x_list[0] + ((x_list[1] - x_list[0]) * 0.5)
    yhalf = y_list[0] + ((y_list[1] - y_list[0]) * 0.5)
    # print("xmin {}".format(xmin))
    # print("xmax {}".format(xmax))
    # print("xhalf {}".format(xhalf))

    # geom1 = QgsGeometry.fromRect(QgsRectangle(xmin, ymin, xmax, ymax))

    geom1 = QgsGeometry.fromRect(QgsRectangle(xmin, ymin, xhalf, yhalf))
    geom2 = QgsGeometry.fromRect(QgsRectangle(xhalf, ymin, xmax, yhalf))
    geom3 = QgsGeometry.fromRect(QgsRectangle(xmin, yhalf, xhalf, ymax))
    geom4 = QgsGeometry.fromRect(QgsRectangle(xhalf, yhalf, xmax, ymax))
    # (geom1, geom2, geom3, geom4)

    for geom in (geom1, geom2, geom3, geom4):
        new_feat = QgsFeature()
        new_feat.setAttributes(feature.attributes())
        new_feat.setGeometry(geom)
        output_layer.dataProvider().addFeatures([new_feat])

output_layer.updateExtents()

# add layer to the canvas
QgsProject.instance().addMapLayer(output_layer)

