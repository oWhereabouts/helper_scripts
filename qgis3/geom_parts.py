from qgis.utils import iface
from qgis.core import QgsFeature, QgsGeometry, QgsProject, QgsVectorLayer, QgsWkbTypes

input_layer = iface.activeLayer()

wkbtype = QgsWkbTypes.displayString(int(input_layer.wkbType()))
crs = input_layer.sourceCrs().authid()
layer = QgsVectorLayer("{}?crs={}&index=yes".format(wkbtype, crs), "single_parts", "memory")
# copy fields
attributeList = input_layer.dataProvider().fields().toList()
layer.dataProvider().addAttributes(attributeList)
layer.updateFields()

for feature in input_layer.selectedFeatures():
    # print(feature.attributes())
    # geom.asGeometryCollection()
    # for part in feature.geometry().parts():
    #     # print(QgsWkbTypes.displayString(int(part.wkbType())))
    #     print(part)
    geom = feature.geometry()
    for part in geom.parts():
        # for part in geom.asGeometryCollection():
        # print("blah")
        # print(part.area())
        new_feat = QgsFeature()
        new_feat.setGeometry(QgsGeometry(part))
        new_feat.setAttributes(feature.attributes())
        layer.dataProvider().addFeature(new_feat)

print(layer.featureCount())
layer.updateExtents()
QgsProject.instance().addMapLayer(layer)
