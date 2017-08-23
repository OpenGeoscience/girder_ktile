import os

from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import Resource, setResponseHeader, rawResponse
from girder.constants import AccessType

from TileStache import parseConfig, getTile
from ModestMaps.Core import Coordinate


class kTile(Resource):
    def __init__(self):
        super(kTile, self).__init__()
        self.resourceName = 'ktile'

        self.route('GET', (':id', ':z', ':x', ':y'), self.getTile)

    def _getLayer(self, girder_file):
        layer_name = os.path.splitext(girder_file['name'])[0]
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
                        "kwargs": {"file": girder_file}
                    },
                    "projection": "spherical mercator"
                }
            }
        }
        config = parseConfig(config_dict)
        layer = config.layers[layer_name]

        return layer


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
