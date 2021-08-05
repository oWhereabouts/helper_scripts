

layer = iface.activeLayer()
true_multi_count = 0
single_count = 0
print("layer is {}".format(QgsWkbTypes.displayString(int(layer.wkbType()))))
for feature in layer.getFeatures():
    length = len(feature.geometry().asGeometryCollection())
    if length > 1:
        true_multi_count += 1
    elif length == 1:
        single_count += 1
print("true multi count {}".format(true_multi_count))
print("single multi count {}".format(single_count))