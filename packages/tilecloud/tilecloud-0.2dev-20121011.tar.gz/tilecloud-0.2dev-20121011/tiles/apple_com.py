from tilecloud.layout.template import TemplateTileLayout
from tilecloud.store.url import URLTileStore


tilestore = URLTileStore(
    (TemplateTileLayout('http://gsp2.apple.com/tile?api=1&style=slideshow&layers=default&lang=en_GB&z=%(z)d&x=%(x)d&y=%(y)d&v=9'),),
    content_type='image/png')
