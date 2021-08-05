import bpy

# script for blender 2.79

scene = bpy.context.scene

# coords with stretched height
coords = [
    (("column", "row", "stretched_height"), "red", "green", "blue"),
    ((2.378, -1.308, 52574.0), 48.0, 139.0, 186.0),
]

for coord in coords:
    # Create new lamp datablock
    lamp_data = bpy.data.lamps.new(name="New Lamp", type="POINT")

    # Create new object with our lamp datablock
    lamp_object = bpy.data.objects.new(name="New Lamp", object_data=lamp_data)

    # Link lamp object to the scene so it'll appear in this scene
    scene.objects.link(lamp_object)

    # Place lamp to a specified location
    lamp_object.location = coord[0]
    # dividing by 65535 which is my maximum height, adding 0.2 to raise it higher
    # and to make the light slightly less harsh
    height = (coord[0][2] / 65535) + 0.2
    lamp_object.location[2] = height

    # set the strength
    lamp_object.data.use_nodes = True
    lamp_object.data.node_tree.nodes["Emission"].inputs["Strength"].default_value = 0.5
    r = coord[1] / 255
    g = coord[2] / 255
    b = coord[3] / 255
    lamp_object.data.node_tree.nodes["Emission"].inputs["Color"].default_value = (r, g, b, 1)
    # the yellow light was brighter than blue so reduce the strength of these lights
    if r > 0.8:
        lamp_object.data.node_tree.nodes["Emission"].inputs["Strength"].default_value = 0.4

    # And finally select it make active
    lamp_object.select = True
    scene.objects.active = lamp_object
