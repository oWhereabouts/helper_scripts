from qgis.utils import iface
from qgis.core import QgsProcessingFeatureSourceDefinition, QgsProject, QgsVectorLayer

unclipped_layer = QgsProject.instance().mapLayersByName("contours_for_script")[-1]
coast_layer = QgsProject.instance().mapLayersByName("coastlines_for_script")[-1]
scale = 55000
stroke_width = 1.5
thick_stroke_width = stroke_width / 1000 / 2 * scale
thin_stroke_width = stroke_width / 1000 / 2 * scale / 2
buffer_val = scale * stroke_width

raster_layer = QgsProject.instance().mapLayersByName("rata_rectangle1")[-1]
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

expr = '  "elevation" % 160 = 0 '
first_clip.selectByExpression(expr, QgsVectorLayer.SetSelection)

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

expr = '   "elevation" % 80 = 0 AND  "elevation" % 160 <> 0 '
first_clip.selectByExpression(expr, QgsVectorLayer.SetSelection)

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

first_coast_clip = processing.run(
    "native:extractbyextent", {"INPUT": coast_layer, "EXTENT": extent_buffered, "CLIP": True, "OUTPUT": "memory:"}
)["OUTPUT"]
print("clipped")

params_coastlines = {"INPUT": first_coast_clip, "OUTPUT": "memory:"}

coastlines = processing.run("native:polygonstolines", params_coastlines)["OUTPUT"]

params_coastbuff = {
    "INPUT": coastlines,
    "DISTANCE": thin_stroke_width,
    "SEGMENTS": 8,
    "END_CAP_STYLE": 0,
    "JOIN_STYLE": 0,
    "MITER_LIMIT": 3.5,
    "DISSOLVE": False,
    "OUTPUT": "memory:",
}

buffered_coast = processing.run("native:buffer", params_coastbuff)["OUTPUT"]
print("buffered coast")

clipped_coast = processing.run(
    "native:extractbyextent", {"INPUT": buffered_coast, "EXTENT": extent, "CLIP": True, "OUTPUT": "memory:"}
)["OUTPUT"]
print("clipped coast")

for feature in clipped_coast.getFeatures():
    # add a feature
    fet = QgsFeature()
    fet.setGeometry(feature.geometry())
    fet.setAttributes([feature["fid"]])
    stroke_geom_layer_pr.addFeatures([fet])

stroke_geom_layer.updateExtents()

# stroke_geom_layer.renderer().setSymbol(
#         QgsFillSymbol.createSimple({"color": "0,0,0,0", "color_border": "0,0,0,100", "width_border": "0.46"})
#     )
#     symbol = QgsFillSymbol.createSimple({'color_border': 'blue', 'style': 'no', 'style_border': 'dash'})
#                 layer.renderer().setSymbol(symbol)
#                 layer.triggerRepaint()

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
