from qgis.core import QgsRasterLayer

# urlWithParams = 'url=http://irs.gis-lab.info/? layers=landsat&styles=&format=image/jpeg&crs=EPSG:4326'

# urlWithParams = 'url=https://data.linz.govt.nz/services;key=a_key/wmts/1.0.0/layer/51318/WMTSCapabilities.xml'

# rlayer = QgsRasterLayer(urlWithParams, 'some layer name', 'wms')
# if not rlayer.isValid():
#   print("Layer failed to load!")

# from imagery surveys plugin

from urllib.request import urlopen
from urllib.error import URLError
from owslib.wms import WebMapService
from owslib.wfs import WebFeatureService
from owslib.wmts import WebMapTileService
from qgis.core import QgsProject, QgsRasterLayer, QgsVectorLayer


class LDS(object):
    def __init__(self, api_key):
        self.api_key = api_key
        self.domain = "data.linz.govt.nz"
        self.service_versions = {"WFS": "2.0.0", "WMS": "1.1.1", "WMTS": "1.0.0"}

    def service_xml(self, service_type, service_version):
        if service_type == "WMTS":
            f = urlopen(
                "https://data.linz.govt.nz/services;key={0}/{1}/{2}/WMTSCapabilities.xml".format(
                    self.api_key, service_type.lower(), service_version
                )
            )
        else:
            f = urlopen(
                "https://data.linz.govt.nz/services;key={0}/{1}?service={2}&version={3}&request=GetCapabilities".format(
                    self.api_key, service_type.lower(), service_type, service_version
                )
            )
        return f.read()

    def service_obj(self, service_type, service_xml, service_version):
        if service_type == "WMS":
            return WebMapService(url=None, xml=service_xml, version=service_version)
        if service_type == "WMTS":
            return WebMapTileService(url=None, xml=service_xml, version=service_version)
        if service_type == "WFS":
            return WebFeatureService(url=None, xml=service_xml, version=service_version)

    def dataset_objs(self, service_type):
        service_xml = self.service_xml(service_type, self.service_versions[service_type])
        service_obj = self.service_obj(service_type, service_xml, self.service_versions[service_type])
        dataset_objs = []
        for item in service_obj.contents.items():
            dataset_objs.append(item[1])
        return dataset_objs

    def get_layer(self, service_type, layer_id, layer_title):
        if service_type == "WFS":
            url = (
                "https://{0}/services;"
                "key={1}/{2}?"
                "SERVICE={2}&"
                "VERSION={3}&"
                "REQUEST=GetFeature&"
                "TYPENAME={0}:{4}-{5}"
            ).format(self.domain, self.api_key, service_type.lower(), self.service_versions[service_type], "layer", layer_id)
            return QgsVectorLayer(url, layer_title, service_type)

        elif service_type == "WMTS":
            url = (
                "SmoothPixmapTransform=1"
                "&contextualWMSLegend=0"
                "&crs={1}&dpiMode=7&format=image/png"
                "&layers={2}-{3}&styles=style%3Dauto&tileMatrixSet={1}"
                "&url=https://{0}/services;"
                "key={4}/{5}/{6}/{2}/{3}/"
                "WMTSCapabilities.xml"
            ).format(
                self.domain,
                "EPSG:3857",
                "layer",
                layer_id,
                self.api_key,
                service_type.lower(),
                self.service_versions[service_type],
            )
            return QgsRasterLayer(url, layer_title, "wms")


lds = LDS('a_key')

layer = lds.get_layer(
    "WMTS", "51318", "Chart NZ 5323 Auckland Harbour West"
)
print(layer.isValid())

QgsProject.instance().addMapLayer(layer)
