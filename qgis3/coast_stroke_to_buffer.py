from qgis.utils import iface
from qgis.core import QgsProcessingFeatureSourceDefinition, QgsProject, QgsVectorLayer


coast = iface.activeLayer()
scale = 55000
stroke_width = 2.0 / 1000
buffer_val = scale * stroke_width

raster_layer = QgsProject.instance().mapLayersByName("rata_rectangle1")[-1]
extent = raster_layer.extent()
extent_buffered = extent.buffered(buffer_val * 2)

stroke_geom_layer = QgsVectorLayer("Polygon?crs=epsg:2193", "stroke_geom_layer", "memory")
stroke_geom_layer_pr = stroke_geom_layer.dataProvider()
stroke_geom_layer_pr.addAttributes([QgsField("fid", QVariant.Int)])
stroke_geom_layer.updateFields()

# count = 0
for feature in coast.getFeatures():
    # count += 1
    geom = feature.geometry()
    # outer_buff =
    feat_id = feature["fid"]
    # expr = ' "fid" = {}'.format(feat_id)
    # inner_buffer.selectByExpression(expr, QgsVectorLayer.SetSelection)
    # inner_geom = False
    # for feature in inner_buffer.selectedFeatures():
    #     if feature.geometry().isNull():
    #         inner_geom = False
    #     else:
    #         inner_geom = feature.geometry()
    # if inner_geom:
    #     stroke_geom = geom.difference(inner_geom)
    # else:
    #     stroke_geom = geom
    innergeombuff = geom.buffer(buffer_val * -1, 8, 0, 1, 3.5)
    stroke_geom = geom.difference(innergeombuff)

    # add a feature
    fet = QgsFeature()
    fet.setGeometry(stroke_geom)
    fet.setAttributes([feat_id])
    stroke_geom_layer_pr.addFeatures([fet])

stroke_geom_layer.updateExtents()
print("difference_buffers")

clipped_layer = processing.run(
    "native:extractbyextent", {"INPUT": stroke_geom_layer, "EXTENT": extent, "CLIP": True, "OUTPUT": "memory:"}
)["OUTPUT"]
print("clipped")
QgsProject.instance().addMapLayer(clipped_layer)
