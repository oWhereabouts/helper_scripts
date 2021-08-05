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


# polygonize the raster as it is at a 45 degree angle
"""
{ 'BAND' : 1, 'EIGHT_CONNECTEDNESS' : False, 'EXTRA' : '', 'FIELD' : 'DN', 'INPUT' : '/home/pking/carto/working/window_decals/working/round4/ data/kanuka_rectangle1.png', 'OUTPUT' : 'TEMPORARY_OUTPUT' }
alglist("polygonize")
processing.run("gdal:polygonize"
processing.run("gdal:polygonize", {'INPUT':Recalteracaoset,'BAND':1,'FIELD':'DN','EIGHT_CONNECTEDNESS':False,'OUTPUT':alteracaovetor})
alglist("clip")
processing.run("native:clip"
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


scale = 10000
stroke_width = 0.1 / 1000
buffer_val = scale * stroke_width * 0.5

unclipped_layer = QgsProject.instance().mapLayersByName("kanuka_parcel")[-1]
raster_area = QgsProject.instance().mapLayersByName("kanuka_rectangle2")[-1]
# print(raster_area.isValid())
# # { 'BAND' : 1, 'EIGHT_CONNECTEDNESS' : False, 'EXTRA' : '', 'FIELD' : 'DN', 'INPUT' : '/home/pking/carto/working/window_decals/working/round4/ data/kanuka_rectangle2.png', 'OUTPUT' : 'TEMPORARY_OUTPUT' }
# params_polygonize = {
#     "INPUT": raster_area,
#     "BAND": 1,
#     "FIELD": "DN",
#     "EIGHT_CONNECTEDNESS": False,
#     "OUTPUT": "TEMPORARY_OUTPUT",
# }
# vector_area_path = processing.run("gdal:polygonize", params_polygonize)["OUTPUT"]
# print("polygonize")
# # print(vector_area)
# vector_area_layer = QgsVectorLayer(vector_area_path, "vector_area_path", "ogr")
# print(vector_area_layer.isValid())
# QgsProject.instance().addMapLayer(vector_area_layer)
# could not get it to work so created the polygon manually

vector_area_layer = QgsProject.instance().mapLayersByName("kanuka_area")[-1]

vector_area_buff = processing.run("native:buffer", buffer_params(vector_area_layer, buffer_val * 2, False))["OUTPUT"]
print("buffer polygonize")
# QgsProject.instance().addMapLayer(vector_area_buff)
print(vector_area_buff.isValid())
print(vector_area_buff.extent())

# clip vector layer
params_clip = {"INPUT": unclipped_layer, "OVERLAY": vector_area_buff, "OUTPUT": "memory:"}
layer = processing.run("native:clip", params_clip)["OUTPUT"]
QgsProject.instance().addMapLayer(layer)
print(layer.extent())

expr = " \"parcel_intent\" !=  'Road'"
layer.selectByExpression(expr, QgsVectorLayer.SetSelection)

inner_buffer = processing.run(
    "native:buffer", buffer_params(QgsProcessingFeatureSourceDefinition(layer.id(), True), buffer_val * -1, False)
)["OUTPUT"]
print("inner_buffer")
outer_buffer = processing.run(
    "native:buffer", buffer_params(QgsProcessingFeatureSourceDefinition(layer.id(), True), buffer_val, False)
)["OUTPUT"]
print("outer_buffer")
stroke_geom_layer = QgsVectorLayer("Polygon?crs=epsg:2193", "stroke_geom_layer", "memory")
stroke_geom_layer_pr = stroke_geom_layer.dataProvider()
stroke_geom_layer_pr.addAttributes([QgsField("fid", QVariant.Int)])
stroke_geom_layer.updateFields()

for feature in layer.selectedFeatures():
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

# # QgsProject.instance().addMapLayer(stroke_geom_layer)
# # print(count)
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

params_clip = {"INPUT": dissolved_layer, "OVERLAY": vector_area_layer, "OUTPUT": "memory:"}
clipped_layer = processing.run("native:clip", params_clip)["OUTPUT"]
clipped_layer.renderer().setSymbol(QgsFillSymbol.createSimple({"color": "#dcdcdc", "style_border": "no"}))


QgsProject.instance().addMapLayer(clipped_layer)
QgsProject.instance().removeMapLayer(layer)
# QgsProject.instance().removeMapLayer(vector_area_buff)
# QgsProject.instance().removeMapLayer(vector_area_layer)

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
