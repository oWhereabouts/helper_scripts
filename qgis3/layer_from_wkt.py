from qgis.core import QgsFeature, QgsProject, QgsVectorLayer

# layer = QgsVectorLayer("Polygon", "wkt_layer", "memory")
layer = QgsVectorLayer("Polygon?crs=epsg:2193", "wkt_layer", "memory")
layer.startEditing()

# geom_wkts = [
# "Polygon ((0 7, 3 7, 3 5, 5 5, 5 2, 2 2, 2 4, 0 4, 0 7))",
# "Polygon ((2 5, 5 5, 5 3, 7 3, 7 0, 4 0, 4 2, 2 2, 2 5))"
# ]

"""
extent = '{0} {1} {2} {3}'.format(ulx, lry, lrx, uly)
2017600.0 5676000.0 2020000.0 5679600.0
"""

geom_wkts = [
"Polygon ((2017600.0 5676000.0, 2020000.0 5676000.0,2020000.0 5679600.0, 2017600.0 5679600.0, 2017600.0 5676000.0))",
]

for geom_wkt in geom_wkts:

    feat = QgsFeature()
    feat.setGeometry(QgsGeometry.fromWkt(geom_wkt))
    layer.dataProvider().addFeatures([feat])

layer.commitChanges()

QgsProject.instance().addMapLayer(layer)
