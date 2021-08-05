import gdal
import os
from shutil import rmtree

"""
2017600 - 2020000 = 2400
5676000 - 5679600 = 3600
2 x 3 pixel == 1200 resolution

gdalwarp -tr 1200.0 1200.0 -r near -of GTiff /home/file_name.tif /tmp/processing_folder/OUTPUT.tif

"""

#warp_command = 'gdalwarp -q -cutline "{}" "{}" "{}" -dstnodata 255 -co compress=lzw'.format(tiled_extent_file, rescale_file, nodata_dst)

# def get_filename_from_path(filepath):
#     return os.path.splitext(os.path.basename(filepath))[0]

# input_dir = "/home/tifs"

# output_dir = "/home/shrunk_tifs"

# if os.path.isdir(output_dir):
#     rmtree(output_dir)
# os.makedirs(output_dir)

# for dir_path, subdirs, files in os.walk(input_dir):
#     for file in files:
#         print(os.path.splitext(file))
#         ext = os.path.splitext(file)[-1].lower()
#         if ext == '.tif':
#             filename = get_filename_from_path(file)
#             input_path = os.path.join(dir_path, "{}.tif".format(filename))
#             output_path = os.path.join(output_dir, "{}.tif".format(filename))
#             warp_command = 'gdalwarp -tr 1200.0 1200.0 -r near -of GTiff "{}" "{}"'.format(input_path, output_path)
#             os.system(warp_command)

filepath = "/home/imagery/file_name.tif"
filename = "blah"
subdir_path = "/home/imagery/folder"
exterior_extent_file = os.path.join(subdir_path, "dissolved_clip_exterior_extent", "shp_name.shp")
rescale_file = os.path.join(subdir_path, "temp", "rescale_{}.tif".format(filename))

def clip_to_extent(filepath, filename, subdir_path, exterior_extent_file, rescale_file):
    # create individual tile extent by clipping exterior extent to tif
    gdal_src = gdal.Open(filepath)
    ulx, xres, xskew, uly, yskew, yres  = gdal_src.GetGeoTransform()
    lrx = ulx + (gdal_src.RasterXSize * xres)
    lry = uly + (gdal_src.RasterYSize * yres)
    extent = '{0} {1} {2} {3}'.format(ulx, lry, lrx, uly)

    # print("extent {}".format(extent))
    subdir_path = "/home/imagery/test_output_just_clip"
    tiled_extent_file = os.path.join(subdir_path, "temp", "poly_no_hole_{}.shp".format(filename))

    # -nlt POLYGON -skipfailures is specifies that the output of tile_extent command must be a polygon
    # and to skip any failures or non-polygon features created
    # this fixes the bug where line slivers are created when vertices exactly match up
    tile_extent_command = 'ogr2ogr {} {} -clipsrc {} -nlt POLYGON -skipfailures'.format(tiled_extent_file, exterior_extent_file, extent)
    tile_extent_command = 'ogr2ogr {} {} -clipsrc {}'.format(tiled_extent_file, exterior_extent_file, extent)
    os.system(tile_extent_command)

    # use mask to set no data             
    nodata_dst = os.path.join(subdir_path, "clipped_tif", "{}.tif".format(filename))
    warp_command = 'gdalwarp -q -cutline "{}" "{}" "{}" -dstnodata 255 -co compress=lzw'.format(tiled_extent_file, rescale_file, nodata_dst)
    os.system(warp_command)

clip_to_extent(filepath, filename, subdir_path, exterior_extent_file, rescale_file)


"""
error from actual failure
ERROR 1: Attempt to write non-polygon (LINESTRING) geometry to POLYGON type shapefile.
ERROR 1: Unable to write feature 0 from layer GisborneTest_exterior_extent.
ERROR 1: Terminating translation prematurely after failed
translation of layer GisborneTest_exterior_extent (use -skipfailures to skip errors)
ERROR 1: Did not get any cutline features.

error when use old poly to cut shrunk features
ERROR 1: Attempt to write non-polygon (LINESTRING) geometry to POLYGON type shapefile.
ERROR 1: Unable to write feature 0 from layer GisborneTest_exterior_extent.
ERROR 1: Terminating translation prematurely after failed
translation of layer GisborneTest_exterior_extent (use -skipfailures to skip errors)
ERROR 1: Did not get any cutline features.
""
