from qgis.core import QgsProcessingFeatureSourceDefinition, QgsProject, QgsVectorLayer

contours = QgsProject.instance().mapLayersByName("taupiri_contours")[-1]
river_poly = QgsProject.instance().mapLayersByName("taupiri_river")[-1]
raster_layer = QgsProject.instance().mapLayersByName("taupiri_rectangle1")[-1]

scale = 80000
thick_stroke_width = 0.4 / 1000 / 2 * scale
thin_stroke_width = 0.2 / 1000 / 2 * scale / 2
buffer_val = 0.4 / 1000 / 2 * scale

expr1 = ' "elevation" % 180 = 0 '
expr2 = ' "elevation" IN (20,100,260,340) '

extent = raster_layer.extent()
extent_buffered = extent.buffered(thick_stroke_width * 2)

stroke_geom_layer = QgsVectorLayer("Polygon?crs=epsg:2193", "stroke_geom_layer", "memory")
stroke_geom_layer_pr = stroke_geom_layer.dataProvider()
stroke_geom_layer_pr.addAttributes([QgsField("t50_fid", QVariant.Int)])
stroke_geom_layer.updateFields()

first_clip = processing.run(
    "native:extractbyextent", {"INPUT": contours, "EXTENT": extent_buffered, "CLIP": True, "OUTPUT": "memory:"}
)["OUTPUT"]

QgsProject.instance().addMapLayer(first_clip)

print("contours clipped")

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

for feature in buffer.getFeatures():
    # add a feature
    fet = QgsFeature()
    fet.setGeometry(feature.geometry())
    fet.setAttributes([feature["t50_fid"]])
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


for feature in buffer_not_100.getFeatures():
    # add a feature
    fet = QgsFeature()
    fet.setGeometry(feature.geometry())
    fet.setAttributes([feature["t50_fid"]])
    stroke_geom_layer_pr.addFeatures([fet])

stroke_geom_layer.updateExtents()

# add rivers
river_poly_clip = processing.run(
    "native:extractbyextent", {"INPUT": river_poly, "EXTENT": extent_buffered, "CLIP": True, "OUTPUT": "memory:"}
)["OUTPUT"]
print("river poly clipped")

for feature in river_poly_clip.getFeatures():
    # add a feature
    fet = QgsFeature()
    fet.setGeometry(feature.geometry())
    fet.setAttributes([feature["t50_fid"]])
    stroke_geom_layer_pr.addFeatures([fet])

stroke_geom_layer.updateExtents()

dissolved_layer = processing.run("native:dissolve", {"INPUT": stroke_geom_layer, "FIELD": [], "OUTPUT": "memory:"})["OUTPUT"]
print("dissolve")

clipped_layer = processing.run(
    "native:extractbyextent", {"INPUT": dissolved_layer, "EXTENT": extent, "CLIP": True, "OUTPUT": "memory:"}
)["OUTPUT"]

clipped_layer.renderer().setSymbol(QgsFillSymbol.createSimple({"color": "#dcdcdc", "style_border": "no"}))
print("final clip")

QgsProject.instance().addMapLayer(clipped_layer)
QgsProject.instance().removeMapLayer(first_clip)
