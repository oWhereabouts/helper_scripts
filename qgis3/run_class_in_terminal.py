# run a class in qgis from terminal for testing


class AverageEdgeCalculator(object):
    """A class to deal with averaging edges."""

    # blah


from qgis.utils import iface
from qgis.core import QgsProject

layer = iface.activeLayer()

average_edge_calculator = AverageEdgeCalculator(layer)
output_layer, number_of_features = average_edge_calculator.run()
QgsProject.instance().addMapLayer(output_layer)
