from qgis.core import QgsProject, QgsFeature, QgsFeatureRequest, QgsVectorLayer, QgsWkbTypes

split = QgsProject.instance().mapLayersByName("Split")[-1]

tracks_3d = QgsProject.instance().mapLayersByName("tracks_3d")[-1]

idx = tracks_3d.fields().indexFromName('slope1')


wkbtype = QgsWkbTypes.displayString(int(split.wkbType()))
output_layer = QgsVectorLayer(
    "{}?crs=epsg:2193&index=yes".format(wkbtype), "split_new_slope", "memory",
)
# copy fields
attributeList = tracks_3d.dataProvider().fields().toList()
output_layer.dataProvider().addAttributes(attributeList)
output_layer.updateFields()

for line in split.getFeatures():
    # poly_geom = poly.geometry()
    # request = QgsFeatureRequest().setFilterRect(poly_geom.boundingBox()).setFlags(QgsFeatureRequest.ExactIntersect)
    boundingBox = line.geometry().boundingBox().buffered(10)
    request = QgsFeatureRequest().setFilterRect(boundingBox)
    slopes = 0
    feat_count = 0
    first = True
    for feature in tracks_3d.getFeatures(request):
        if feature.geometry().contains(line.geometry()):
            slopes += feature.attributes()[idx]
            feat_count += 1
            if first:
                new_attributes = feature.attributes()
                first = False

    if feat_count > 0:
        new_slope = slopes/feat_count
    else:
        slope = 0
    new_feat = QgsFeature()
    # new_attributes = line.attributes()
    # new_attributes.append(new_slope)
    new_attributes[idx] = new_slope
    new_feat.setAttributes(new_attributes)
    new_feat.setGeometry(line.geometry())
    output_layer.dataProvider().addFeatures([new_feat])

output_layer.updateExtents()
QgsProject.instance().addMapLayer(output_layer)
