from qgis.core import QgsFeature, QgsProject, QgsVectorLayer

for layer_name in ("test_polygon", "test_average_line"):
    layers = QgsProject.instance().mapLayersByName(layer_name)
    for layer in layers:
        QgsProject.instance().removeMapLayer(layer)

poly_layer = QgsVectorLayer("Polygon?crs=epsg:2193", "test_polygon", "memory")
poly_layer_pr = poly_layer.dataProvider()

# # add fields
# poly_layer_pr.addAttributes([QgsField("name", QVariant.String),
#                     QgsField("age",  QVariant.Int),
#                     QgsField("size", QVariant.Double)])
# poly_layer.updateFields() # tell the vector layer to fetch changes from the provider

# add a feature
fet = QgsFeature()
fet.setGeometry(polygon_geom)
# fet.setAttributes(["Johny", 2, 0.3])
poly_layer_pr.addFeatures([fet])

poly_layer.updateExtents()
QgsProject.instance().addMapLayer(poly_layer)

average_line_layer = QgsVectorLayer("LineString?crs=epsg:2193", "test_average_line", "memory")
average_line_layer_pr = average_line_layer.dataProvider()

# # add fields
# poly_layer_pr.addAttributes([QgsField("name", QVariant.String),
#                     QgsField("age",  QVariant.Int),
#                     QgsField("size", QVariant.Double)])
# poly_layer.updateFields() # tell the vector layer to fetch changes from the provider

# add a feature
fet = QgsFeature()
fet.setGeometry(QgsGeometry().fromPolylineXY(average_edge))
# fet.setAttributes(["Johny", 2, 0.3])
average_line_layer_pr.addFeatures([fet])

new_poly.setGeometry(QgsGeometry.fromMultiPolygonXY([[new_coords]]))

average_line_layer.updateExtents()
QgsProject.instance().addMapLayer(average_line_layer)

new_layer.renderer().setSymbol(
    QgsFillSymbol.createSimple({"color": "0,0,0,0", "color_border": "#ff0101", "width_border": "0.46"})
)
# or line QgsLineSymbol.createSimple({'color': '#82aebd', 'line_width': '1'})
# for my style options https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/vector.html#appearance-symbology-of-vector-layers
new_layer.triggerRepaint()

