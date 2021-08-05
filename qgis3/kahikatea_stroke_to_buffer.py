from qgis.core import QgsProcessingFeatureSourceDefinition, QgsProject, QgsVectorLayer

rivers = QgsProject.instance().mapLayersByName("kahikatea_river")[-1]
water_race = QgsProject.instance().mapLayersByName("kahikatea_water_race")[-1]
lake = QgsProject.instance().mapLayersByName("kahikatea_lake")[-1]
river_poly = QgsProject.instance().mapLayersByName("kahikatea_river_poly")[-1]
raster_layer = QgsProject.instance().mapLayersByName("kahikatea_rectangle1")[-1]

extent = raster_layer.extent()

scale = 100000
stroke_width = 0.2 / 1000 * scale / 2

extent_buffered = extent.buffered(stroke_width * 2)

stroke_geom_layer = QgsVectorLayer("Polygon?crs=epsg:2193", "stroke_geom_layer", "memory")
stroke_geom_layer_pr = stroke_geom_layer.dataProvider()
stroke_geom_layer_pr.addAttributes([QgsField("t50_fid", QVariant.Int)])
stroke_geom_layer.updateFields()

rivers_clip = processing.run(
    "native:extractbyextent", {"INPUT": rivers, "EXTENT": extent_buffered, "CLIP": True, "OUTPUT": "memory:"}
)["OUTPUT"]

print("rivers clipped")

params_riverbuff = {
    "INPUT": rivers_clip,
    "DISTANCE": stroke_width,
    "SEGMENTS": 8,
    "END_CAP_STYLE": 0,
    "JOIN_STYLE": 0,
    "MITER_LIMIT": 3.5,
    "DISSOLVE": False,
    "OUTPUT": "memory:",
}

river_buff = processing.run("native:buffer", params_riverbuff)["OUTPUT"]
print("rivers buffered")

for feature in river_buff.getFeatures():
    # add a feature
    fet = QgsFeature()
    fet.setGeometry(feature.geometry())
    fet.setAttributes([feature["t50_fid"]])
    stroke_geom_layer_pr.addFeatures([fet])

stroke_geom_layer.updateExtents()

water_race_clip = processing.run(
    "native:extractbyextent", {"INPUT": water_race, "EXTENT": extent_buffered, "CLIP": True, "OUTPUT": "memory:"}
)["OUTPUT"]

print("water race clipped")

params_water_race = {
    "INPUT": water_race_clip,
    "DISTANCE": stroke_width,
    "SEGMENTS": 8,
    "END_CAP_STYLE": 0,
    "JOIN_STYLE": 0,
    "MITER_LIMIT": 3.5,
    "DISSOLVE": False,
    "OUTPUT": "memory:",
}

water_race_buff = processing.run("native:buffer", params_water_race)["OUTPUT"]
print("water race buffered")

for feature in water_race_buff.getFeatures():
    # add a feature
    fet = QgsFeature()
    fet.setGeometry(feature.geometry())
    fet.setAttributes([feature["t50_fid"]])
    stroke_geom_layer_pr.addFeatures([fet])

stroke_geom_layer.updateExtents()

lake_clip = processing.run(
    "native:extractbyextent", {"INPUT": lake, "EXTENT": extent_buffered, "CLIP": True, "OUTPUT": "memory:"}
)["OUTPUT"]

print("lake clipped")

for feature in lake_clip.getFeatures():
    # add a feature
    fet = QgsFeature()
    fet.setGeometry(feature.geometry())
    fet.setAttributes([feature["t50_fid"]])
    stroke_geom_layer_pr.addFeatures([fet])

stroke_geom_layer.updateExtents()

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
