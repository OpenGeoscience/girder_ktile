import os

from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import Resource, setResponseHeader, rawResponse
from girder.constants import AccessType

from ModestMaps.Core import Coordinate

from girder.plugins.girder_ktile.util import getInfo, getLayer

class kTile(Resource):
    def __init__(self):
        super(kTile, self).__init__()
        self.resourceName = 'ktile'
        self.route('GET', (':id', ':z', ':x', ':y',), self.getTile)
        self.route('GET', (':id', 'info'), self.getTiffInfo)

    @access.public
    @access.cookie
    @rawResponse
    @autoDescribeRoute(
        Description('A tile based on a z, x, y')
        .modelParam('id', 'The ID of the file to be visualized.',
                    model='file', level=AccessType.READ)
        .param('z', 'Zoom level', paramType='path')
        .param('x', 'X Coordinate', paramType='path')
        .param('y', 'Y Coordinate', paramType='path')
        .param('band', 'Band number to be visualized',
               default=-1, paramType='query')
        .param('minimum', 'Minimum value for the band',
               default='0', paramType='query')
        .param('maximum', 'Maximum value for the band',
               default='256', paramType='query')
        .param('palette', 'Palette from given source',
               default='cmocean.diverging.Curl_10', paramType='query')
    )
    def getTile(self, file, z, x, y, params):
        coordinates = Coordinate(int(y), int(x), int(z))
        band = params['band']
        palette = params['palette']
        layer = getLayer(file, band, params['minimum'],
                         params['maximum'], palette)
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
        return getInfo(file)
