import mapnik
from PIL import Image

from girder.utility.model_importer import ModelImporter


class MapnikProvider(object):
    def __init__(self, layer, **kwargs):
        pass

    def addStyle(self, mapnik_map, base, file):
        style = mapnik.Style()
        rule = mapnik.Rule()
        rule.symbols.append(mapnik.RasterSymbolizer())
        style.rules.append(rule)
        mapnik_map.append_style('Style', style)
        lyr = mapnik.Layer('Layer')
        lyr.srs = "+proj=cea +lon_0=-117.333333333333 +lat_ts=33.75 +x_0=0 +y_0=0 +datum=NAD27 +units=m +no_defs"
        lyr.datasource = mapnik.Gdal(base=base,
                                     file=file,
                                     band=-1)
        lyr.styles.append('Style')
        mapnik_map.layers.append(lyr)

    def getFilePath(self, itemId):
        item = ModelImporter.model('item').load(itemId, force=True)
        _file = list(ModelImporter.model('item').childFiles(item))[0]
        assetstore = ModelImporter.model('file').getAssetstoreAdapter(_file)
        path = assetstore.fullPath(_file)

        return path

    def renderArea(self, width, height, srs, xmin, ymin, xmax, ymax, zoom):
        mapnik_map = mapnik.Map(width, height, srs)

        mapnik_map.zoom_to_box(mapnik.Box2d(xmin, ymin, xmax, ymax))

        img = mapnik.Image(width, height)

        path = self.getFilePath('5988c9cc78e55a088e46c652')
        self.addStyle(mapnik_map, '', path)

        mapnik.render(mapnik_map, img)

        return Image.frombytes('RGBA', (width, height), img.tostring())
