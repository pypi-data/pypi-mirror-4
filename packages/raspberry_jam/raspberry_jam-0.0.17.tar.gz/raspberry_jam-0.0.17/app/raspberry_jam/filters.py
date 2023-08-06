from raspberry_jam import app, models

class Filter:
    def filter_track(self, track, table):
        if table == 'bucket':
            return self._bucket_filter(track)
        elif table == 'library':
            return self._library_filter(track)
        return False

    def popularity(self, track):
        try:
            if track.favoritings_count > 0 and track.playback_count > 0:
                return float(track.favoritings_count) / float(track.playback_count)
        except Exception, e:
            app.logger.debug('err')

        return 0

    def unique(self, track_sc_id, table):
        m = models.Storage()
        if table == 'bucket' :
            if not m.lookup_bucket(track_sc_id):
                return True
            else:
                return False
        elif table == 'library' :
            if not m.lookup_library(track_sc_id):
                return True
            else:
                return False

    # Filter for track to be added to bucket table
    def _bucket_filter(self, track):
        if hasattr(track, 'stream_url'):
            return True
        return False

    # Filter for track to be added to library table
    def _library_filter(self, track):
        p = self.popularity(track)
        if p: # if p > 0
            app.logger.debug('Popular enough')
            return True
        else:
            return False
