from qgis.core import QgsProject
import processing
# processes based on first two layer in legend
# top must be exterior extent, the extent without holes
# second is the extent with holes

legend_list = QgsProject.instance().layerTreeRoot().layerOrder()

no_holes = legend_list[0]
holes = legend_list[1]

diff_param = { 'INPUT' : no_holes, 'OUTPUT' : 'TEMPORARY_OUTPUT', 'OVERLAY' :holes }
diff1 = processing.run("native:difference", diff_param)["OUTPUT"]

QgsProject.instance().addMapLayer(diff1)