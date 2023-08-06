from tilecloud.layout.template import TemplateTileLayout
from tilecloud.store.url import URLTileStore


tilestore = URLTileStore([TemplateTileLayout('http://mt%d.google.com/vt/lyrs=t@128,r@167000000&hl=en&x=%%(x)d&y=%%(y)d&z=%%(z)d&s=Gali' % i) for i in xrange(0, 4)])
