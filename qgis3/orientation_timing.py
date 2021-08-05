import os
import processing
from shutil import rmtree
import time

from qgis.core import QgsProject
from qgis.utils import iface

# layer = iface.activeLayer()

proj = QgsProject.instance()

residential_area_poly = QgsProject.instance().mapLayersByName("residential_area_poly")[-1]
linz_map_sheet = QgsProject.instance().mapLayersByName("linz_map_sheet")[-1]
output_directory = "/home/pking/buildings_names_and_uses/orientation/orig_bd34"
output_directory = "/home/pking/buildings_names_and_uses/orientation/new_convert_bb35"
if os.path.isdir(output_directory):
    rmtree(output_directory)
    os.makedirs(output_directory)
building_pnt_destination = os.path.join(output_directory, "generalised_building_pnt.gpkg")
building_poly_destination = os.path.join(output_directory, "generalised_building_poly.gpkg")
simplify = QgsProject.instance().mapLayersByName("simplify")[-1]

missing_building_pnt_destination = os.path.join(output_directory, "missing_building_pnt.gpkg")
missing_building_poly_destination = os.path.join(output_directory, "missing_building_poly.gpkg")


alg_parameters = {
    "INPUT_LAYER": simplify,
    "RESIDENTIAL_AREA_POLY": residential_area_poly,
    "LINZ_MAP_SHEET": linz_map_sheet,
    "BUILDING_PNT_DESTINATION": building_pnt_destination,
    "BUILDING_POLY_DESTINATION": building_poly_destination,
}
start_time = time.time()
result = processing.run("topogeneralistion:ConvertToTopo50", alg_parameters)
print("--- %s seconds ---" % (time.time() - start_time))
