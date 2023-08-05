from tilecloud.layout.template import TemplateTileLayout
from tilecloud.store.url import URLTileStore


tilestore = URLTileStore(
    (TemplateTileLayout('http://s3.amazonaws.com/com.modestmaps.bluemarble/%(z)d-r%(y)d-c%(x)d.jpg'),))
