import os

path = "/home/folder/gpkg_file.gpkg"

ogr_info_command = 'ogrinfo -al -so {}'.format(path)
os.system(ogr_info_command)
