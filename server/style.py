import importlib


def getColorList(palette):
    params = palette.split('.')
    palette = params[-1]
    base = '.'.join(params[:-1])
    palettes = importlib.import_module('palettable.{}'.format(base))
    return getattr(palettes, palette).hex_colors
