from qgis.utils import iface
from qgis.core import QgsFeature, QgsLineSymbol, QgsProject, QgsVectorLayer

# create dicts of vert and horizontal lines. Iterate through features and grab min and max x and y
# see if min x in hori dict, if so check if its ymin lower than min or ymax higher than max and if so adjust
# do the same for xmax, ymin and ymax
# needs to be to x decimal places, oh but its 2193 so just in meters

layer = iface.activeLayer()
x_dict = {}
y_dict = {}

for feature in layer.getFeatures():
    bbox = feature.geometry().boundingBox()
    xmin = bbox.xMinimum()
    xmax = bbox.xMaximum()
    ymin = bbox.yMinimum()
    ymax = bbox.yMaximum()

    if xmin in x_dict:
        if ymin < x_dict[xmin]['ymin']:
            x_dict[xmin]['ymin'] = ymin
        if ymax > x_dict[xmin]['ymax']:
            x_dict[xmin]['ymax'] = ymax
    else:
        x_dict[xmin] = {}
        x_dict[xmin]['ymin'] = ymin
        x_dict[xmin]['ymax'] = ymax

    if xmax in x_dict:
        if ymin < x_dict[xmax]['ymin']:
            x_dict[xmax]['ymin'] = ymin
        if ymax > x_dict[xmax]['ymax']:
            x_dict[xmax]['ymax'] = ymax
    else:
        x_dict[xmax] = {}
        x_dict[xmax]['ymin'] = ymin
        x_dict[xmax]['ymax'] = ymax

    if ymin in y_dict:
        if xmin < y_dict[ymin]['xmin']:
            y_dict[ymin]['xmin'] = xmin
        if xmax > y_dict[ymin]['xmax']:
            y_dict[ymin]['xmax'] = xmax
    else:
        y_dict[ymin] = {}
        y_dict[ymin]['xmin'] = xmin
        y_dict[ymin]['xmax'] = xmax

    if ymax in y_dict:
        if xmin < y_dict[ymax]['xmin']:
            y_dict[ymax]['xmin'] = xmin
        if xmax > y_dict[ymax]['xmax']:
            y_dict[ymax]['xmax'] = xmax
    else:
        y_dict[ymax] = {}
        y_dict[ymax]['xmin'] = xmin
        y_dict[ymax]['xmax'] = xmax

grid2line_layer = QgsVectorLayer("LineString?crs=epsg:2193", "grid2line", "memory")
grid2line_layer_pr = grid2line_layer.dataProvider()
grid2line_layer_pr.addAttributes([QgsField("key",  QVariant.Int)])
grid2line_layer.updateFields()
for key, values in x_dict.items():
    ymin = values['ymin']
    ymax = values['ymax']

    # add a feature
    fet = QgsFeature()
    fet.setGeometry(QgsGeometry().fromPolylineXY([QgsPointXY(int(key), ymin), QgsPointXY(int(key), ymax)]))
    fet.setAttributes([key])
    grid2line_layer_pr.addFeatures([fet])

# for key, values in x_dict.items():
#     ymin = values['ymin']
#     ymax = values['ymax']

#     # add a feature
#     fet = QgsFeature()
#     fet.setGeometry(QgsGeometry().fromPolylineXY([QgsPointXY(key, ymin), QgsPointXY(key, ymax)]))
#     fet.setAttributes([key])
#     grid2line_layer_pr.addFeatures([fet])

for key, values in y_dict.items():
    xmin = values['xmin']
    xmax = values['xmax']

    # add a feature
    fet = QgsFeature()
    fet.setGeometry(QgsGeometry().fromPolylineXY([QgsPointXY(xmin, key), QgsPointXY(xmax,key)]))
    fet.setAttributes([key])
    grid2line_layer_pr.addFeatures([fet])

# for key, values in y_dict.items():
#     xmin = values['xmin']
#     xmax = values['xmax']

#     # add a feature
#     fet = QgsFeature()
#     fet.setGeometry(QgsGeometry().fromPolylineXY([QgsPointXY(xmin, key), QgsPointXY(xmax,key)]))
#     fet.setAttributes([key])
#     grid2line_layer_pr.addFeatures([fet])

grid2line_layer.updateExtents()
QgsProject.instance().addMapLayer(grid2line_layer)

# but this is just a pure grid and doesn't consider a line which is in north and south but with a gap between
# could take a combined/ dissolved grid and do an intersect to remove those bits?

dissolve = processing.run("native:dissolve", {"INPUT": layer, "FIELD": [], "OUTPUT": "memory:"})["OUTPUT"]

intersection = processing.run("native:intersection", { 'INPUT' : grid2line_layer, 'INPUT_FIELDS' : [], 'OUTPUT' : 'memory:', 'OVERLAY' : dissolve, 'OVERLAY_FIELDS' : [], 'OVERLAY_FIELDS_PREFIX' : '' })["OUTPUT"]
QgsProject.instance().addMapLayer(intersection)

intersection.renderer().setSymbol(
    QgsLineSymbol.createSimple({'color': '#82aebd', 'line_width': '0.5'})
)
intersection.triggerRepaint()

lineintersections = processing.run("native:lineintersections", { 'INPUT' : intersection, 'INPUT_FIELDS' : [], 'INTERSECT' : intersection, 'INTERSECT_FIELDS' : [], 'INTERSECT_FIELDS_PREFIX' : '', 'OUTPUT' : 'memory:' })["OUTPUT"]
QgsProject.instance().addMapLayer(lineintersections)