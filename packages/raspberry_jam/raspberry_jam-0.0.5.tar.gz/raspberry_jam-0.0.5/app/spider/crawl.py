from spider import app
from raspberry_jam import helpers, app
import soundcloud, pprint

raspberry_jam = '00d1b88836fe1fd24a9753ab974c87b1'
client = soundcloud.Client(client_id=raspberry_jam)

# Returns latest 10 tracks from the SoundCloud API as string
def fetch_tracks():
    try:
        tracks = client.get('/tracks', order='latest', limit=200)
    except:
        return "Unable to get tracks from SoundCloud"

    return tracks

# Returns track metadata from the SoundCloud API for ids specified
def lookup_tracks(requested_ids):
    try:
        tracks = client.get('/tracks', ids=requested_ids, limit=200)
        return tracks
    except Exception as e:
        app.logger.error('Err: %s' % e)
