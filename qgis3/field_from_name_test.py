from qgis.utils import iface
from qgis.core import QgsWkbTypes

input_layer = iface.activeLayer()
# facility_fields = input_layer.fields()
# print(len(facility_fields))
# name_field = facility_fields.field('poly_name')
# print(name_field)

# for feature in input_layer.selectedFeatures():
#     attributes = feature.attributes()
#     index = feature.fieldNameIndex('name')
#     print(index)

# fields = self.building_outlines_layer.dataProvider().fields()
# index = fields.indexFromName('name')
# fields.rename(index, 'associated_poly_name')

# index = building_feature.fieldNameIndex('associated_poly_name')
# full_attributes[0] = None
# full_attributes[0] = 'None'

geometry_type = QgsWkbTypes.displayString(int(input_layer.wkbType()))
if geometry_type.startswith('Multi'):
    print("was multi {}".format(geometry_type))
