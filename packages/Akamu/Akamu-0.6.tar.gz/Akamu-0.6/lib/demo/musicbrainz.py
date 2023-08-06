import json, os, cgi, urllib, re
from pprint import pprint
from amara.writers.struct import structwriter, E, ROOT
from cStringIO import StringIO
from akara import module_config as config, request
from akara.services  import service, simple_service
from akamu.config.dataset import Query
from akamu.xslt import xslt_rest, NOOPXML

SERVICE_ID_PREFIX = u'http://example.com/service/'
HTML_IMT   = 'text/html'
JSON_IMT   = 'application/json'

@simple_service(
    'GET' ,
    SERVICE_ID_PREFIX + 'music_brainz_browse_artist',
    'browse.artist',
    HTML_IMT)
@xslt_rest(
    os.path.join(
        config().get('working_directory'),
        'test/musicbrainz/music_brainz_browse_artist.xslt'),
)
def browse_artist(artist_uri):
    names           = set()
    tracks          = set()
    for artistName, track, trackLabel in Query(
            'musicbrainz-artist-info.rq',
            'musicbrainz',
            params=(artist_uri,artist_uri)):
        names.add(artistName)
        tracks.add(trackLabel)
    src = StringIO()
    w = structwriter(indent=u"yes", stream=src)
    w.feed(ROOT(
        E(u'Music',{u'artist': ' / '.join(names)},
          E(u'Tracks',
            (
                E(u'Track',{u'name':trackLabel}) for trackLabel in tracks
            )
          ),
        )
    ))
    return src.getvalue()

@simple_service(
    'GET' ,
    SERVICE_ID_PREFIX + 'music_brainz_form',
    'search.form',
    HTML_IMT)
@xslt_rest(
    os.path.join(
        config().get('working_directory'),
        'test/musicbrainz/music_brainz_search.xslt'),
    source=NOOPXML
)
def search_form(): pass

@simple_service('GET', SERVICE_ID_PREFIX + 'categories', 'categories',JSON_IMT)
def categories(term=None):
    return json.dumps([
        { 'label' : label,
          'value' : label }
            for tag,label in Query('musicbrainz-categories.rq',
                                   'musicbrainz',
                                   params=(term,))
    ])

@simple_service(
    'POST' ,
    SERVICE_ID_PREFIX + 'music_brainz_search',
    'search',
    HTML_IMT)
@xslt_rest(
    os.path.join(
        config().get('working_directory'),
        'test/musicbrainz/music_brainz_search.xslt'),
)
def search(body,ctype):
    form = cgi.FieldStorage(
        fp=StringIO(body),
        environ=request.environ
    )
    category = form.getvalue('category')
    artist   = form.getvalue('artistSearch')
    pattern = re.compile(artist)
    src = StringIO()
    w = structwriter(indent=u"yes", stream=src)

    if category is not None and category.strip():
        queryFile   = 'musicbrainz-artists.rq'
        params      = (category,)
    else:
        queryFile   = 'musicbrainz-artists-any-category.rq'
        params      = None

    w.feed(ROOT(
        E(u'Root',
          E(u'Artists',
            (
                E(u'Artist',
                  {u'name' : name,
                   u'url'  : urllib.quote(artist_uri)})
                for artist_uri,
                    name in Query(queryFile,'musicbrainz',params=params)
                if pattern.match(name)
            )
          )
        )
    ))
    return src.getvalue()