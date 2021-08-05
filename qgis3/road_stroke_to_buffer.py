from qgis.utils import iface
from qgis.core import QgsProcessingFeatureSourceDefinition, QgsProject, QgsVectorLayer


def buffer_params(input_layer, distance, dissolve):
    # flat and bevel
    return {
        "INPUT": input_layer,
        "DISTANCE": distance,
        "SEGMENTS": 5,
        "END_CAP_STYLE": 2,
        "JOIN_STYLE": 2,
        "MITER_LIMIT": 3.5,
        "DISSOLVE": dissolve,
        "OUTPUT": "memory:",
    }


unclipped_layer = iface.activeLayer()
scale = 8500
lane4_stroke_width = 1.5 / 1000
lane3_stroke_width = 1.3 / 1000
lane2_stroke_width = 1.0 / 1000
lane1_stroke_width = 0.6 / 1000
lane4_buffer_val = scale * lane4_stroke_width
lane3_buffer_val = scale * lane3_stroke_width
lane2_buffer_val = scale * lane2_stroke_width
lane1_buffer_val = scale * lane1_stroke_width

raster_layer = QgsProject.instance().mapLayersByName("area2_rectangle1")[-1]
extent = raster_layer.extent()
extent_buffered = extent.buffered(lane4_buffer_val * 2)
not_smoothlayer = processing.run(
    "native:extractbyextent", {"INPUT": unclipped_layer, "EXTENT": extent_buffered, "CLIP": True, "OUTPUT": "memory:"}
)["OUTPUT"]
# QgsProject.instance().addMapLayer(not_smoothlayer)

# alglist("smooth")
# processing.run("native:smoothgeometry"
# processing.run("native:union"

params_smooth = {"INPUT": not_smoothlayer, "ITERATIONS": 3, "MAX_ANGLE": 180, "OFFSET": 0.2, "OUTPUT": "memory:"}
layer = processing.run("native:smoothgeometry", params_smooth)["OUTPUT"]
QgsProject.instance().addMapLayer(layer)

expr = ' "lane_count" >= 4'
layer.selectByExpression(expr, QgsVectorLayer.SetSelection)

lane4_buffer = processing.run(
    "native:buffer", buffer_params(QgsProcessingFeatureSourceDefinition(layer.id(), True), lane4_buffer_val, True)
)["OUTPUT"]

expr = ' "lane_count" = 3'
layer.selectByExpression(expr, QgsVectorLayer.SetSelection)

lane3_buffer = processing.run(
    "native:buffer", buffer_params(QgsProcessingFeatureSourceDefinition(layer.id(), True), lane3_buffer_val, True)
)["OUTPUT"]

expr = ' "lane_count" = 2'
layer.selectByExpression(expr, QgsVectorLayer.SetSelection)

lane2_buffer = processing.run(
    "native:buffer", buffer_params(QgsProcessingFeatureSourceDefinition(layer.id(), True), lane2_buffer_val, True)
)["OUTPUT"]

expr = ' "lane_count" = 1'
layer.selectByExpression(expr, QgsVectorLayer.SetSelection)

lane1_buffer = processing.run(
    "native:buffer", buffer_params(QgsProcessingFeatureSourceDefinition(layer.id(), True), lane1_buffer_val, True)
)["OUTPUT"]

params_union = {"INPUT": lane4_buffer, "OVERLAY": lane3_buffer, "OVERLAY_FIELDS_PREFIX": "", "OUTPUT": "memory:"}
first_union = processing.run("native:union", params_union)["OUTPUT"]

params_union = {"INPUT": lane2_buffer, "OVERLAY": lane1_buffer, "OVERLAY_FIELDS_PREFIX": "", "OUTPUT": "memory:"}
second_union = processing.run("native:union", params_union)["OUTPUT"]

params_union = {"INPUT": first_union, "OVERLAY": second_union, "OVERLAY_FIELDS_PREFIX": "", "OUTPUT": "memory:"}
third_union = processing.run("native:union", params_union)["OUTPUT"]

dissolved_layer = processing.run("native:dissolve", {"INPUT": third_union, "FIELD": [], "OUTPUT": "memory:"})["OUTPUT"]
clipped_layer = processing.run(
    "native:extractbyextent", {"INPUT": dissolved_layer, "EXTENT": extent, "CLIP": True, "OUTPUT": "memory:"}
)["OUTPUT"]
QgsProject.instance().addMapLayer(clipped_layer)
QgsProject.instance().removeMapLayer(layer)
