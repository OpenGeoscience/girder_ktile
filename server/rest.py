import os

from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import Resource, setResponseHeader, rawResponse
from girder.constants import AccessType
from girder.utility.model_importer import ModelImporter


import gdal
import osr
from TileStache import parseConfig, getTile
from ModestMaps.Core import Coordinate


class kTile(Resource):
    def __init__(self):
        super(kTile, self).__init__()
        self.resourceName = 'ktile'

        self.route('GET', (':id', ':z', ':x', ':y'), self.getTile)
        self.route('GET', (':id', 'info'), self.getTiffInfo)

    def _getLayer(self, girder_file):
        layer_name = os.path.splitext(girder_file['name'])[0]
        info = kTile._getInfo(girder_file)
        config_dict = {
            "cache":
            {
                "name": "Test",
                "path": "/tmp/stache",
                "umask": "0000"
            },
            "layers":
            {
                "{}".format(layer_name):
                {
                    "provider":
                    {
                        "class": "girder.plugins.girder_ktile.provider:MapnikProvider",
                        "kwargs": {"file": girder_file,
                                   "info": info}
                    },
                    "projection": "spherical mercator"
                }
            }
        }
        config = parseConfig(config_dict)
        layer = config.layers[layer_name]

        return layer

    @staticmethod
    def _getInfo(file):
        info = {}
        assetstore_model = ModelImporter.model('assetstore')
        assetstore = assetstore_model.load(file['assetstoreId'])
        path = os.path.join(assetstore['root'], file['path'])
        dataset = gdal.Open(path)
        geotransform = dataset.GetGeoTransform()
        wkt = dataset.GetProjection()
        proj = osr.SpatialReference()
        proj.ImportFromWkt(wkt)
        lrx = geotransform[0] + (dataset.RasterXSize * geotransform[1])
        lry = geotransform[3] + (dataset.RasterYSize * geotransform[5])
        info['path'] = path
        info['driver'] = dataset.GetDriver().GetDescription()
        info['pixel_size'] = geotransform[1], geotransform[5]
        info['srs'] = proj.ExportToProj4()
        info['size'] = dataset.RasterXSize, dataset.RasterYSize
        info['bands'] = dataset.RasterCount
        info['corners'] = {'ulx': geotransform[0],
                           'uly': geotransform[3],
                           'lrx': lrx,
                           'lry': lry}
        return info


    @access.public
    @rawResponse
    @autoDescribeRoute(
        Description('A tile based on a z, x, y')
        .modelParam('id', 'The ID of the file to be visualized.',
                    model='file', level=AccessType.READ)
        .param('z', 'Zoom level', paramType='path')
        .param('x', 'X Coordinate', paramType='path')
        .param('y', 'Y Coordinate', paramType='path')
    )
    def getTile(self, file, z, x, y, params):
        coordinates = Coordinate(int(y), int(x), int(z))
        layer = self._getLayer(file)
        status_code, headers, tile = layer.getTileResponse(coordinates, 'png')
        setResponseHeader('Content-Type', headers.values()[0])
        return tile

    @access.public
    @autoDescribeRoute(
        Description('Get information about a tiff file')
        .modelParam('id', 'The ID of the file to be inspected.',
                    model='file', level=AccessType.READ)
    )
    def getTiffInfo(self, file, params):
        return kTile._getInfo(file)
