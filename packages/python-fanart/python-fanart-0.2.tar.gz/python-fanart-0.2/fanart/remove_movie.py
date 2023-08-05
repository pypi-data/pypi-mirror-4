from fanart.core import Request
import fanart
from pprint import pprint


request = Request(
    apikey='e3c7f0d0beeaf45b3a0dd3b9dd8a3338',
    id='70160',
    ws=fanart.WS.MOVIE,
    type=fanart.TYPE.ALL,
    sort=fanart.SORT.POPULAR,
    limit=fanart.LIMIT.ALL,
)
pprint(request.response)

import os
from fanart.movie import Movie
os.environ.setdefault('FANART_APIKEY', 'e3c7f0d0beeaf45b3a0dd3b9dd8a3338')
a = Movie.get(id='70160')
pprint(a)
