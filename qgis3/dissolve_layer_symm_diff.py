from qgis.core import QgsProject
import processing
# processes based on first two layer in legend
# order not important but should be the exterior extent and the survey mosaic

legend_list = QgsProject.instance().layerTreeRoot().layerOrder()

# scratch1 = QgsProject.instance().mapLayersByName("scratch1")[-1]
# scratch2 = QgsProject.instance().mapLayersByName("scratch2")[-1]
scratch1 = legend_list[0]
scratch2 = legend_list[1]

dissolve_param1 = { 'FIELD' : [], 'INPUT' : scratch1, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
dissolve1 = processing.run("native:dissolve", dissolve_param1)["OUTPUT"]

dissolve_param2 = { 'FIELD' : [], 'INPUT' : scratch2, 'OUTPUT' : 'TEMPORARY_OUTPUT' }
dissolve2 = processing.run("native:dissolve", dissolve_param2)["OUTPUT"]

symm_param = { 'INPUT' : dissolve1, 'OUTPUT' : 'TEMPORARY_OUTPUT', 'OVERLAY' : dissolve2, 'OVERLAY_FIELDS_PREFIX' : '' }
symm = processing.run("native:symmetricaldifference", symm_param)["OUTPUT"]

QgsProject.instance().addMapLayer(symm)
