from qgis.utils import iface
from qgis.core import QgsGeometry, QgsWkbTypes

layer = iface.activeLayer()


for feature in layer.selectedFeatures():
    # round wkt to 1dp
    wkt = feature.geometry().asWkt(1)
    print(wkt)
    geom = feature.geometry()
    wkbtype = QgsWkbTypes.displayString(int(geom.wkbType()))
    print(wkbtype)
    # length = QgsGeometry.fromWkt(wkt).length()
    # print("length {}".format(length))

    print(len(geom.asMultiPolygon()))
    multi = geom.asMultiPolygon()[0][0]
    print(len(multi))
    # multi = multi[:]
    multi.reverse()
    print(len(multi))
    geom = QgsGeometry.fromMultiPolygonXY([[multi]])
    print(geom.asWkt(1))

# vrt layer sql = SELECT ST_GeomFromText('Polygon ((2 1, 0 1, 0 0, 1 0, 1 2, 2 1))')
# LINESTRING
# SELECT ST_GeomFromText('Linestring (2 1, 0 1, 0 0, 1 0, 1 2)',2193)
