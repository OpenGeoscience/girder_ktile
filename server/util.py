import os
import struct

import gdal
import osr
from pyproj import Proj, transform
from TileStache import parseConfig

from girder.utility.model_importer import ModelImporter
from girder.plugins.girder_ktile.style import getColorList

# Python bindings do not raise exceptions unless you
# explicitly call UseExceptions()
gdal.UseExceptions()

def getValueList(start, stop, count):
    sequence = []
    step = (stop - start) / (float(count) - 1)
    for i in range(count):
      sequence.append(float(start + i * step))

    return sequence

def _getDatasetPath(girder_file):
    assetstore_model = ModelImporter.model('assetstore')
    assetstore = assetstore_model.load(girder_file['assetstoreId'])
    path = os.path.join(assetstore['root'], girder_file['path'])

    return path

def _getProj4String(dataset):
    wkt = dataset.GetProjection()
    proj = osr.SpatialReference()
    proj.ImportFromWkt(wkt)

    return proj.ExportToProj4()

def _getBandStats(dataset):
    stats = {}
    stats_tags = ['min', 'max', 'mean', 'stdev']
    for i in range(dataset.RasterCount):
        band = dataset.GetRasterBand(i+1)
        band_stats = band.GetStatistics(True, True)
        stats[i+1] = dict(zip(stats_tags, band_stats))

    return stats

def getInfo(girder_file):
    info = {}
    path = _getDatasetPath(girder_file)
    dataset = gdal.Open(path)
    geotransform = dataset.GetGeoTransform()
    lrx = geotransform[0] + (dataset.RasterXSize * geotransform[1])
    lry = geotransform[3] + (dataset.RasterYSize * geotransform[5])
    info['path'] = path
    info['driver'] = dataset.GetDriver().GetDescription()
    info['pixel_size'] = geotransform[1], geotransform[5]
    info['srs'] = _getProj4String(dataset)
    info['size'] = dataset.RasterXSize, dataset.RasterYSize
    info['bands'] = _getBandStats(dataset)
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

def queryLayer(file, lat, lon):
    path = _getDatasetPath(file)
    dataset = gdal.Open(path)
    srs = _getProj4String(dataset)

    in_proj = Proj(init='epsg:4326')
    out_proj = Proj(srs)
    x, y = transform(in_proj, out_proj, lon, lat)

    gt = dataset.GetGeoTransform()

    px = int((x - gt[0]) / gt[1])
    py = int((y - gt[3]) / gt[5])
    result = {}

    for i in range(dataset.RasterCount):
        band = dataset.GetRasterBand(i+1)
        try:
            value = band.ReadRaster(px, py, 1, 1, buf_type=gdal.GDT_Float32)
            if value:
                result['band_{}'.format(i+1)] = struct.unpack('f', value)[0]
        except RuntimeError:
            pass

    return result
