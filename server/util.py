import os

import gdal
import osr
from TileStache import parseConfig

from girder.utility.model_importer import ModelImporter
from girder.plugins.girder_ktile.style import getColorList


def getValueList(start, stop, count):
    sequence = []
    step = (stop - start) / (float(count) - 1)
    for i in range(count):
      sequence.append(float(start + i * step))

    return sequence


def getInfo(girder_file):
    info = {}
    assetstore_model = ModelImporter.model('assetstore')
    assetstore = assetstore_model.load(girder_file['assetstoreId'])
    path = os.path.join(assetstore['root'], girder_file['path'])
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

def getLayer(girder_file, band, minimum, maximum, palette):
    layer_name = os.path.splitext(girder_file['name'])[0]
    count = int(palette.split('_')[-1])
    color_list = getColorList(palette)
    value_list = getValueList(float(minimum),
                              float(maximum),
                              count)
    info = getInfo(girder_file)
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
                               "info": info,
                               "band": band,
                               "minimum": minimum,
                               "maximum": maximum,
                               "style": zip(color_list, value_list)}
                },
                "projection": "spherical mercator"
            }
        }
    }
    config = parseConfig(config_dict)
    layer = config.layers[layer_name]

    return layer
