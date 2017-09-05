import os

import gdal
import osr

from girder.utility.model_importer import ModelImporter


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
