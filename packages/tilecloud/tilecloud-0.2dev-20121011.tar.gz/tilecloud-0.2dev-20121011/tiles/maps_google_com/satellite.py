from tilecloud.layout.template import TemplateTileLayout
from tilecloud.store.url import URLTileStore


tilestore = URLTileStore([TemplateTileLayout('https://khms%d.google.com/kh/v=113&src=app&x=%%(x)d&y=%%(y)d&z=%%(z)d&s=Galileo' % i) for i in (0, 1)])
