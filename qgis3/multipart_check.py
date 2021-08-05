import os
from qgis.PyQt.QtCore import QVariant
from qgis.core import QgsFeature, QgsField, QgsMapLayer, QgsProject, QgsWkbTypes, QgsVectorLayer
from qgis.utils import iface

# layers = iface.legendInterface().layers()
# for layer in layers:
#     if layer.name() == "road_cl_updated":
#         for feat in layer.getFeatures():
#             if not feat.geometry():
#                 print feat['t50_fid'], feat['qa_id']
#     elif layer.name() == "track_cl_updated":
#         for feat in layer.getFeatures():
#             if not feat.geometry():
#                 print feat['t50_fid'], feat['qa_id']


def multi_check():
    road_cl_updated = QgsProject.instance().mapLayersByName("road_cl")
    track_cl_updated = QgsProject.instance().mapLayersByName("track_cl")

    # road_cl_updated = QgsProject.instance().mapLayersByName("road_cl_updated")
    # track_cl_updated = QgsProject.instance().mapLayersByName("track_cl_updated")

    count = 0

    for layer_list in (road_cl_updated, track_cl_updated):
        if layer_list == road_cl_updated:
            name = "Multipart road check"
            source_name = "road_cl_updated"
        elif layer_list == track_cl_updated:
            name = "Multipart track check"
            source_name = "track_cl_updated"

        # check layers exist, and not multiple layers
        if len(layer_list) != 1:
            if len(layer_list) == 0:
                return [False, "No layers named {}".format(source_name)]
            else:
                return [False, "Multiple layers named {}".format(source_name)]

        layer = layer_list[0]

        # check layer type and geometry type
        print(QgsWkbTypes.displayString(int(layer.wkbType())))
        layer_type = layer.type()
        if layer_type != QgsMapLayer.VectorLayer:
            msg = "Invalid layer type, requires vector layer"
            return [False, msg]

        geometry_type = QgsWkbTypes.displayString(int(layer.wkbType()))
        if geometry_type not in ("LineString", "MultiLineString"):
            msg = "Invalid layer geometry {}, requires LineString ".format(geometry_type)
            return [False, msg]

        # create memory layer
        memory_layer = QgsVectorLayer("LineString?crs=epsg:2193", name, "memory")
        memory_layer_pr = memory_layer.dataProvider()

        oldattributeList = layer.dataProvider().fields().toList()
        newattributeList = []
        for attrib in oldattributeList:
            newattributeList.append(QgsField(attrib.name(), attrib.type()))
        newattributeList.append(QgsField("geometry error", QVariant.String, "string", 50))
        memory_layer_pr.addAttributes(newattributeList)
        memory_layer.updateFields()

        fet = QgsFeature()

        layer_count = 0

        # iterate through features looking for multipart features
        for feature in layer.getFeatures():
            geom = feature.geometry()
            if not geom:
                fet = QgsFeature()
                attributes = feature.attributes()
                attributes.append("Null geometry")
                fet.setAttributes(attributes)
                memory_layer_pr.addFeatures([fet])
                layer_count += 1
            elif QgsWkbTypes.displayString(int(geom.wkbType())) != "LineString":
                if len(geom.asMultiPolyline()) > 1:
                    # print(QgsWkbTypes.displayString(int(geom.wkbType())))
                    # print(geom.isMultipart())
                    # print(len(geom.asMultiPolyline()))
                    for line in geom.asMultiPolyline():
                        print(len(line))
                print(geom.isMultipart())
                fet.setGeometry(geom)
                attributes = feature.attributes()
                attributes.append(QgsWkbTypes.displayString(int(geom.wkbType())))
                fet.setAttributes(attributes)
                memory_layer_pr.addFeatures([fet])
                layer_count += 1

        # if multiparts have been found display to the user and style
        if layer_count > 0:
            memory_layer.updateExtents()
            QgsProject.instance().addMapLayer(memory_layer)
            # style error layer
            count += layer_count

    if count == 0:
        msg = "Processing Done \n" "No multipart features found"
        return [True, msg]
    else:
        msg = "Processing Done \n" "{} multipart features found".format(count)
        return [False, msg]


print(multi_check())
