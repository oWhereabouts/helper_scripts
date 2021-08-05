from qgis.core import QgsProcessingFeatureSourceDefinition, QgsProject, QgsVectorLayer


def buffer_params(input_layer, distance, dissolve):
    return {
        "INPUT": input_layer,
        "DISTANCE": distance,
        "SEGMENTS": 5,
        "END_CAP_STYLE": 0,
        "JOIN_STYLE": 1,
        "MITER_LIMIT": 3.5,
        "DISSOLVE": dissolve,
        "OUTPUT": "memory:",
    }


rivers = QgsProject.instance().mapLayersByName("arapuni_river")[-1]
lakes = QgsProject.instance().mapLayersByName("arapuni_lake")[-1]
parcels = QgsProject.instance().mapLayersByName("arapuni_parcels")[-1]
raster_layer = QgsProject.instance().mapLayersByName("arapuni_rectangle1")[-1]

scale = 22000
river_stroke = 0.4 / 1000 * scale / 2
parcels_stroke = 0.1 / 1000 * scale / 2

extent = raster_layer.extent()
extent_buffered = extent.buffered(river_stroke * 2)

stroke_geom_layer = QgsVectorLayer("Polygon?crs=epsg:2193", "stroke_geom_layer", "memory")
stroke_geom_layer_pr = stroke_geom_layer.dataProvider()
stroke_geom_layer_pr.addAttributes([QgsField("fid", QVariant.Int)])
stroke_geom_layer.updateFields()

rivers_clip = processing.run(
    "native:extractbyextent", {"INPUT": rivers, "EXTENT": extent_buffered, "CLIP": True, "OUTPUT": "memory:"}
)["OUTPUT"]

print("rivers clipped")

params_riverbuff = {
    "INPUT": rivers_clip,
    "DISTANCE": river_stroke,
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
    fet.setAttributes([feature["fid"]])
    stroke_geom_layer_pr.addFeatures([fet])

stroke_geom_layer.updateExtents()

lake_clip = processing.run(
    "native:extractbyextent", {"INPUT": lakes, "EXTENT": extent_buffered, "CLIP": True, "OUTPUT": "memory:"}
)["OUTPUT"]

print("lake clipped")

for feature in lake_clip.getFeatures():
    # add a feature
    fet = QgsFeature()
    fet.setGeometry(feature.geometry())
    fet.setAttributes([feature["fid"]])
    stroke_geom_layer_pr.addFeatures([fet])

stroke_geom_layer.updateExtents()

parcel_clip = processing.run(
    "native:extractbyextent", {"INPUT": parcels, "EXTENT": extent_buffered, "CLIP": True, "OUTPUT": "memory:"}
)["OUTPUT"]
QgsProject.instance().addMapLayer(parcel_clip)

print("parcels clipped")

expr = " \"parcel_intent\" !=  'Road'"
parcel_clip.selectByExpression(expr, QgsVectorLayer.SetSelection)

inner_buffer = processing.run(
    "native:buffer", buffer_params(QgsProcessingFeatureSourceDefinition(parcel_clip.id(), True), parcels_stroke * -1, False)
)["OUTPUT"]
print("inner_buffer")
outer_buffer = processing.run(
    "native:buffer", buffer_params(QgsProcessingFeatureSourceDefinition(parcel_clip.id(), True), parcels_stroke, False)
)["OUTPUT"]
print("outer_buffer")

for feature in parcel_clip.selectedFeatures():
    geom = feature.geometry()
    feat_id = feature["fid"]
    expr = ' "fid" = {}'.format(feat_id)
    inner_buffer.selectByExpression(expr, QgsVectorLayer.SetSelection)
    for feature in inner_buffer.selectedFeatures():
        inner_geom = feature.geometry()
    outer_buffer.selectByExpression(expr, QgsVectorLayer.SetSelection)
    for feature in outer_buffer.selectedFeatures():
        outer_geom = feature.geometry()
    stroke_geom = outer_geom.difference(inner_geom)

    # add a feature
    fet = QgsFeature()
    fet.setGeometry(stroke_geom)
    fet.setAttributes([feat_id])
    stroke_geom_layer_pr.addFeatures([fet])

stroke_geom_layer.updateExtents()
print("difference_buffers")

expr = " \"parcel_intent\" =  'Road'"
parcel_clip.selectByExpression(expr, QgsVectorLayer.SetSelection)

road_buffer = processing.run(
    "native:buffer", buffer_params(QgsProcessingFeatureSourceDefinition(parcel_clip.id(), True), parcels_stroke, False)
)["OUTPUT"]
print("road_buffers")

for feature in road_buffer.getFeatures():
    fet = QgsFeature()
    fet.setGeometry(feature.geometry())
    fet.setAttributes([feature["fid"]])
    stroke_geom_layer_pr.addFeatures([fet])

stroke_geom_layer.updateExtents()
print("added road_buffers")

dissolved_layer = processing.run("native:dissolve", {"INPUT": stroke_geom_layer, "FIELD": [], "OUTPUT": "memory:"})["OUTPUT"]
print("dissolve")

clipped_layer = processing.run(
    "native:extractbyextent", {"INPUT": dissolved_layer, "EXTENT": extent, "CLIP": True, "OUTPUT": "memory:"}
)["OUTPUT"]

clipped_layer.renderer().setSymbol(QgsFillSymbol.createSimple({"color": "#dcdcdc", "style_border": "no"}))
print("final clip")

QgsProject.instance().addMapLayer(clipped_layer)
QgsProject.instance().removeMapLayer(parcel_clip)
