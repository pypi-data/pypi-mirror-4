from tilecloud.layout.template import TemplateTileLayout
from tilecloud.store.url import URLTileStore


tilestore = URLTileStore((TemplateTileLayout('http://maps.refuges.info/tiles/renderer.py/hiking/%(z)d/%(x)d/%(y)d.jpeg'),), content_type='image/jpeg')
