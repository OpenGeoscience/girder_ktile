import os
from girder.plugins.girder_ktile.style import getColorList
from girder.plugins.girder_ktile.util import getValueList, getInfo


from TileStache import parseConfig


def getLayer(girder_file, params):
    # TODO: Fix this ugliness
    if girder_file['mimeType'] == 'image/tiff':
        band = params['band']
        minimum = params['minimum']
        maximum = params['maximum']
        palette = params['palette']
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
                        "class": "girder.plugins.girder_ktile.geotiff:GeotiffProvider",
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

    elif girder_file['mimeType'] == 'application/x-esri-shape':
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
                        "class": "girder.plugins.girder_ktile.shapefile:ShapefileProvider",
                        "kwargs": {"file": girder_file}
                    },
                    "projection": "spherical mercator"
                }
            }
        }

        config = parseConfig(config_dict)
        layer = config.layers[layer_name]

        return layer
