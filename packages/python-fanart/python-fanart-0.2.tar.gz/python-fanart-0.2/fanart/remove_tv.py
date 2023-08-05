from fanart.core import Request
import fanart
from pprint import pprint


request = Request(
    apikey='e3c7f0d0beeaf45b3a0dd3b9dd8a3338',
    id='80379',
    ws=fanart.WS.TV,
    type=fanart.TYPE.ALL,
    sort=fanart.SORT.POPULAR,
    limit=fanart.LIMIT.ALL,
)
pprint(request.response)

import os
from fanart.tv import TvShow
os.environ.setdefault('FANART_APIKEY', 'e3c7f0d0beeaf45b3a0dd3b9dd8a3338')
a = TvShow.get(id='80379')
pprint(a)
