from qgis.core import (
    QgsCategorizedSymbolRenderer,
    QgsFillSymbol,
    QgsPalLayerSettings,
    QgsProject,
    QgsRendererCategory,
    QgsSymbol,
    QgsTextBufferSettings,
    QgsTextFormat,
    QgsVectorLayerSimpleLabeling,
)
from qgis.PyQt.QtGui import QColor, QFont
from qgis.utils import iface

layer_to_style = QgsProject.instance().mapLayersByName("error_layer_test")[-1]

# Create dictionary to store
# 'attribute value' : ('symbol colour', 'legend name')
land_class = {
    "Unassigned use": ("#a20a0a", "Unassigned use"),
    "New use assigned": ("#0aa245", "New use assigned"),
    "Use or status has changed": ("#999999", "Use or status has changed"),
}
# Create list to store symbology properties
categories = []
# Iterate through the dictionary
for classes, (colour, label) in land_class.items():
    # Automatically set symbols based on layer's geometry
    # symbol = QgsSymbol.defaultSymbol(current_layer.geometryType())
    # Set colour
    # symbol.setColor(QColor(color))
    symbol = QgsFillSymbol.createSimple(
        {"color": "0,0,0,0", "color_border": colour, "width_border": "0.66"}
    )
    # Set the renderer properties
    category = QgsRendererCategory(classes, symbol, label)
    categories.append(category)

# Field name
expression = "new_error_categories"
# Set the categorized renderer
renderer = QgsCategorizedSymbolRenderer(expression, categories)
layer_to_style.setRenderer(renderer)
# Refresh layer
layer_to_style.triggerRepaint()

layer_settings = QgsPalLayerSettings()
text_format = QgsTextFormat()

text_format.setFont(QFont("Arial", 12))
text_format.setSize(12)
text_format.setColor(QColor("black"))

buffer_settings = QgsTextBufferSettings()
buffer_settings.setEnabled(True)
buffer_settings.setSize(1)
buffer_settings.setColor(QColor("white"))

text_format.setBuffer(buffer_settings)
layer_settings.setFormat(text_format)
# layer_settings.isExpression = True
# layer_settings.fieldName = "coalesce(\"name\",'') || '\n' || coalesce(\"use\",'')"
layer_settings.fieldName = "new_error_categories"
layer_settings.placement = 1

layer_settings.enabled = True

layer_settings = QgsVectorLayerSimpleLabeling(layer_settings)
layer_to_style.setLabelsEnabled(True)
layer_to_style.setLabeling(layer_settings)
layer_to_style.triggerRepaint()
iface.layerTreeView().refreshLayerSymbology(layer_to_style.id())
print("got here")
