from qgis.utils import iface
from qgis.core import QgsProcessingFeatureSourceDefinition, QgsProject, QgsVectorLayer

unclipped_layer = QgsProject.instance().mapLayersByName("area5_for_script")[-1]
# coast_layer = QgsProject.instance().mapLayersByName("coastlines_for_script")[-1]
scale = 190000
# stroke_width = 1.5
stroke_width = 0.5
thick_stroke_width = stroke_width / 1000 / 2 * scale
thin_stroke_width = stroke_width / 1000 / 2 * scale / 2
buffer_val = scale * stroke_width
# thin_elevation = 160
# thick_elevation = 480
# thin_elevation = 200
# thick_elevation = 600

expr1 = '  "elevation" % {} = 0'.format(thick_elevation)
expr2 = '   "elevation" % {} = 0 AND  "elevation" % {} <> 0 '.format(thin_elevation, thick_elevation)
expr1 = '  "elevation" = 460'
expr2 = '  "elevation" IN (20, 240, 680, 1000)'

raster_layer = QgsProject.instance().mapLayersByName("area5_rectangle1")[-1]
extent = raster_layer.extent()
extent_buffered = extent.buffered(thick_stroke_width * 2)

stroke_geom_layer = QgsVectorLayer("Polygon?crs=epsg:2193", "stroke_geom_layer", "memory")
stroke_geom_layer_pr = stroke_geom_layer.dataProvider()
stroke_geom_layer_pr.addAttributes([QgsField("fid", QVariant.Int)])
stroke_geom_layer.updateFields()

first_clip = processing.run(
    "native:extractbyextent", {"INPUT": unclipped_layer, "EXTENT": extent_buffered, "CLIP": True, "OUTPUT": "memory:"}
)["OUTPUT"]

QgsProject.instance().addMapLayer(first_clip)

print("clipped")

first_clip.selectByExpression(expr1, QgsVectorLayer.SetSelection)

params_thickbuff = {
    "INPUT": QgsProcessingFeatureSourceDefinition(first_clip.id(), True),
    "DISTANCE": thick_stroke_width,
    "SEGMENTS": 8,
    "END_CAP_STYLE": 0,
    "JOIN_STYLE": 0,
    "MITER_LIMIT": 3.5,
    "DISSOLVE": False,
    "OUTPUT": "memory:",
}

buffer = processing.run("native:buffer", params_thickbuff)["OUTPUT"]
print("buffered")

clipped_layer = processing.run(
    "native:extractbyextent", {"INPUT": buffer, "EXTENT": extent, "CLIP": True, "OUTPUT": "memory:"}
)["OUTPUT"]
print("clipped")

for feature in clipped_layer.getFeatures():
    # add a feature
    fet = QgsFeature()
    fet.setGeometry(feature.geometry())
    fet.setAttributes([feature["fid"]])
    stroke_geom_layer_pr.addFeatures([fet])

stroke_geom_layer.updateExtents()

first_clip.selectByExpression(expr2, QgsVectorLayer.SetSelection)

params_thinbuff = {
    "INPUT": QgsProcessingFeatureSourceDefinition(first_clip.id(), True),
    "DISTANCE": thin_stroke_width,
    "SEGMENTS": 8,
    "END_CAP_STYLE": 0,
    "JOIN_STYLE": 0,
    "MITER_LIMIT": 3.5,
    "DISSOLVE": False,
    "OUTPUT": "memory:",
}

buffer_not_100 = processing.run("native:buffer", params_thinbuff)["OUTPUT"]
print("second buffered")

second_clipped_layer = processing.run(
    "native:extractbyextent", {"INPUT": buffer_not_100, "EXTENT": extent, "CLIP": True, "OUTPUT": "memory:"}
)["OUTPUT"]
print("second clipped")

for feature in second_clipped_layer.getFeatures():
    # add a feature
    fet = QgsFeature()
    fet.setGeometry(feature.geometry())
    fet.setAttributes([feature["fid"]])
    stroke_geom_layer_pr.addFeatures([fet])

stroke_geom_layer.updateExtents()

# Convert Polygon to Lines

# first_coast_clip = processing.run(
#     "native:extractbyextent", {"INPUT": coast_layer, "EXTENT": extent_buffered, "CLIP": True, "OUTPUT": "memory:"}
# )["OUTPUT"]
# print("clipped")

# params_coastlines = {"INPUT": first_coast_clip, "OUTPUT": "memory:"}

# coastlines = processing.run("native:polygonstolines", params_coastlines)["OUTPUT"]

# params_coastbuff = {
#     "INPUT": coastlines,
#     "DISTANCE": thin_stroke_width,
#     "SEGMENTS": 8,
#     "END_CAP_STYLE": 0,
#     "JOIN_STYLE": 0,
#     "MITER_LIMIT": 3.5,
#     "DISSOLVE": False,
#     "OUTPUT": "memory:",
# }

# buffered_coast = processing.run("native:buffer", params_coastbuff)["OUTPUT"]
# print("buffered coast")

# clipped_coast = processing.run(
#     "native:extractbyextent", {"INPUT": buffered_coast, "EXTENT": extent, "CLIP": True, "OUTPUT": "memory:"}
# )["OUTPUT"]
# print("clipped coast")

# for feature in clipped_coast.getFeatures():
#     # add a feature
#     fet = QgsFeature()
#     fet.setGeometry(feature.geometry())
#     fet.setAttributes([feature["fid"]])
#     stroke_geom_layer_pr.addFeatures([fet])

# stroke_geom_layer.updateExtents()

stroke_geom_layer.renderer().setSymbol(QgsFillSymbol.createSimple({"color": "#dcdcdc", "style_border": "no"}))

QgsProject.instance().addMapLayer(stroke_geom_layer)
QgsProject.instance().removeMapLayer(first_clip)


# def alglist(search_term: str = False):
#     s = ""
#     for alg in QgsApplication.processingRegistry().algorithms():
#         if search_term:
#             if search_term.lower() in alg.displayName().lower():
#                 s += "{}->{}\n".format(alg.id(), alg.displayName())
#         else:
#             s += "{}->{}\n".format(alg.id(), alg.displayName())
#             # l = alg.displayName().ljust(50, "-")
#             # r = alg.id()
#             # s += '{}--->{}\n'.format(l, r)
#     print(s)

# alglist("polygons")

# processing.run("native:polygonstolines"
