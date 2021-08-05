from PyQt4.QtGui import QColor

colours = ('#440154', '#482475', '#404387', '#345f8d', '#29788e', '#20908d', '#22a884', '#43bf70', '#7ad251', '#bcdf27', '#fde725')

for colour_hex in colours:
    colour = QColor(colour_hex)
    colour.setHsl(colour.hue(), colour.saturation() - 20, colour.lightness())
    print colour.name()

#410350
#461d7b
#363b8f
#2b5e95
#217c95
#1a9692
#1cae85
#39c96b
#7ecd57
#bee026
#e7d33b
