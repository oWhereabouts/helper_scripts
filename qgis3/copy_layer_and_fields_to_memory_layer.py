from qgis.utils import iface
from qgis.core import (
    QgsFeature,
    QgsProject,
    QgsVectorLayer,
    QgsWkbTypes
)
input_layer = iface.activeLayer()



################
# copy a layer and its attributes to a memory layer


self.input_layer = input_layer
self.wkbtype = QgsWkbTypes.displayString(int(self.input_layer.wkbType()))

# crs = topo50_building_poly.sourceCrs()
# lyr.crs().authid() != "EPSG:2193"

self.output_layer = QgsVectorLayer(
    "{}?crs=epsg:2193&index=yes".format(self.wkbtype), "building_outlines_non_res_simplified", "memory",
)
# copy fields
attributeList = self.input_layer.dataProvider().fields().toList()
self.output_layer.dataProvider().addAttributes(attributeList)
self.output_layer.updateFields()

# then later use
new_poly.setAttributes(feature.attributes())
new_poly = QgsFeature()

def copy_layer(input_layer):
    """Copy a layer."""
    wkbtype = QgsWkbTypes.displayString(int(input_layer.wkbType()))
    crs = input_layer.sourceCrs().authid()
    layer = QgsVectorLayer("{}?crs={}&index=yes".format(wkbtype, crs), "building_outlines", "memory")
    # copy fields
    attributeList = input_layer.dataProvider().fields().toList()
    layer.dataProvider().addAttributes(attributeList)
    layer.updateFields()

    new_feat = QgsFeature()
    for input_feat in input_layer.getFeatures():
        new_feat.setGeometry(input_feat.geometry())
        new_feat.setAttributes(input_feat.attributes())
        layer.dataProvider().addFeature(new_feat)

        # or 
        # layer.dataProvider().addFeature(input_feat)
    return layer

output_layer.updateExtents()
QgsProject.instance().addMapLayer(output_layer)
