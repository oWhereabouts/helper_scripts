# scripts for finding and using processing algs


import processing

# find an alg
for alg in QgsApplication.processingRegistry().algorithms():
    print(alg.id(), "->", alg.displayName())


def alglist(search_term: str = False):
    s = ""
    for alg in QgsApplication.processingRegistry().algorithms():
        if search_term:
            if search_term.lower() in alg.displayName().lower():
                s += "{}->{}\n".format(alg.id(), alg.displayName())
        else:
            s += "{}->{}\n".format(alg.id(), alg.displayName())
            # l = alg.displayName().ljust(50, "-")
            # r = alg.id()
            # s += '{}--->{}\n'.format(l, r)
    print(s)


alglist("")

# if you run the alg in qgis in the log you can see the inputs


# {
#     "DATA_TYPE": 0,
#     "INPUT": "/home/pking/simplify/qa/s_drive/Imagery/Topo50 shts - Current Imagery/New Zealand Mainland/BR26.ecw",
#     "NODATA": None,
#     "OPTIONS": "",
#     "OUTPUT": "/tmp/processing_cab/OUTPUT.tif",
#     "PROJWIN": "1084000.000000001,2092000.000000001,4722000.000000001,6234000.000000001 [EPSG:2193]",
# }
# alglist("dissolve")

# processing.run("saga:polygondissolveallpolygons"
# processing.run("native:difference
# processing.run("native:extenttolayer"
# processing.run("native:multiparttosingleparts

# processing.algorithmHelp("native:dissolve")

# alglist("intersect")

# processing.algorithmHelp("native:intersection")

# dissolve = processing.run("native:dissolve", {"INPUT": layer, "FIELD": [], "OUTPUT": "memory:"})["OUTPUT"]

# intersection = processing.run(
#     "native:intersection",
#     {
#         "INPUT": grid2line_layer,
#         "INPUT_FIELDS": [],
#         "OUTPUT": "memory:",
#         "OVERLAY": dissolve,
#         "OVERLAY_FIELDS": [],
#         "OVERLAY_FIELDS_PREFIX": "",
#     },
# )["OUTPUT"]


# alglist("symmetrical")
# alglist("difference")
# native:difference

alglist("service")
