# get layers

# make sure polygons have spatial index

# for each MoH school
# limit 10
# buffer geom, square buff for speed?
# find intersecting polygons which have feature_type = school
# make list of names
# strip MoH school name
# match/ fuzzy match
# create output
# school fields, poly geom, poly name, id, feature group, date modified
from fuzzywuzzy import process
import pandas as pd

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsFeature,
    QgsFeatureRequest,
    QgsField,
    QgsProject,
    QgsSpatialIndex,
    QgsVectorLayer
)
from qgis.PyQt.QtCore import QVariant

import time


startTime = time.time()

def add_feature(
        match_type,
        possible_feature_count,
        feature_ids,
        point_feature,
        poly_layer,
        poly_attributes,
        output_layer
    ):
    # expression = '"NAME" = \'{}\''.format(name)
    # request = QgsFeatureRequest().setFilterExpression(expression)
    request = QgsFeatureRequest().setFilterFids(feature_ids)
    for poly_feature in poly_layer.getFeatures(request):
        # change to 2193
        geom = poly_feature.geometry()
        sourceCrs = poly_layer.sourceCrs()
        destCrs = QgsCoordinateReferenceSystem(2193)
        tr = QgsCoordinateTransform(sourceCrs, destCrs, QgsProject.instance())
        geom.transform(tr)

        attributes = []
        attributes.append(match_type)
        attributes.append(possible_feature_count)

        for poly_attribute in poly_attributes:
            attribute = poly_feature[poly_attribute]
            attributes.append(attribute)
        attributes.extend(point_feature.attributes())

        fet = QgsFeature()
        fet.setGeometry(geom)
        fet.setAttributes(attributes)
        output_layer.dataProvider().addFeature(fet)
        output_layer.updateExtents()

def add_unmatched(text, possible_feature_count,  feature, input_crs, output_layer):
    fet = QgsFeature()
    # geometry = get_buffered_point(feature.geometry(), input_crs, 1)
    feat_attributes = feature.attributes()
    attributes = [text, possible_feature_count, None, '', None, None]
    attributes.extend(feat_attributes)

    # convert geom to 2193
    geometry = feature.geometry()
    destCrs = QgsCoordinateReferenceSystem(2193)
    tr = QgsCoordinateTransform(input_crs, destCrs, QgsProject.instance())
    geometry.transform(tr)
    geometry = geometry.buffer(100, 5)

    fet.setGeometry(geometry)
    fet.setAttributes(attributes)
    output_layer.dataProvider().addFeature(fet)
    output_layer.updateExtents()

def count_categories(output_layer):
    match_types = ("direct_match", "fuzzy_match", "spatial_match", "unmatched")
    for match_type in match_types:
        output_layer.selectByExpression( '"match_type"=\'{}\''.format(match_type) )
        count = output_layer.selectedFeatureCount()
        print("{} {}".format(match_type, count))
        output_layer.removeSelection()

def create_output(point_layer, polygon_layer, polygon_attributes, name, output_path = "memory"):

    output_layer = QgsVectorLayer("Polygon?crs=epsg:2193", name, output_path)
    output_layer_pr = output_layer.dataProvider()

    MSch_fields = point_layer.dataProvider().fields().toList()
    NMPoly_fields = polygon_layer.dataProvider().fields()
    attributeList = []
    # add match type
    attributeList.append(QgsField("match_type", QVariant.String))
    attributeList.append(QgsField("count", QVariant.String))

    # add national map attributes
    for NMPoly_attribute in polygon_attributes:
        NMPoly_field = NMPoly_fields.field(NMPoly_fields.indexFromName(NMPoly_attribute))
        attributeList.append(NMPoly_field)

    # add features attributes
    for field in MSch_fields:
        attributeList.append(field)

    output_layer.dataProvider().addAttributes(attributeList)
    output_layer.updateFields()

    return output_layer

def get_buffered_point(geometry, input_crs, buffer_distance):
    destCrs = QgsCoordinateReferenceSystem(2193)
    tr = QgsCoordinateTransform(input_crs, destCrs, QgsProject.instance())
    geometry.transform(tr)
    geometry = geometry.buffer(buffer_distance, 5)
    tr = QgsCoordinateTransform(destCrs, input_crs, QgsProject.instance())
    geometry.transform(tr)

    return geometry

def get_fuzzy_match(name_to_match, names_dict, is_school):
    # tidy up
    names_list = names_dict.keys()
    if is_school:
        stripped_name_to_match = strip_school(name_to_match)
    else:
        stripped_name_to_match = name_to_match
    matched_names = []
    # for name in names_list:
    #     stripped_name = strip_school(name)
    #     ratios = process.extract(stripped_name_to_match,[stripped_name])
    #     score = ratios[0][1]
    #     if score > 90:
    #         matched_names.append((score, name))
    matched_names = process.extract(stripped_name_to_match,names_list)

    if matched_names:
        # matched_names.sort()
        if matched_names[0][1] > 80:
            matched_name = matched_names[0][0]
            matched_feature_ids = names_dict[matched_name]
            return matched_feature_ids
        else:
            return False
    else:
        return False

def get_input_variables(facility_type):
    if facility_type == 'school':
        buffer_distance = 1000
        polygon_attributes = ("UNIQUE_ID", "NAME", "FEATURE_GROUP", "DATE_MODIFIED")

        # MoE schools
        point_layer = QgsProject.instance().mapLayersByName("schools_30_3_21")[-1]

        # National map polygons
        polygon_layer = QgsProject.instance().mapLayersByName("Landuse LANDUSE")[-1]

        expression = '"FEATURE_TYPE" = \'School\''
        point_layer_field = 'School Name'
        output_name = 'matched_school_polygon'
        point_request = None
    elif facility_type == 'hospital':
        buffer_distance = 1000
        polygon_attributes = ("UNIQUE_ID", "NAME", "FEATURE_GROUP", "DATE_MODIFIED")

        # MoE schools
        point_layer = QgsProject.instance().mapLayersByName("Certified_Premises_joined_4167")[-1]

        # National map polygons
        polygon_layer = QgsProject.instance().mapLayersByName("Landuse LANDUSE")[-1]

        expression = '"FEATURE_TYPE" in ( \'Clinic\',  \'Hospice\',  \'Hospital\' )'
        point_layer_field = 'Premises Name'
        output_name = 'matched_hospital_polygon'

        point_expression = '"Certification Service Type" != \'Aged Care\''
        point_request = QgsFeatureRequest().setFilterExpression(point_expression)
    return (buffer_distance, 
            polygon_attributes, 
            point_layer, 
            polygon_layer, 
            expression, 
            point_layer_field, 
            output_name, 
            point_request
    )

def get_intersection_match(feature, polygon_layer, names_dict):
    intersection_match_ids = []
    geom = feature.geometry()
    feature_ids = []
    for id_list in names_dict.values():
        feature_ids.extend(id_list)
    request = QgsFeatureRequest().setFilterFids(feature_ids)
    for poly_feature in polygon_layer.getFeatures(request):
        if poly_feature.geometry().intersects(geom):
            intersection_match_ids.append(poly_feature.id())
    return intersection_match_ids

def strip_school(text):
    # seperates on ( as some schools have (location) after the school name
    sep = ' ('
    stripped = text.split(sep, 1)[0]
    return stripped

facility_type = 'school'
facility_type = 'hospital'
(
    buffer_distance, 
    polygon_attributes, 
    point_layer, 
    polygon_layer, 
    expression, 
    point_layer_field,
    output_name,
    point_request
) = get_input_variables(facility_type)

request = QgsFeatureRequest().setLimit(100)

print("the expression {}".format(expression))

nm_request = QgsFeatureRequest().setFilterExpression(expression)
index = QgsSpatialIndex(polygon_layer.getFeatures(nm_request))
# print("index ref {}".format(index.refs()))
polygon_layer.selectByExpression( expression )
count = polygon_layer.selectedFeatureCount()
print("poly in index {}".format(count))
polygon_layer.removeSelection()

output_layer = create_output(point_layer, polygon_layer, polygon_attributes, output_name)

input_crs = point_layer.sourceCrs()

if point_request:
    iter = point_layer.getFeatures(point_request)
else:
    iter = point_layer.getFeatures()
# count = 0
for feature in iter:
    # count+=1
    # possible_matches = []
    # possible_matches_dict = {}
    possible_matches = {}
    point_name = feature[point_layer_field]

    # find polygons schools within buffer_distance
    point = get_buffered_point(feature.geometry(), input_crs, buffer_distance)
    rectangle = point.boundingBox()

    intersect_ids = index.intersects(rectangle)
    # if count <10:
    #     print(intersect_ids)
    #     print("rect area = {}".format(rectangle.area()))
    for poly_feature in polygon_layer.getFeatures(QgsFeatureRequest().setFilterFids(intersect_ids)):
        if poly_feature['NAME'] in possible_matches:
            possible_matches[poly_feature['NAME']].append(poly_feature.id())
        else:
            possible_matches[poly_feature['NAME']] = [poly_feature.id()]
        # possible_matches.append(poly_feature['NAME'])
        # if feature.id() in possible_matches_dict:
        #     possible_matches_dict[feature.id()].append(poly_feature['NAME'))
        # else:
        #     possible_matches_dict[feature.id()] = [poly_feature['NAME')]


    # need the feature id incase of dupliicate nm names in different parts of the country

    # print("{} matched {}".format(feature['School Name'], len(possible_matches)))

    # for name in possible_matches:
    #     add_feature(name, feature, NMPoly_layer, polygon_attributes, output_layer)

    if point_name in possible_matches:
        matched_feature_ids = possible_matches[point_name]
        add_feature("direct_match", len(possible_matches), matched_feature_ids, feature, polygon_layer, polygon_attributes, output_layer)
    else:
        if facility_type == 'school':
            is_school = True
        else:
            is_school = False
        matched_feature_ids = get_fuzzy_match(point_name, possible_matches, is_school )
        if matched_feature_ids:
            matched_feature_ids = list(set(matched_feature_ids))
            add_feature("fuzzy_match", len(possible_matches), matched_feature_ids, feature, polygon_layer, polygon_attributes, output_layer)        
        else:
            intersect_feature_ids = get_intersection_match(feature, polygon_layer, possible_matches)
            if intersect_feature_ids:
                intersect_feature_ids = list(set(intersect_feature_ids))
                add_feature("spatial_match", len(possible_matches), intersect_feature_ids, feature, polygon_layer, polygon_attributes, output_layer)
            else:
                add_unmatched("unmatched", len(possible_matches), feature, input_crs, output_layer)

QgsProject.instance().addMapLayer(output_layer)

# print("featured queries {}".format(count))

count_categories(output_layer)

executionTime = (time.time() - startTime)
print('Execution time in seconds: ' + str(executionTime))
