from tilecloud.layout.osm import OSMTileLayout
from tilecloud.layout.wrapped import WrappedTileLayout
from tilecloud.store.s3 import S3TileStore


tilestore = S3TileStore('map3d', WrappedTileLayout(OSMTileLayout(), 'data/image/ch.swisstopo.swissimage-20111129/tiles/', '.jpg'))
