# copy as memory layer
# find max value
# for each feature if null add max +1 and increment max value

from qgis.core import QgsFeature, QgsProject, QgsVectorDataProvider, QgsVectorLayer, QgsWkbTypes
from qgis.utils import iface


input_layer = iface.activeLayer()
# [-1 below is the last layer added with that name, other wise you iterate through the list of layers
# input_layer = QgsProject.instance().mapLayersByName("road_cl_2")[-1]

# make vector layer in memory with the same geom type
wkbtype = QgsWkbTypes.displayString(int(input_layer.wkbType()))
output_layer = QgsVectorLayer(
    "{}?crs=epsg:2193&index=yes".format(wkbtype), "incremented_layer", "memory",
)

# copy fields
attributeList = input_layer.dataProvider().fields().toList()
output_layer.dataProvider().addAttributes(attributeList)
output_layer.updateFields()

# find the index of the attribute
idx = output_layer.fields().indexFromName('qa_id')

# set up a variable to store the max value
max_value = 0

# iterate through the features in the input layer and copy features
for feature in input_layer.getFeatures():
    # copy the feature
    new_feat = QgsFeature()
    new_feat.setAttributes(feature.attributes())
    new_feat.setGeometry(feature.geometry())
    output_layer.dataProvider().addFeatures([new_feat])

    # find the value of the attribute and if larger than our current max change the max value
    attributes = feature.attributes()[idx]
    if attr_value > max_value:
        max_value = attr_value
# update extents resets the layers extents after geoms were added
output_layer.updateExtents()

# for each feature, if the attribute is null adjust the attributes to one larger than the max value and adjust the max value
output_layer.startEditing()
for feature in output_layer.getFeatures():
    attributes = feature.attributes()
    attr_value = attributes[idx]
    if not attr_value:
        max_value += 1
        attr_value = max_value
        output_layer.changeAttributeValue(feature.id(), idx, attr_value)
output_layer.commitChanges()

# add layer to the canvas
QgsProject.instance().addMapLayer(output_layer)
