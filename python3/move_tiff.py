import os
from shutil import copyfile

rootdir = '/folder/with_tiffs'
fontdir = '/save_location'

if not os.path.isdir(fontdir):
    os.mkdir(fontdir)


extensions = ('.tif', '.tfw')

for subdir, dirs, files in os.walk(rootdir):
    for file in files:
        ext = os.path.splitext(file)[-1].lower()
        if ext in extensions:
            filename = os.path.basename(file)
            dst = os.path.join(fontdir, file)
            src = os.path.join(subdir, file)
            if not os.path.isfile(dst):
                copyfile(src, dst)