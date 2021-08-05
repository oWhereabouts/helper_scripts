from qgis.core import (
    QgsFeature,
    QgsFeatureRequest,
    QgsProject,
    QgsSpatialIndex,
    QgsVectorLayer
)

import time

def create_output(polygon_layer, output_path = "memory"):

    output_layer = QgsVectorLayer("MultiPolygon?crs=epsg:4167", "unmatched_buildings", output_path)
    output_layer_pr = output_layer.dataProvider()

    NMPoly_fieldslist = polygon_layer.dataProvider().fields().toList()

    output_layer.dataProvider().addAttributes(NMPoly_fieldslist)
    output_layer.updateFields()

    print("is valid {}".format(output_layer.isValid()))

    return output_layer

startTime = time.time()

polygon_layer = QgsProject.instance().mapLayersByName("Landuse LANDUSE")[-1]
buildings_layer = QgsProject.instance().mapLayersByName("nz-building-outlines nz_building_outlines")[-1]

output_txt_filepath = "/home/pking/buildings_names_and_uses/resilience/trial1/unmatched_polygons.txt"

output_layer = create_output(polygon_layer)

with open(output_txt_filepath, 'w') as text_file:
    indexStart = time.time()

    # make spatial index
    # request = QgsFeatureRequest().setLimit(100)
    buildings_index = QgsSpatialIndex(buildings_layer.getFeatures())
    # expression = '"fid" in (316100, 316078)'
    # request = QgsFeatureRequest().setFilterExpression(expression)
    # buildings_index = QgsSpatialIndex(buildings_layer.getFeatures(request))
    indexExecutionTime = (time.time() - indexStart)
    print('Execution time in seconds: {}'.format(str(indexExecutionTime)))

    # expression for schools and hospitals
    expression = '"FEATURE_TYPE" in ( \'Clinic\',  \'Hospice\',  \'Hospital\', \'School\')'
    request = QgsFeatureRequest().setFilterExpression(expression)

    # expression = '"UNIQUE_ID" = \'LANDUSE 130\''
    # request = QgsFeatureRequest().setFilterExpression(expression)

    # expression = '"UNIQUE_ID" = \'SCHOOLS 900021397\''
    # request = QgsFeatureRequest().setFilterExpression(expression)

    # simple request for 100 features to test timing
    # request = QgsFeatureRequest().setLimit(100)

    if request:
        iter = polygon_layer.getFeatures(request)
    else:
        iter = polygon_layer.getFeatures()
    # iter = polygon_layer.getFeatures()

    processed_count = 0
    count = 0
    for feature in iter:
        if processed_count % 100 == 0:
            print("{} processed".format(couprocessed_countnt))
        # if count > 3:
        #     break
        geom = feature.geometry()
        # text_file.write("Errors in file {}\n{}\n{}\n\n\n".format(tif_filepath, self.errors, gdalinfo))

        # find polygons schools within buffer_distance
        # point = get_buffered_point(feature.geometry(), input_crs, buffer_distance)
        # rectangle = point.boundingBox()

        # intersect_ids = index.intersects(rectangle)
        intersect_ids = buildings_index.intersects(geom.boundingBox())
        # print(intersect_ids)
        if intersect_ids != []:
            intersects = False
            intersect_request = QgsFeatureRequest().setFilterFids(intersect_ids)
            for intersect_feature in buildings_layer.getFeatures(intersect_request):
                if intersect_feature.geometry().intersects(geom):
                    intersects = True
                    break
            if not intersects:
                # add feature
                fet = QgsFeature()
                fet.setGeometry(geom)
                fet.setAttributes(feature.attributes())
                output_layer.dataProvider().addFeature(fet)
                output_layer.updateExtents()

                unique_id = feature['UNIQUE_ID']
                name = feature['NAME']
                text_file.write('No match: {} {}\n'.format(unique_id, name))
                count += 1
        else:
            output_layer.dataProvider().addFeature(feature)
            output_layer.updateExtents()

            unique_id = feature['UNIQUE_ID']
            name = feature['NAME']
            text_file.write('No match: {} {}\n'.format(unique_id, name))
            count += 1

        processed_count += 1

    text_file.write('Count of polygons which don\'t intersect: {}\n'.format(count))
    print('Count of polygons which don\'t intersect: {}'.format(count))

    QgsProject.instance().addMapLayer(output_layer)

    executionTime = (time.time() - startTime)
    text_file.write('Execution time in seconds: {}\n'.format(str(executionTime)))
    print('Execution time in seconds: {}'.format(str(executionTime)))
    print("featurecount = {}".format(output_layer.featureCount()))

text_file.close()

