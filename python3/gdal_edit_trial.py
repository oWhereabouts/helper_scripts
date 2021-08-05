import json
import os
from osgeo import gdal
from osgeo import osr
from subprocess import PIPE, Popen

def create_gtiff(outfn, band_count = 1, no_data: int = 255, xres = 1200, yres = 1200, epsg = 2193):
    driver = gdal.GetDriverByName('GTiff')

    spatref = osr.SpatialReference()
    spatref.ImportFromEPSG(epsg)
    wkt = spatref.ExportToWkt()

    xmin = 2020000
    xmax = 2022400
    ymin = 5679600
    ymax = 5676000
    dtype = gdal.GDT_Byte

    xsize = abs(int((xmax - xmin) / xres))
    ysize = abs(int((ymax - ymin) / yres))

    ds = driver.Create(outfn, xsize, ysize, band_count, dtype, options=['COMPRESS=LZW', 'TILED=YES'])
    ds.SetProjection(wkt)
    ds.SetGeoTransform([xmin, xres, 0, ymax, 0, yres])
    for n in range(1, band_count+1):
        ds.GetRasterBand(n).Fill(125)
        if no_data:
            ds.GetRasterBand(n).SetNoDataValue(no_data)
    ds.FlushCache()
    ds = None

def print_color_int(filepath):


    gdalinfo_json_command = 'gdalinfo -mm -stats -json {}'.format(filepath)
    gdalinfo_json = json.loads(os.popen(gdalinfo_json_command).read())

    try:
        current_bands = gdalinfo_json['bands']

        print(current_bands)

        for n in range(len(current_bands)):
            colour_int = current_bands[n]['colorInterpretation']
            print(colour_int)
    except:
        print("colour int failed")


def create_colorint_tif(test_filepath):
    if not os.path.isfile(test_filepath):
        create_gtiff(test_filepath, band_count = 4)

    # print_color_int(test_filepath)

    gdaledit_command = 'gdal_edit.py -colorinterp_1 gray -colorinterp_2 gray -colorinterp_3 gray "{}"'.format(test_filepath)
    # gdaledit_command = 'gdal_edit.py -colorinterp_1 red -colorinterp_2 green -colorinterp_3 blue "{}"'.format(test_filepath)
    gdaledit_command = 'gdal_edit.py -colorinterp_1 red -colorinterp_2 undefined -colorinterp_3 blue -colorinterp_4 green "{}"'.format(test_filepath)

    # colorinterp_X red|green|blue|alpha|gray|undefined

    # os.system(gdaledit_command)

    subprocess_command = Popen(gdaledit_command, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)

    output, error  = subprocess_command.communicate()
    subprocess_error = error.decode("utf-8")
    print(subprocess_error)

    # print_color_int(test_filepath)

def check_color_interpretation(gdalinfo_json):
    band_colour_ints = ('Red', 'Green', 'Blue')
    band_colour_ints = {1:'Red', 2:'Green', 3:'Blue'}
    current_bands = gdalinfo_json['bands']

    missing_bands = []

    for n in range(len(current_bands)):
        colour_int = current_bands[n]['colorInterpretation']
        if n+1 in band_colour_ints.keys():
            if colour_int != band_colour_ints[n+1]:
                missing_bands.append("band {} {}".format(n+1, colour_int))
        else:
            missing_bands.append("band {} {}".format(n+1, colour_int))
    if missing_bands:
        missing_bands.sort()
        return "unexpected color interpretation bands; {}".format(', '.join(missing_bands))
    else:
        return False

test_filepath = "/home/pking/imagery/non_visual/test4/test4.tif"

# create_colorint_tif(test_filepath)

gdalinfo_json_command = 'gdalinfo -mm -stats -json {}'.format(test_filepath)
gdalinfo_json = json.loads(os.popen(gdalinfo_json_command).read())

errors = check_color_interpretation(gdalinfo_json)

print(errors)
