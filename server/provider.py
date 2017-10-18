import mapnik
from PIL import Image


class MapnikProvider(object):
    def __init__(self, layer, **kwargs):
        self.info = kwargs['info']
        self.band = kwargs['band']
        self.style = kwargs['style']

    def addStyle(self, m):
        style = mapnik.Style()
        rule = mapnik.Rule()
        sym = mapnik.RasterSymbolizer()

        if self.band != '-1':
            colorizer = mapnik.RasterColorizer(
                mapnik.COLORIZER_DISCRETE,
                mapnik.Color('white')
            )
            for color, value in self.style:
                colorizer.add_stop(value, mapnik.Color(color))
            sym.colorizer = colorizer

        rule.symbols.append(sym)
        style.rules.append(rule)
        m.append_style('Raster Style', style)
        lyr = mapnik.Layer('GDAL Layer from TIFF file')
        lyr.srs = self.info['srs']
        lyr.datasource = mapnik.Gdal(base='',
                                     file=self.info['path'],
                                     band=self.band)
        lyr.styles.append('Raster Style')
        m.layers.append(lyr)

    def renderArea(self, width, height, srs, xmin, ymin, xmax, ymax, zoom):
        mapnik_map = mapnik.Map(width, height, srs)
        mapnik_map.zoom_to_box(mapnik.Box2d(xmin, ymin, xmax, ymax))
        img = mapnik.Image(width, height)
        self.addStyle(mapnik_map)
        mapnik.render(mapnik_map, img)

        return Image.frombytes('RGBA', (width, height), img.tostring())
