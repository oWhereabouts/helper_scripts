from qgis.utils import iface
from qgis.core import QgsFeature, QgsGeometry, QgsLineSymbol, QgsProject, QgsVectorLayer

# taking geoetic layer with lat lon and change in east and change in north, and creating line layer from these

layer = iface.activeLayer()

lines = QgsVectorLayer("LineString?crs=epsg:4167", "lines", "memory")
lines_pr = lines.dataProvider()

for feature in layer.getFeatures():
    attr = feature.attributes()
    lon = attr[0]
    lat = attr[1]
    de = attr[2]
    dn = attr[3]
    new_lon = lon + dn
    new_lat = lat + de
    # print(lat)
    # print(new_lat)

    first_pnt = QgsPoint(lon, lat)
    second_pnt = QgsPoint(new_lon, new_lat)
    geom = QgsGeometry.fromPolyline([first_pnt, second_pnt])
    fet = QgsFeature()
    fet.setGeometry(geom)
    lines_pr.addFeatures([fet])

lines.updateExtents()
QgsProject.instance().addMapLayer(lines)