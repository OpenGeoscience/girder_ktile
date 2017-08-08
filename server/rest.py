from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import Resource, setResponseHeader, rawResponse

from TileStache import parseConfig, getTile
from ModestMaps.Core import Coordinate

xml_config = {
    "cache":
    {
        "name": "Test",
        "path": "/tmp/stache",
        "umask": "0000"
    },
    "layers":
    {
        "osm":
        {
            "provider": {"name": "proxy", "provider": "OPENSTREETMAP"},
            "png options": {"palette": "http://tilestache.org/example-palette-openstreetmap-mapnik.act"}
        },
        "geotiff":
        {
            "provider":
            {
                "class": "girder.plugins.girder_ktile.provider:MapnikProvider"
            },
            "projection": "spherical mercator"
        }
    }
}

class kTile(Resource):
    def __init__(self):
        super(kTile, self).__init__()
        self.resourceName = 'ktile'

        self.route('GET', (':layer', ':z', ':x', ':y'), self.getTile)

    @access.public
    @rawResponse
    @autoDescribeRoute(
        Description('A tile based on a z, x, y')
        .param('layer', 'Layer name in the config file', paramType='path')
        .param('z', 'Zoom level', paramType='path')
        .param('x', 'X Coordinate', paramType='path')
        .param('y', 'Y Coordinate', paramType='path')
    )
    def getTile(self, layer, z, x, y, params):
        coordinates = Coordinate(int(y), int(x), int(z))
        config = parseConfig(xml_config)
        layer = config.layers[layer]
        status_code, headers, tile = layer.getTileResponse(coordinates, 'png')
        setResponseHeader('Content-Type', headers.values()[0])
        return tile
