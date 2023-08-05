from tilecloud import BoundingPyramid, Bounds
from tilecloud.layout.i3d import I3DTileLayout
from tilecloud.layout.wrapped import WrappedTileLayout
from tilecloud.store.url import URLTileStore


tilestore = URLTileStore(
    (WrappedTileLayout(
        I3DTileLayout(),
        prefix='http://www.openwebglobe.org/data/elv/SRTM_JSON/',
        suffix='.json'),),
    bounding_pyramid=BoundingPyramid({14: (Bounds(8419, 8647), Bounds(5556, 5893))}),
    content_type='application/json')
