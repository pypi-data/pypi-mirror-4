from raspberry_jam import app, filters, models, helpers
from spider import crawl
import pprint

@app.route('/')
def raspberry_jam():
    return 'Homepage'

# Crawl soundcloud for tracks to store in `bucket` table
@app.route('/crawl')
def jam():
    tracks = crawl.fetch_tracks()
    m = models.Storage()
    tracks_crawled = []

    for track in tracks:
        f = filters.Filter()
        if f.unique(track.id, 'bucket') and f.filter_track(track, 'bucket'):
            p = f.popularity(track)
            stored_track = m.store_track_in_bucket(track, p)
            tracks_crawled.append(stored_track.id)

    return '<pre>%s</pre>' % pprint.pformat(tracks_crawled)

@app.route('/move-to-library')
def move_to_library():
    m = models.Storage()
    tracks = m.lookup_tracks(98)
    app.logger.debug('Got tracks')

    # Build list of track ids to send to SoundCloud
    id_list = []
    for track_id in tracks:
        for id_group in track_id:
            id_list.append(str(id_group))

    track_lists = helpers.chunk(id_list, 200)
    app.logger.debug('Requests to make: %s' % len(track_lists))

    # Loop through track_lists
    for i, track_list in enumerate(track_lists):
        requested_ids = ','.join(track_list)
        app.logger.debug('Request: %s' % (i, ))
        updated_tracks = crawl.lookup_tracks(requested_ids)

        if updated_tracks:
            f = filters.Filter()
            for track in updated_tracks:
                if m.lookup_bucket(track.id):
                    m.remove_track_from_bucket(track.id)
                    p = f.popularity(track)
                    m.store_track_in_bucket(track, p)
                    app.logger.debug('id: %s, p: %s' % (track.id, p))
                    if p > 0.3: # Threshold of quality
                        added_track = m.store_track_in_library(track, p)
        else:
            lost_tracks = [int(track_id) for track_id in track_list]
            removed = m.remove_track_from_bucket(lost_tracks)
            app.logger.debug('...: %s', removed)

    return 'Moved tracks'

# Setup tables for app
@app.route('/setup/')
def setup():
    m = models.Storage()
    m.create_table_library()
    m.create_table_bucket()

    return 'Setup Correctly'
