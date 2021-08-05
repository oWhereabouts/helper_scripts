import numpy as np
import os
from osgeo.ogr import Layer
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsExpression,
    QgsFeature,
    QgsFeatureRequest,
    QgsField,
    QgsFields,
    QgsProject,
    QgsVectorFileWriter,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QVariant

final_building_outlines = QgsProject.instance().mapLayersByName(
    "final_building_outlines"
)[-1]

outputPath = "/home/pking/buildings_names_and_uses/load_hosp_school/copy_assign"
output_name = "error_layer"
output_destination = os.path.join(outputPath, output_name + ".gpkg")
# output_destination = os.path.join(outputPath, output_name + ".shp")

error_layers = QgsProject.instance().mapLayersByName(output_name)
if len(error_layers) > 0:
    for layer in error_layers:
        QgsProject.instance().removeMapLayer(layer)
if os.path.isfile(output_destination):
    os.remove(output_destination)

# crs = QgsCoordinateReferenceSystem("EPSG:2193")
crs = final_building_outlines.sourceCrs()
# fields = QgsFields()
# fields.append(QgsField("Id", QVariant.Int))
# fields.append(QgsField("Comments", QVariant.String, "string", 150))
fields = final_building_outlines.fields()
name_field = final_building_outlines.fields().field(
    final_building_outlines.fields().indexFromName("name")
)
name_field.setName("name_assigned")

use_field = final_building_outlines.fields().field(
    final_building_outlines.fields().indexFromName("use")
)
use_field.setName("use_assigned")

status_field = final_building_outlines.fields().field(
    final_building_outlines.fields().indexFromName("status")
)
status_field.setName("status_assigned")

error_comment = QgsField("Error_comment", QVariant.String, "string", 150)
for field in (name_field, use_field, status_field, error_comment):
    fields.append(field)
fields.append(name_field)
# wkbtype = QgsWkbTypes.Point
wkbtype = final_building_outlines.wkbType()

writer = QgsVectorFileWriter(
    output_destination, None, fields, wkbtype, crs, driverName="GPKG"
)

if writer.hasError() != QgsVectorFileWriter.NoError:
    msg = "Error when creating assigned buildings error layer: {}".format(
        writer.errorMessage()
    )
    print(msg)

del writer

error_layer = QgsVectorLayer(output_destination, output_name, "ogr")
QgsProject.instance().addMapLayer(error_layer)
