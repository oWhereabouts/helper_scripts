import itertools
from math import degrees, radians
import processing
import time

from qgis.core import (
    QgsExpression,
    QgsExpressionContext,
    QgsExpressionContextScope,
    QgsFeature,
    QgsFeatureRequest,
    QgsField,
    QgsGeometry,
    QgsProject,
    QgsVectorLayer,
    QgsVectorDataProvider,
)
from qgis.utils import iface


layer = iface.activeLayer()


def copy_layer(input_layer, name):
    """Copy a layer."""
    wkbtype = QgsWkbTypes.displayString(int(input_layer.wkbType()))
    crs = input_layer.sourceCrs().authid()
    layer = QgsVectorLayer("{}?crs={}&index=yes".format(wkbtype, crs), name, "memory",)
    # copy fields
    attributeList = input_layer.dataProvider().fields().toList()
    layer.dataProvider().addAttributes(attributeList)
    layer.updateFields()

    new_feat = QgsFeature()
    if input_layer.selectedFeatureCount() > 0:
        print("selected")
        features = input_layer.selectedFeatures()
    else:
        print("not selected")
        features = input_layer.getFeatures()
    for input_feat in features:
        new_feat.setGeometry(input_feat.geometry())
        new_feat.setAttributes(input_feat.attributes())
        layer.dataProvider().addFeature(new_feat)
    return layer


def add_and_calc_field_id(layer):
    field = QgsField("uniqueID", QVariant.Int)
    idx_uniqueID = layer.fields().indexFromName("uniqueID")
    # remove if field exists
    if idx_uniqueID != -1:
        layer.dataProvider().deleteAttributes([idx_uniqueID])
    layer.dataProvider().addAttributes([field])
    layer.updateFields()

    # calc
    idx_uniqueID = layer.fields().indexFromName("uniqueID")
    layer.startEditing()
    for feat in layer.getFeatures():
        uniqueID = feat.id()
        layer.changeAttributeValue(feat.id(), idx_uniqueID, uniqueID)
    layer.commitChanges()


def get_polygon(geom):
    wkbtype = QgsWkbTypes.displayString(int(geom.wkbType()))
    if wkbtype == "Polygon":
        # return in list so can handle multipart in same manner
        return [geom.asPolygon()], wkbtype
    elif wkbtype == "MultiPolygon":
        return geom.asMultiPolygon(), wkbtype
    else:
        return False, wkbtype


def orig_azi_script(layer, name):

    copied_layer = copy_layer(layer, "copied_layer")

    add_and_calc_field_id(copied_layer)

    alg_parameters = {"INPUT": copied_layer, "OUTPUT": "memory:"}
    buildingPoints = processing.run("native:centroids", alg_parameters,)["OUTPUT"]

    # Convert Polygon layer into lines
    alg_parameters = {"INPUT": copied_layer, "OUTPUT": "memory:"}
    buildingLines = processing.run("qgis:polygonstolines", alg_parameters)["OUTPUT"]

    # buildingLines.setName("buildingLines")

    # Explode lines
    alg_parameters = {"INPUT": buildingLines, "OUTPUT": "memory:"}
    buildingLinesExploded = processing.run("qgis:explodelines", alg_parameters)["OUTPUT"]

    # buildingLinesExploded.setName("buildingLinesExploded")

    # Add new fields
    buildingLinesExploded_pr = buildingLinesExploded.dataProvider()
    buildingLinesExploded_caps = buildingLinesExploded_pr.capabilities()
    buildingLinesExploded_pr.addAttributes([QgsField("lineLength", QVariant.Double)])  # QVariant.
    buildingLinesExploded_pr.addAttributes([QgsField("lineID", QVariant.Int)])  # QVariant.
    buildingLinesExploded_pr.addAttributes([QgsField("angle", QVariant.Double)])  # QVariant.
    buildingLinesExploded.updateFields()

    idx_lineLength = buildingLinesExploded.fields().indexFromName("lineLength")
    idx_lineID = buildingLinesExploded.fields().indexFromName("lineID")
    idx_line_angle = buildingLinesExploded.fields().indexFromName("angle")
    buildingLinesExploded.startEditing()
    for feature in buildingLinesExploded_pr.getFeatures():
        length = feature.geometry().length()
        # Add ID feild
        new_id = int(feature.id())
        angle = 0
        attrs = {idx_lineLength: length, idx_lineID: new_id, idx_line_angle: angle}
        fid = feature.id()
        if buildingLinesExploded_caps & QgsVectorDataProvider.ChangeAttributeValues:
            buildingLinesExploded_pr.changeAttributeValues({fid: attrs})

    buildingLinesExploded.commitChanges()

    # --------------------------------------------------------------------------------
    # Search for the longest length of every line and add it to the dictionary as a value
    # based on whether it is the longest line for the building.
    idx_uniqueID = buildingLinesExploded.fields().indexFromName("uniqueID")
    dist = {}  # create dictionary
    for feat in buildingLinesExploded.getFeatures():
        # If the feature ID is not already in the dictionary add it.
        if int(feat.attributes()[idx_uniqueID]) not in list(dist.keys()):
            dist[int(feat.attributes()[idx_uniqueID])] = [feat.attributes()[idx_lineLength], feat.attributes()[idx_lineID]]
        # If it is in there but larger than the previous distance add it
        elif int(feat.attributes()[idx_lineLength]) > dist[int(feat.attributes()[idx_uniqueID])][0]:
            dist[int(feat.attributes()[idx_uniqueID])] = [feat.attributes()[idx_lineLength], feat.attributes()[idx_lineID]]

    # Add values to the list of distance files
    distList = [x[1] for x in list(dist.values())]

    # Delete Features that are not in the dist list.
    buildingLinesExploded.startEditing()
    request = QgsFeatureRequest().setFilterExpression('"lineID" NOT IN ' + (str(tuple(distList))))
    ids = [f.id() for f in buildingLinesExploded.getFeatures(request)]
    for fid in ids:
        buildingLinesExploded.deleteFeature(fid)
    buildingLinesExploded.commitChanges()

    # --------------------------------------------------------------------------------
    # Calculate Angle of Line
    expression = QgsExpression(
        "(atan((xat(-1)-xat(0))/(yat(-1)-yat(0)))) * 180/3.14159 + (180 *(((yat(-1) -yat(0)) < 0) + (((xat(-1)-xat(0)) < 0 AND (yat(-1) - yat(0)) >0)*2)))"
    )

    exp_context = QgsExpressionContext()  # Added for QGIS3
    scope = QgsExpressionContextScope()  # Added for QGIS3
    exp_context.appendScope(scope)  # Added for QGIS3

    buildingLinesExploded.startEditing()
    for feature in buildingLinesExploded.getFeatures():
        scope.setFeature(feature)  # Added for QGIS3
        value = expression.evaluate(exp_context)  # feature changed to context for QGIS3
        buildingLinesExploded.changeAttributeValue(feature.id(), idx_line_angle, value)

    buildingLinesExploded.commitChanges()

    # ------------------------------------------------------------------------------
    # Add angle and radians fields to the building points layer. (LAMPS uses radians (anticlockwise) to determine building rotation.)

    buildingPoints_pr = buildingPoints.dataProvider()
    buildingPoints_caps = buildingPoints_pr.capabilities()
    buildingPoints_pr.addAttributes([QgsField("angle", QVariant.Double)])  # QVariant.
    buildingPoints_pr.addAttributes([QgsField("radians", QVariant.Double)])  # QVariant.
    buildingPoints.updateFields()

    idx_angle = buildingPoints.fields().indexFromName("angle")
    idx_radians = buildingPoints.fields().indexFromName("radians")
    idx_use = buildingPoints.fields().indexFromName("use")

    # Loop to add the angle field from the line layer to the point layer.
    for feat in buildingPoints.getFeatures():
        if (
            feat.attributes()[idx_use] != "church" or feat.attributes()[idx_use] is None
        ):  # Do not rotate use = 'church', because they have a special point symbol
            request = QgsFeatureRequest().setFilterRect(feat.geometry().boundingBox())
            for feat2 in buildingLinesExploded.getFeatures(request):
                if float(feat.attributes()[idx_uniqueID]) == float(feat2.attributes()[idx_uniqueID]):
                    # calculate building angle
                    buildingAngle = feat2.attributes()[idx_line_angle]
                    # calculate building radians
                    if buildingAngle == None or buildingAngle == 0:
                        buildingRadians = 0
                    else:
                        buildingRadians = (360.0 - buildingAngle) * 0.0174533
                    # attribute field values
                    attrs = {idx_angle: buildingAngle, idx_radians: buildingRadians}
                    fid = feat.id()
                    if buildingPoints_caps & QgsVectorDataProvider.ChangeAttributeValues:
                        buildingPoints_pr.changeAttributeValues({fid: attrs})

    QgsProject.instance().addMapLayer(copied_layer)
    QgsProject.instance().addMapLayer(buildingPoints)

    arrow_qml = "/home/pking/buildings_names_and_uses/orientation/orientation_style.qml"
    buildingPoints.loadNamedStyle(arrow_qml)
    buildingPoints.triggerRepaint()

    copied_layer.setName("old_poly")
    buildingPoints.setName("old_point")


def new_azi_script(layer, name):
    copied_layer = copy_layer(layer, "copied_layer")

    add_and_calc_field_id(copied_layer)

    alg_parameters = {"INPUT": copied_layer, "OUTPUT": "memory:"}
    centroids = processing.run("native:centroids", alg_parameters,)["OUTPUT"]

    # add an angle field
    centroids.dataProvider().addAttributes(
        [QgsField("angle", QVariant.Double), QgsField("radians", QVariant.Double), QgsField("radians2", QVariant.Double),]
    )
    centroids.updateFields()
    # do the work
    idx_uniqueID = copied_layer.fields().indexFromName("uniqueID")

    idx_angle = centroids.fields().indexFromName("angle")
    idx_radians = centroids.fields().indexFromName("radians")
    idx_radians2 = centroids.fields().indexFromName("radians2")
    # idx_uniqueID = centroids.fields().indexFromName("uniqueID")

    poly_layer = QgsVectorLayer("Polygon?crs=epsg:2193", "test_polygon", "memory")
    poly_layer_pr = poly_layer.dataProvider()
    attributeList = copied_layer.dataProvider().fields().toList()
    poly_layer_pr.addAttributes(attributeList)
    poly_layer.updateFields()

    # lg_parameters = {
    #     "INPUT": copied_layer,
    #     "DISTANCE": 0.001,
    #     "DISSOLVE": False,
    #     "SEGMENTS": 3,
    #     "OUTPUT": "memory:",
    # }
    # buffer_buildings = processing.run("native:buffer", alg_parameters)["OUTPUT"]

    # copied_layer.startEditing()
    count = 0
    for feat in copied_layer.getFeatures():
        # for feat in buffer_buildings.getFeatures():
        count += 1
        if count % 100 == 0:
            print(count)
        # if count > 500:
        #     break
        field = "uniqueID"
        expr = QgsExpression("{} = {}".format(field, float(feat.attributes()[idx_uniqueID])))

        # expr = QgsExpression('"uniqueID" = {}'.format(field, float(feat.attributes()[idx_uniqueID])))
        expr = QgsExpression('"uniqueID" = {}'.format(field, float(feat.attributes()[idx_uniqueID])))

        # geom, area, angle, width, height = feat.geometry().orientedMinimumBoundingBox()

        geom, area, angle, width, height = feat.geometry().buffer(0.001, 3).orientedMinimumBoundingBox()

        fet = QgsFeature()
        fet.setGeometry(geom)
        poly_layer_pr.addFeatures([fet])

        angle = angle % 90
        # calculate building radians
        if angle == None or angle == 0:
            radian = 0
        else:
            radian2 = (360.0 - angle) * 0.0174533
            radian = radians(angle)

        for feature in centroids.getFeatures(QgsFeatureRequest(expr)):
            attrs = {idx_angle: angle, idx_radians: radian, idx_radians2: radian2}
            fid = feature.id()
            if centroids.dataProvider().capabilities() & QgsVectorDataProvider.ChangeAttributeValues:
                centroids.dataProvider().changeAttributeValues({fid: attrs})
        # for feature in centroids.getFeatures(expr):
        #     # geom = feat.geometry()
        #     # get the angle
        #     # angle = None
        #     geom, area, angle, width, height = feat.geometry().orientedMinimumBoundingBox()
        #     angle = angle % 90
        #     # calculate building radians
        #     if angle == None or angle == 0:
        #         radian = 0
        #     else:
        #         # radians = (360.0 - angle) * 0.0174533
        #         radian = radians(angle)
        #     # attribute field values
        #     # centroids.changeAttributeValue(feat.id(), idx_angle, azi_angle)
        #     # centroids.changeAttributeValue(feat.id(), idx_angle, azi_angle)

        #     attrs = {idx_angle: angle, idx_radians: radian}
        #     fid = feature.id()
        #     if centroids.dataProvider().capabilities() & QgsVectorDataProvider.ChangeAttributeValues:
        #         centroids.dataProvider().changeAttributeValues({fid: attrs})
        #     # print(geom)
        #     # print(angle)
        #     # print(width)
        #     # print(height)

        #     # if angle < 0:
        #     #     print("was less than 0")
        #     #     print(angle)
        #     # in_90 = angle % 90
        #     # copied_layer.changeAttributeValue(feat.id(), idx_angle, in_90)

        #     # first_edge = QgsGeometry.fromPolyline([geom.vertexAt(0), geom.vertexAt(1)])
        #     # first_edge_length = first_edge.length()
        #     # second_edge = QgsGeometry.fromPolyline([geom.vertexAt(1), geom.vertexAt(2)])
        #     # second_edge_length = second_edge.length()
        #     # if first_edge_length > second_edge_length:
        #     #     azi_angle = geom.vertexAt(0).azimuth(geom.vertexAt(1))
        #     # else:
        #     #     azi_angle = geom.vertexAt(1).azimuth(geom.vertexAt(2))
        #     # copied_layer.changeAttributeValue(feat.id(), idx_angle, azi_angle)

        #     # fet = QgsFeature()
        #     # fet.setGeometry(geom)
        #     # poly_layer_pr.addFeatures([fet])

    # copied_layer.commitChanges()

    # alg_parameters = {"INPUT": copied_layer, "OUTPUT": "memory:"}
    # centroids = processing.run("native:centroids", alg_parameters,)["OUTPUT"]

    # QgsProject.instance().addMapLayer(copied_layer)
    # QgsProject.instance().addMapLayer(centroids)

    # arrow_qml = "/home/pking/buildings_names_and_uses/orientation/orientation_style.qml"
    # centroids.loadNamedStyle(arrow_qml)
    # centroids.triggerRepaint()
    # copied_layer.setName("new_poly")
    # centroids.setName("new_point")

    poly_layer.updateExtents()
    QgsProject.instance().addMapLayer(poly_layer)
    poly_layer.setName("oriented_poly")


def new_azi_script2(layer, name):
    copied_layer = copy_layer(layer, "copied_layer")

    add_and_calc_field_id(copied_layer)

    alg_parameters = {"INPUT": copied_layer, "OUTPUT": "memory:"}
    centroids = processing.run("native:centroids", alg_parameters,)["OUTPUT"]

    # add an angle field
    centroids.dataProvider().addAttributes([QgsField("angle", QVariant.Double), QgsField("angle2", QVariant.Double), QgsField("radians", QVariant.Double)])
    
    centroids.updateFields()

    idx_uniqueID = copied_layer.fields().indexFromName("uniqueID")

    idx_angle = centroids.fields().indexFromName("angle")
    idx_angle2 = centroids.fields().indexFromName("angle2")
    idx_radians = centroids.fields().indexFromName("radians")

    line_layer = QgsVectorLayer("Linestring?crs=epsg:2193", "test_linestring", "memory")
    line_layer_pr = line_layer.dataProvider()

    orig_degree_layer = QgsVectorLayer("Linestring?crs=epsg:2193", "orig_degree_layer", "memory")
    orig_degree_layer_pr = orig_degree_layer.dataProvider()
    _360_degree_layer = QgsVectorLayer("Linestring?crs=epsg:2193", "_360_degree_layer", "memory")
    _360_degree_layer_pr = _360_degree_layer.dataProvider()
    mod_degree_layer = QgsVectorLayer("Linestring?crs=epsg:2193", "mod_degree_layer", "memory")
    mod_degree_layer_pr = mod_degree_layer.dataProvider()

    # for each poly find the longest edge
    for feature in copied_layer.getFeatures():
        # multi due to shapefile
        geom = feature.geometry()
        list_of_polygon, geom_type = get_polygon(geom)
        # print(geom_type)
        # print(len(multipolygon))
        # print(multipolygon)
        for polygons in list_of_polygon:
            polygon = polygons[0]

            longest_length = 0
            longest_start_node = 0
            # iterate through pairs ignoring last vertex
            # print(len(polygon))
            for n in range(0, len(polygon) - 1):
                # print(n)
                new_geom = QgsGeometry.fromPolylineXY([polygon[n], polygon[n + 1]])
                if new_geom.length() > longest_length:
                    longest_length = new_geom.length()
                    longest_start_node = n

            angle = geom.vertexAt(longest_start_node).azimuth(geom.vertexAt(longest_start_node + 1))

            # angle = angle % 90\
            angle2 = angle % 360
            # calculate building radians
            if angle == None or angle == 0:
                radian = 0
            else:
                radian = radians(angle)

            radian_360 = radians(360 - angle)
            angle_360 = degrees(radian_360)

            field = "uniqueID"
            attribute = float(feature.attributes()[idx_uniqueID])
            expr = QgsExpression("{} = {}".format(field, attribute))

            for feat in centroids.getFeatures(QgsFeatureRequest(expr)):
                attrs = {idx_angle: angle, idx_angle2: angle2, idx_radians: radian}
                fid = feat.id()
                if centroids.dataProvider().capabilities() & QgsVectorDataProvider.ChangeAttributeValues:
                    centroids.dataProvider().changeAttributeValues({fid: attrs})

            fet = QgsFeature()
            fet.setGeometry(
                QgsGeometry().fromPolyline([geom.vertexAt(longest_start_node), geom.vertexAt(longest_start_node + 1)])
            )
            line_layer_pr.addFeatures([fet])

            fet = QgsFeature()
            new_point = geom.vertexAt(longest_start_node).project(longest_length, angle)
            new_line = QgsGeometry().fromPolyline([geom.vertexAt(longest_start_node), new_point])
            fet.setGeometry(new_line)
            orig_degree_layer_pr.addFeatures([fet])

            fet = QgsFeature()
            new_point = geom.vertexAt(longest_start_node).project(longest_length, angle2)
            new_line = QgsGeometry().fromPolyline([geom.vertexAt(longest_start_node), new_point])
            fet.setGeometry(new_line)
            mod_degree_layer_pr.addFeatures([fet])

            fet = QgsFeature()
            new_point = geom.vertexAt(longest_start_node).project(longest_length, angle_360)
            new_line = QgsGeometry().fromPolyline([geom.vertexAt(longest_start_node), new_point])
            fet.setGeometry(new_line)
            _360_degree_layer_pr.addFeatures([fet])

    QgsProject.instance().addMapLayer(copied_layer)
    QgsProject.instance().addMapLayer(centroids)

    arrow_qml = "/home/pking/buildings_names_and_uses/orientation/orientation_style.qml"
    centroids.loadNamedStyle(arrow_qml)
    centroids.triggerRepaint()
    copied_layer.setName("new_poly")
    centroids.setName("new_point")

    line_layer.updateExtents()
    QgsProject.instance().addMapLayer(line_layer)
    line_layer.setName("longest_edge")

    orig_degree_layer.updateExtents()
    QgsProject.instance().addMapLayer(orig_degree_layer)
    orig_degree_layer.setName("orig degree")

    mod_degree_layer.updateExtents()
    QgsProject.instance().addMapLayer(mod_degree_layer)
    mod_degree_layer.setName("mod degree")

    _360_degree_layer.updateExtents()
    QgsProject.instance().addMapLayer(_360_degree_layer)
    _360_degree_layer.setName("360 degree")


# start_time = time.time()
# orig_azi_script(layer, "old_azi")
# print("--- %s seconds ---" % (time.time() - start_time))

# start_time = time.time()
# new_azi_script(layer, "new_azi")
# print("--- %s seconds ---" % (time.time() - start_time))

start_time = time.time()
new_azi_script2(layer, "new_azi")
print("--- %s seconds ---" % (time.time() - start_time))
