"""
Takes a layer with features selected you wish to turn into points
a DEM layer, this has been modified to stretch the height so it is uint16
and has the values stretch so the fit the range 1 - 65535
This layer is loaded in blender so I used the pixel coords and height from this layer
when placing points in blender
And a colour layer, I saved a map along with a world file and imported back into
QGIS. This lets me find the colour under a point and then assign it to a light later.
Instead of a colour layer you coloud swap in the RGB vlaues for a colour you wish to use. 

The script iterates through each selected feature point in a layer, finds the raster cell
it sits above for the DEM and colour layer and saves the pixel coordinates of the DEM,
the height and RGB colours to a list.
The list is printed  and then copied to the start of the add_lights_blender.py script
and turned into an individual light in blender.

To use change the name of the pnt_layer, dem_lyr and colour_lyr to match the names in
you QGIS project. Open this script in the python console. Select the points you
wish to use in the point layer, and run the script.
"""

pnt_lyr = QgsProject.instance().mapLayersByName("pnt_layer_name")[-1]
dem_lyr = QgsProject.instance().mapLayersByName("dem_layer_name")[-1]
colour_lyr = QgsProject.instance().mapLayersByName("colour_layer_name")[-1]
list = []

for feature in pnt_lyr.selectedFeatures():
    point = feature.geometry().asPoint()
    ident = dem_lyr.dataProvider().identify(point, QgsRaster.IdentifyFormatValue)

    width = dem_lyr.width()
    height = dem_lyr.height()

    xsize = dem_lyr.rasterUnitsPerPixelX()
    ysize = dem_lyr.rasterUnitsPerPixelY()

    extent = dem_lyr.extent()

    ymax = extent.yMaximum()
    xmin = extent.xMinimum()

    # row in pixel coordinates
    row = int(((ymax - point.y()) / ysize) + 1)

    # column in pixel coordinates
    column = int(((point.x() - xmin) / xsize) + 1)

    height = ident.results()[1]
    colour_ident = colour_lyr.dataProvider().identify(point, QgsRaster.IdentifyFormatValue)

    # I'm not sure why it is column/ 500 -6.6, the dimensions of my dem is 6600 x 6600
    list.append(
        (
            (column / 500 - 6.6, (row / 500 - 6.6) * -1, height),
            colour_ident.results()[1],
            colour_ident.results()[2],
            colour_ident.results()[3],
        )
    )

print(list)
