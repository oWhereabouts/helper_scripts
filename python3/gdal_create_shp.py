import ogr, gdal
import osr

import os
from shutil import rmtree
from tempfile import mkdtemp

# test_folder = mkdtemp()
# path = os.path.join(test_folder, "trial.shp")
path = "/home/pking/imagery/create_shp/trial.shp"


shpDriver = ogr.GetDriverByName('ESRI Shapefile')
latlong = osr.SpatialReference()
latlong.ImportFromEPSG( 2193 )

outDataSource = shpDriver.CreateDataSource(path)
outLayer = outDataSource.CreateLayer('', srs=latlong, geom_type=ogr.wkbPoint)

outLayer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))
outDefn = outLayer.GetLayerDefn()
outFeature = ogr.Feature(outDefn)
outFeature.SetField('id', 1)
point = ogr.Geometry(ogr.wkbPoint)
point.AddPoint(2020000, 5679600)
outFeature.SetGeometry(point)
outLayer.CreateFeature(outFeature)

# Remove temporary files
outDataSource.Destroy() 

# rmtree(test_folder)
