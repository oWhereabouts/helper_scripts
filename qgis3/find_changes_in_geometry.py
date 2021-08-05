from qgis.utils import iface
from qgis.core import (
    QgsFeatureRequest,
    QgsProcessingFeatureSourceDefinition,
    QgsProject, QgsVectorLayer,
    QgsWkbTypes)

layer_1 = QgsProject.instance().mapLayersByName("hospital_matched_polygons_v3 matched_polygons")[-1]
layer_2 = QgsProject.instance().mapLayersByName("hospital_matched_polygons_v2 matched_polygons")[-1]

layer_1_unique_id_name = 'fid'
layer_2_unique_id_name = 'fid'

wkbtype = QgsWkbTypes.displayString(int(layer_1.wkbType()))
crs = layer_1.sourceCrs().authid()
output_layer = QgsVectorLayer("{}?crs={}&index=yes".format(wkbtype, crs), "output_layer", "memory")
# copy fields
attributeList = layer_1.dataProvider().fields().toList()
output_layer.dataProvider().addAttributes(attributeList)
output_layer.updateFields()

for feature1 in layer_1.getFeatures():
    feature1_unique_id = feature1[layer_1_unique_id_name]

    request = (
        QgsFeatureRequest().setFilterExpression("{} = {}".format(layer_2_unique_id_name, feature1_unique_id))
    ) 
    for feature2 in layer_2.getFeatures(request):
        area1 = round(feature1.geometry().area())
        area2 = round(feature2.geometry().area())
        if not feature1.geometry().equals(feature2.geometry()):
            output_layer.dataProvider().addFeature(feature1)
            
output_layer.updateExtents()
QgsProject.instance().addMapLayer(output_layer)
