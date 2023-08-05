from fanart.core import Request
import fanart
request = Request(
    apikey='e3c7f0d0beeaf45b3a0dd3b9dd8a3338',
    id='24e1b53c-3085-4581-8472-0b0088d2508c',
    ws=fanart.WS.MUSIC,
    type=fanart.TYPE.ALL,
    sort=fanart.SORT.POPULAR,
    limit=fanart.LIMIT.ALL,
)
print request.response

import os
from fanart.music import Artist
os.environ.setdefault('FANART_APIKEY', 'e3c7f0d0beeaf45b3a0dd3b9dd8a3338')
a = Artist.get(id='24e1b53c-3085-4581-8472-0b0088d2508c')
print a
print repr(a)
#print a.name
#print a.mbid
#for album in a.albums:
#    for cover in album.covers:
#        print 'Saving: %s' % cover
#        cover.write()
