from qgis.core import *
from qgis.PyQt.QtCore import QVariant

line_layer = QgsVectorLayer(r"C:\Users\user\Downloads\Input_slope\Shapefiles\N0100110001GJ_slope_lines.shp", "lines", "ogr")
dem_layer = QgsRasterLayer(r"C:\Users\user\Downloads\Input_slope\N0100110001GJ_DEM_utm.tif", "DEM")

if not line_layer.isValid() or not dem_layer.isValid():
    raise Exception("Layer loading failed")

# Add fields if missing
provider = line_layer.dataProvider()
existing_fields = [f.name() for f in line_layer.fields()]
new_fields = []

for field in ["Z_start", "Z_end", "Length_m", "Slope"]:
    if field not in existing_fields:
        new_fields.append(QgsField(field, QVariant.Double))

if new_fields:
    provider.addAttributes(new_fields)
    line_layer.updateFields()

line_layer.startEditing()

for feat in line_layer.getFeatures():
    geom = feat.geometry()
    if not geom:
        continue

    line = geom.asPolyline() if not geom.isMultipart() else geom.asMultiPolyline()[0]
    if len(line) < 2:
        continue

    pt1 = QgsPointXY(line[0])
    pt2 = QgsPointXY(line[-1])

    z1 = dem_layer.dataProvider().identify(pt1, QgsRaster.IdentifyFormatValue).results().get(1)
    z2 = dem_layer.dataProvider().identify(pt2, QgsRaster.IdentifyFormatValue).results().get(1)

    L_m = geom.length()
    slope = abs(z2 - z1) / L_m if z1 is not None and z2 is not None and L_m > 0 else None

    feat.setAttribute("Z_start", z1)
    feat.setAttribute("Z_end", z2)
    feat.setAttribute("Length_m", L_m)
    feat.setAttribute("Slope", slope)
    line_layer.updateFeature(feat)

line_layer.commitChanges()
print("✅ Slope calculation completed with projected CRS")
