import mapnik
from girder.utility.model_importer import ModelImporter

class ShapefileProvider(object):
    def __init__(self, layer, **kwargs):
        self.girder_file = kwargs['file']

    def addStyle(self, m, file):
        m.background = mapnik.Color('steelblue')
        s = mapnik.Style()
        r = mapnik.Rule()
        polygon_symbolizer = mapnik.PolygonSymbolizer()
        polygon_symbolizer.fill = mapnik.Color('#f2eff9')
        r.symbols.append(polygon_symbolizer)

        line_symbolizer = mapnik.LineSymbolizer()
        line_symbolizer.stroke = mapnik.Color('rgb(50%,50%,50%)')
        line_symbolizer.stroke_width = 0.1

        r.symbols.append(line_symbolizer)
        s.rules.append(r)
        m.append_style('My Style',s)
        ds = mapnik.Shapefile(file=file)
        layer = mapnik.Layer('world')
        layer.datasource = ds
        layer.styles.append('My Style')
        m.layers.append(layer)

    def renderArea(self, width, height, srs, xmin, ymin, xmax, ymax, zoom):
        mapnik_map = mapnik.Map(width, height, srs)
        mapnik_map.zoom_to_box(mapnik.Box2d(xmin, ymin, xmax, ymax))
        img = mapnik.Image(width, height)
        path = ModelImporter.model('file').getFuseFilePath(self.girder_file)
        self.addStyle(mapnik_map, path)
        mapnik.render(mapnik_map, img)

        return Image.frombytes('RGBA', (width, height), img.tostring())
