from raspberry_jam import app, filters, models, helpers
from spider import crawl
from flask import render_template, request
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
                    if f.filter_track(track, 'library'): # Threshold of quality
                        added_track = m.store_track_in_library(track, p)
        else:
            lost_tracks = [int(track_id) for track_id in track_list]
            removed = m.remove_track_from_bucket(lost_tracks)
            app.logger.debug('...: %s', removed)

    return 'Moved tracks'

# Filter tracks to filter table
@app.route('/filter/')
def filter():
    m = models.Storage()
    tracks = m.copy_tracks_to_filter(**{ 'table' : 'bucket', 'clause' : 'where', 'arguments' :
        'popularity > 0.01 and playback_count > 1000' })
    return "filter"

# Update tracks
@app.route('/update/')
def update():
    m = models.Storage()
    tracks = m.lookup_tracks(85)
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
            for track in updated_tracks:
                m.remove_track_from_bucket(track.id)

            f = filters.Filter()
            track_group = [{'track': track, 'p': f.popularity(track)} for track
                    in updated_tracks]
            m.update_tracks(track_group)
            app.logger.debug('List of dicts: %s' % track_group)

        else:
            lost_tracks = [int(track_id) for track_id in track_list]
            removed = m.remove_track_from_bucket(lost_tracks)

    return 'Updated tracks'

# Streaming
@app.route('/stream/')
def stream():
    m = models.Storage()

    if request.args.get('destroy'):
        t = m.remove_from_filter(request.args.get('destroy'))
        app.logger.debug(t)

    if request.args.get('like'):
        m.like_track_filter(request.args.get('like'))

    if request.args.get('dislike'):
        m.dislike_track_filter(request.args.get('dislike'))

    track = m.lookup_track_filter()
    data = { 'track' : track, 'id' : crawl.client_id() }
    app.logger.debug(pprint.pformat(data))
    return render_template('stream.html', data=data)

# Setup tables for app
@app.route('/setup/')
def setup():
    m = models.Storage()
    m.create_table_library()
    m.create_table_bucket()
    m.create_table_filter()

    return 'Setup Correctly'

