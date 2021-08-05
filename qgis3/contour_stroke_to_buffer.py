# alglist("buffer")
# processing.run("qgis:singlesidedbuffer"
# alglist("multipart")
# alglist("polygon")
# processing.run("qgis:singlesidedbuffer"

from qgis.utils import iface
from qgis.core import QgsProcessingFeatureSourceDefinition, QgsProject, QgsVectorLayer


unclipped_layer = iface.activeLayer()
scale = 55000
stroke_width = 1.0 / 1000
buffer_val = scale * stroke_width

raster_layer = QgsProject.instance().mapLayersByName("rata_rectangle1")[-1]
extent = raster_layer.extent()
extent_buffered = extent.buffered(buffer_val * 2)

params_polygons = {
    "INPUT": unclipped_layer,
    "OUTPUT": "memory:",
}

# params_single = {
#     "INPUT": unclipped_layer,
#     "OUTPUT": "memory:",
# }

# single = processing.run("native:multiparttosingleparts", params_single)["OUTPUT"]
# # QgsProject.instance().addMapLayer(layer)
# print("singleparts")

params_polygons = {
    "INPUT": single,
    "OUTPUT": "memory:",
}

polygons = processing.run("qgis:linestopolygons", params_polygons)["OUTPUT"]
print("polygons")
print(polygons.isValid())
print(polygons.featureCount())
QgsProject.instance().addMapLayer(polygons)
layer = polygons
# clipped = processing.run(
#     "native:extractbyextent", {"INPUT": polygons, "EXTENT": extent_buffered, "CLIP": True, "OUTPUT": "memory:"}
# )["OUTPUT"]
# print("clipped")

# params_single = {
#     "INPUT": clipped,
#     "OUTPUT": "memory:",
# }

# layer = processing.run("native:multiparttosingleparts", params_single)["OUTPUT"]
# QgsProject.instance().addMapLayer(layer)
# print("singleparts")
expr = '  "elevation" % 100 = 0 '
layer.selectByExpression(expr, QgsVectorLayer.SetSelection)

# params = {
#     "INPUT": QgsProcessingFeatureSourceDefinition(layer.id(), True),
#     "DISTANCE": buffer_val,
#     "SIDE": 0,
#     "JOIN_STYLE": 2,
#     "MITER_LIMIT": 2,
#     "SEGMENTS": 8,
#     "OUTPUT": "memory:",
# }

# inner_buffer = processing.run("qgis:singlesidedbuffer", params)["OUTPUT"]
params_innerbuff = {
    "INPUT": layer,
    "DISTANCE": buffer_val * -1,
    "SEGMENTS": 8,
    "END_CAP_STYLE": 0,
    "JOIN_STYLE": 1,
    "MITER_LIMIT": 3.5,
    "DISSOLVE": True,
    "OUTPUT": "memory:",
}

inner_buffer = processing.run(
    "native:buffer", buffer_params(QgsProcessingFeatureSourceDefinition(layer.id(), True), buffer_val * -1, False)
)["OUTPUT"]
print("inner buffer")

stroke_geom_layer = QgsVectorLayer("Polygon?crs=epsg:2193", "stroke_geom_layer", "memory")
stroke_geom_layer_pr = stroke_geom_layer.dataProvider()
stroke_geom_layer_pr.addAttributes([QgsField("fid", QVariant.Int)])
stroke_geom_layer.updateFields()

# count = 0
for feature in layer.selectedFeatures():
    # count += 1
    geom = feature.geometry()
    # outer_buff =
    feat_id = feature["fid"]
    expr = ' "fid" = {}'.format(feat_id)
    inner_buffer.selectByExpression(expr, QgsVectorLayer.SetSelection)
    inner_geom = False
    for feature in inner_buffer.selectedFeatures():
        if feature.geometry().isNull():
            inner_geom = False
        else:
            inner_geom = feature.geometry()
    if inner_geom:
        stroke_geom = geom.difference(inner_geom)
    else:
        stroke_geom = geom

    # add a feature
    fet = QgsFeature()
    fet.setGeometry(stroke_geom)
    fet.setAttributes([feat_id])
    stroke_geom_layer_pr.addFeatures([fet])

stroke_geom_layer.updateExtents()
# QgsProject.instance().addMapLayer(stroke_geom_layer)
# print(count)
print("difference_buffers")
# dissolved_layer = processing.run("native:dissolve", {"INPUT": inner_buffer, "FIELD": [], "OUTPUT": "memory:"})["OUTPUT"]
# print("dissolved")
clipped_layer = processing.run(
    "native:extractbyextent", {"INPUT": stroke_geom_layer, "EXTENT": extent, "CLIP": True, "OUTPUT": "memory:"}
)["OUTPUT"]
print("clipped")
QgsProject.instance().addMapLayer(clipped_layer)
QgsProject.instance().removeMapLayer(layer)
