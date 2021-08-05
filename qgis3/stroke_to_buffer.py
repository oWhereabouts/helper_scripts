from qgis.utils import iface
from qgis.core import QgsProcessingFeatureSourceDefinition, QgsProject, QgsVectorLayer

"""
to avoid havign to use "stroke to path" which keeps crashing in inkscape
I want to take the geom and turn the stroke to a polygon
for each geom
add a buffer of half the stroke and remove a buffer of half the negative stroke
then do a union so it is already a complete layer

later could also do the solid fills so its just a qgis layer completely ready
"""


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


unclipped_layer = iface.activeLayer()
# scale = 10000
scale = 5000
stroke_width = 0.1 / 1000
buffer_val = scale * stroke_width * 0.5

# raster_layer = QgsProject.instance().mapLayersByName("te_puna_rectangle1")[-1]
# raster_layer = QgsProject.instance().mapLayersByName("area3_rectangle1")[-1]
raster_layer = QgsProject.instance().mapLayersByName("area3_rectangle2")[-1]
extent = raster_layer.extent()
extent_buffered = extent.buffered(buffer_val * 2)
layer = processing.run(
    "native:extractbyextent", {"INPUT": unclipped_layer, "EXTENT": extent_buffered, "CLIP": True, "OUTPUT": "memory:"}
)["OUTPUT"]
print(layer.isValid())
QgsProject.instance().addMapLayer(layer)

expr = " \"parcel_intent\" !=  'Road'"
layer.selectByExpression(expr, QgsVectorLayer.SetSelection)

inner_buffer = processing.run(
    "native:buffer", buffer_params(QgsProcessingFeatureSourceDefinition(layer.id(), True), buffer_val * -1, False)
)["OUTPUT"]
# print(inner_buffer.featureCount())
print("inner_buffer")
outer_buffer = processing.run(
    "native:buffer", buffer_params(QgsProcessingFeatureSourceDefinition(layer.id(), True), buffer_val, False)
)["OUTPUT"]
print("outer_buffer")
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
# QgsProject.instance().addMapLayer(stroke_geom_layer)
# print(count)
print("difference_buffers")
expr = " \"parcel_intent\" =  'Road'"
layer.selectByExpression(expr, QgsVectorLayer.SetSelection)

outer_buffer = processing.run(
    "native:buffer", buffer_params(QgsProcessingFeatureSourceDefinition(layer.id(), True), buffer_val, False)
)["OUTPUT"]
print("road_buffers")

for feature in outer_buffer.getFeatures():
    fet = QgsFeature()
    fet.setGeometry(feature.geometry())
    fet.setAttributes([feature["fid"]])
    stroke_geom_layer_pr.addFeatures([fet])

stroke_geom_layer.updateExtents()
print("added road_buffers")

dissolved_layer = processing.run("native:dissolve", {"INPUT": stroke_geom_layer, "FIELD": [], "OUTPUT": "memory:"})["OUTPUT"]
# QgsProject.instance().addMapLayer(dissolved_layer)
print("dissolve")
"""processing.runalg('gdalogr:clipvectorsbyextent', input_layer, clip_extent, options, output_layer)

for alg in QgsApplication.processingRegistry().algorithms():
    print(alg.id(), "->", alg.displayName())

    clipvectorsbyextent

def alglist(search_term: str = False):
    s = ""
    for alg in QgsApplication.processingRegistry().algorithms():
        if search_term:
            if search_term.lower() in alg.displayName().lower():
                s += "{}->{}\n".format(alg.id(), alg.displayName())
        else:
            s += "{}->{}\n".format(alg.id(), alg.displayName())
            # l = alg.displayName().ljust(50, "-")
            # r = alg.id()
            # s += '{}--->{}\n'.format(l, r)
    print(s)

alglist("clipvectorsbyextent")

processing.algorithmHelp("gdal:clipvectorbyextent")
"""
clipped_layer = processing.run(
    "native:extractbyextent", {"INPUT": dissolved_layer, "EXTENT": extent, "CLIP": True, "OUTPUT": "memory:"}
)["OUTPUT"]
QgsProject.instance().addMapLayer(clipped_layer)
QgsProject.instance().removeMapLayer(layer)
