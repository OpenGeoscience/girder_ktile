import gdal
import mapnik
import osr
import os
from PIL import Image

from girder.utility.model_importer import ModelImporter


class MapnikProvider(object):
    def __init__(self, layer, **kwargs):
        self.girder_file = kwargs['file']

    def getAssetStorePath(self):

        assetstore_model = ModelImporter.model('assetstore')
        assetstore = assetstore_model.load(self.girder_file['assetstoreId'])
        return assetstore['root']

    def getLayerProjection(self):
        file_path = os.path.join(self.getAssetStorePath(), self.girder_file['path'])
        dataset = gdal.Open(file_path)
        wkt = dataset.GetProjection()
        proj = osr.SpatialReference()
        proj.ImportFromWkt(wkt)
        return proj.ExportToProj4()

    def addStyle(self, m, file):
        style = mapnik.Style()
        rule = mapnik.Rule()
        rule.symbols.append(mapnik.RasterSymbolizer())
        style.rules.append(rule)
        m.append_style('Raster Style', style)
        lyr = mapnik.Layer('GDAL Layer from TIFF file')
        lyr.srs = self.getLayerProjection()
        lyr.datasource = mapnik.Gdal(base=self.getAssetStorePath(),
                                     file=file,
                                     band=-1)
        lyr.styles.append('Raster Style')
        m.layers.append(lyr)

    def renderArea(self, width, height, srs, xmin, ymin, xmax, ymax, zoom):
        mapnik_map = mapnik.Map(width, height, srs)

        mapnik_map.zoom_to_box(mapnik.Box2d(xmin, ymin, xmax, ymax))

        img = mapnik.Image(width, height)

        self.addStyle(mapnik_map, self.girder_file['path'])

        mapnik.render(mapnik_map, img)

        return Image.frombytes('RGBA', (width, height), img.tostring())
