from raspberry_jam import app
from datetime import datetime, timedelta
import psycopg2, pprint, random


class Storage:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(database='raspberryjam',
                    user='raspberryadmin', host='localhost',
                    password='43D8!aHWXsrk26AZA2%t')
            self.cur = self.conn.cursor()
        except psycopg2.DatabaseError, e:
            app.logger.error(e.pgerror)

    def store_track_in_bucket(self, track, popularity):
        try:
            track_fields = ('created_at', 'duration', 'commentable', 'state',
                    'sharing', 'tag_list', 'permalink', 'description',
                    'streamable', 'downloadable', 'genre', 'release',
                    'purchase_url', 'label_id', 'label_name', 'isrc',
                    'video_url', 'track_type', 'key_signature', 'bpm', 'title',
                    'release_year', 'release_month', 'release_day',
                    'original_format', 'original_content_size', 'license',
                    'uri', 'permalink_url', 'artwork_url', 'waveform_url',
                    'download_url', 'stream_url', 'playback_count',
                    'download_count', 'favoritings_count', 'attachments_uri')
            user_fields = ('id', 'permalink', 'username', 'uri',
                    'permalink_url', 'avatar_url')
            params = {name: getattr(track, name, '') for name in track_fields}
            params.update(('sc_user_{}'.format(name), track.user[name]) for name
                    in user_fields)
            params.update(last_crawled=str(datetime.utcnow().replace(microsecond=0).isoformat(' ')),
            popularity=popularity, sc_id=track.id)

            query = 'INSERT INTO bucket ({}) VALUES ({});'.format(', '.join(params),
                    ', '.join(['%s'] * len(params)))
            app.logger.debug('Query: %s' % query)
            self.cur.execute(query, params.values())
            self.conn.commit()

            return track
        except psycopg2.DatabaseError, e:
            app.logger.error(e.pgerror)
            if self.conn:
                self.conn.rollback()
            pass

        return False

    def store_track_in_library(self, track, popularity):
        try:
            track_fields = ('created_at', 'duration', 'commentable', 'state',
                    'sharing', 'tag_list', 'permalink', 'description',
                    'streamable', 'downloadable', 'genre', 'release',
                    'purchase_url', 'label_id', 'label_name', 'isrc',
                    'video_url', 'track_type', 'key_signature', 'bpm', 'title',
                    'release_year', 'release_month', 'release_day',
                    'original_format', 'original_content_size', 'license',
                    'uri', 'permalink_url', 'artwork_url', 'waveform_url',
                    'download_url', 'stream_url', 'playback_count',
                    'download_count', 'favoritings_count', 'attachments_uri')
            user_fields = ('id', 'permalink', 'username', 'uri',
                    'permalink_url', 'avatar_url')
            params = {name: getattr(track, name, '') for name in track_fields}
            params.update(('sc_user_{}'.format(name), track.user[name]) for name
                    in user_fields)
            params.update(popularity=popularity, sc_id=track.id)

            query = 'INSERT INTO library ({}) VALUES ({});'.format(', '.join(params),
                    ', '.join(['%s'] * len(params)))
            self.cur.execute(query, params.values())
            self.conn.commit()

            return track
        except psycopg2.DatabaseError, e:
            app.logger.error(e.pgerror)
            if self.conn:
                self.conn.rollback()
            pass

        return False

    # Updates tracks when given list of dictionaries
    def update_tracks(self, tracks):
        try:
            track_fields = ('created_at', 'duration', 'commentable', 'state',
                    'sharing', 'tag_list', 'permalink', 'description',
                    'streamable', 'downloadable', 'genre', 'release',
                    'purchase_url', 'label_id', 'label_name', 'isrc',
                    'video_url', 'track_type', 'key_signature', 'bpm', 'title',
                    'release_year', 'release_month', 'release_day',
                    'original_format', 'original_content_size', 'license',
                    'uri', 'permalink_url', 'artwork_url', 'waveform_url',
                    'download_url', 'stream_url', 'playback_count',
                    'download_count', 'favoritings_count', 'attachments_uri')
            user_fields = ('id', 'permalink', 'username', 'uri',
                    'permalink_url', 'avatar_url')

            insert = []
            param_names = None
            for track in tracks:
                params = {name: getattr(track['track'], name, '') for name in track_fields}
                params.update(('sc_user_{}'.format(name), track['track'].user[name]) for name
                        in user_fields)
                params.update(last_crawled=str(datetime.utcnow().replace(microsecond=0).isoformat(' ')),
                popularity=track['p'], sc_id=track['track'].id)
                insert.append(params)
                param_names = params
            insert = tuple(insert) # Convert list to tuple (sequence)

            self.cur.executemany("""INSERT INTO bucket ({}) VALUES
                    ({});""".format(', '.join(param_names.keys()), ', '.join(
                        ['%(a)s'.replace('a', key) for key in
                            param_names.keys()] )), insert)
            self.conn.commit()

            return True
        except psycopg2.DatabaseError, e:
            app.logger.error(e.pgerror)
            if self.conn:
                self.conn.rollback()
            pass

        return False

    # Return sc_id of records last crawled outside of given time period
    def lookup_tracks(self, day_offset):
        try:
            self.cur.execute("""SELECT sc_id FROM bucket WHERE last_crawled <
                    now() - interval '%s days'""", (day_offset, ))
            self.conn.commit()
        except psycopg2.DatabaseError, e:
            app.logger.error(e.pgerror)
            if self.conn:
                self.conn.rollback()

        if self.cur.rowcount:
            return self.cur.fetchall()
        else:
            return False

    # Lookup a track according to sc_id of track_sc_id in bucket
    def lookup_bucket(self, track_sc_id):
        try:
            self.cur.execute("SELECT * FROM bucket WHERE sc_id = %s;",
                    (track_sc_id, ))
            self.conn.commit()
        except Exception as e:
            app.logger.error(e.pgerror)

        if self.cur.rowcount:
            return True
        else:
            return False

    # Lookup a track according to sc_id of track_sc_id in library
    def lookup_library(self, track_sc_id):
        try:
            self.cur.execute("SELECT * FROM library WHERE sc_id = %s;",
                    (track_sc_id, ))
            if self.cur.fetchone() is None:
                return False
            else:
                return True
        except psycopg2.DatabaseError, e:
            app.logger.error(e)

    # Remove row(s) based on id
    def remove_track_from_bucket(self, track_sc_id):
        if not isinstance(track_sc_id, list):
            try:
                self.cur.execute("DELETE FROM bucket WHERE sc_id = %s;",
                        (track_sc_id, ))
                self.conn.commit()
                return True
            except Exception, e:
                app.logger.error(e.pgerror)
                if self.conn:
                    self.conn.rollback()
                return False
        else:
            try:
                self.cur.execute("DELETE FROM bucket WHERE sc_id = ANY(%s);",
                        (track_sc_id, ))
                self.conn.commit()
                return True
            except Exception, e:
                app.logger.error(e.pgerror)
                if self.conn:
                    self.conn.rollback()
                return False

    # Lookup tracks with parameters passed in kwargs
    def copy_tracks_to_filter(self, **kwargs):
        try:
            self.cur.execute("""SELECT * INTO filter from {} {} ({});""".format(
                '%s' % kwargs.get('table'), '%s' % kwargs.get('clause'),
                '%s' % kwargs.get('arguments')))
            self.conn.commit()
        except psycopg2.DatabaseError, e:
            app.logger.error(e.pgerror)
            if self.conn:
                self.conn.rollback()

        if self.cur.rowcount:
            return self.cur.fetchall()
        else:
            return False

    # Lookup track from filter
    def lookup_track_filter(self):
        try:
            self.cur.execute("""select * from filter offset random() * (select count(*)
                    from filter) limit 1;""")
            self.conn.commit()
        except psycopg2.DatabaseError as e:
            app.logger.debug('Err: %s', e)
            if self.conn:
                self.conn.rollback()

        if self.cur.rowcount:
            tracks = self.cur.fetchall()
            cols = [column[0] for column in self.cur.description]
            app.logger.debug(cols)
            return map(lambda row: dict(zip(cols, row)), tracks).pop()
        else:
            return None

    def like_track_filter(self, track_id):
        try:
            self.cur.execute("""UPDATE filter SET popularity = popularity + .1
            WHERE id = '%s';""" % track_id)
            self.conn.commit()

            return True
        except psycopg2.DatabaseError as e:
            app.logger.debug('Err: %s', e)
            if self.conn:
                self.conn.rollback()

    def dislike_track_filter(self, track_id):
        try:
            self.cur.execute("""UPDATE filter SET popularity = popularity - .1
            WHERE id = '%s';""" % track_id)
            self.conn.commit()

            return True
        except psycopg2.DatabaseError as e:
            app.logger.debug('Err: %s', e)
            if self.conn:
                self.conn.rollback()



    def remove_from_filter(self, track_id):
        try:
            self.cur.execute("""delete from filter where id = '%s';""" %
                    track_id)
            self.conn.commit()

            return True
        except psycopg2.DatabaseError as e:
            app.logger.debug('Err: %s', e)
            if self.conn:
                self.conn.rollback()

    # Creates 'library' table in database
    def create_table_library(self):
        try:
            self.cur.execute("""CREATE TABLE library(id SERIAL PRIMARY KEY, popularity
                    NUMERIC, sc_id INT, created_at TIMESTAMP WITH TIME ZONE,
                    sc_user_id INT, duration INT, commentable BOOLEAN, state TEXT
                    , sharing TEXT, tag_list TEXT, permalink TEXT,
                    description TEXT, streamable BOOLEAN, downloadable BOOLEAN,
                    genre TEXT, release TEXT, purchase_url TEXT, label_id INT,
                    label_name TEXT, isrc TEXT, video_url TEXT, track_type TEXT,
                    key_signature TEXT, bpm INT, title TEXT, release_year INT,
                    release_month TEXT, release_day TEXT, original_format TEXT,
                    original_content_size INT, license TEXT, uri TEXT,
                    permalink_url TEXT, artwork_url TEXT, waveform_url TEXT,
                    sc_user_permalink TEXT, sc_user_username TEXT,
                    sc_user_uri TEXT, sc_user_permalink_url TEXT,
                    sc_user_avatar_url TEXT, stream_url TEXT, download_url TEXT,
                    playback_count INT, download_count INT, favoritings_count INT,
                    attachments_uri TEXT);""")
            self.conn.commit()
        except psycopg2.DatabaseError, e:
            app.logger.error(e.pgerror)
            if self.conn:
                self.conn.rollback()

    # Creates 'bucket' table in database
    def create_table_bucket(self):
        try:
            self.cur.execute("""CREATE TABLE bucket(id SERIAL PRIMARY KEY, popularity
                    NUMERIC, sc_id INT, created_at TIMESTAMP WITH TIME ZONE,
                    sc_user_id INT, duration INT, commentable BOOLEAN, state TEXT
                    , sharing TEXT, tag_list TEXT, permalink TEXT,
                    description TEXT, streamable BOOLEAN, downloadable BOOLEAN,
                    genre TEXT, release TEXT, purchase_url TEXT, label_id INT,
                    label_name TEXT, isrc TEXT, video_url TEXT, track_type TEXT,
                    key_signature TEXT, bpm INT, title TEXT, release_year INT,
                    release_month TEXT, release_day TEXT, original_format TEXT,
                    original_content_size INT, license TEXT, uri TEXT,
                    permalink_url TEXT, artwork_url TEXT, waveform_url TEXT,
                    sc_user_permalink TEXT, sc_user_username TEXT,
                    sc_user_uri TEXT, sc_user_permalink_url TEXT,
                    sc_user_avatar_url TEXT, stream_url TEXT, download_url TEXT,
                    playback_count INT, download_count INT, favoritings_count INT,
                    attachments_uri TEXT, last_crawled TIMESTAMP);""")
            self.conn.commit()
        except psycopg2.DatabaseError, e:
            app.logger.error(e.pgerror)
            if self.conn:
                self.conn.rollback()

    def create_table_filter(self):
        try:
            self.cur.execute("""CREATE TABLE filter(id SERIAL PRIMARY KEY, popularity
                    NUMERIC, sc_id INT, created_at TIMESTAMP WITH TIME ZONE,
                    sc_user_id INT, duration INT, commentable BOOLEAN, state TEXT
                    , sharing TEXT, tag_list TEXT, permalink TEXT,
                    description TEXT, streamable BOOLEAN, downloadable BOOLEAN,
                    genre TEXT, release TEXT, purchase_url TEXT, label_id INT,
                    label_name TEXT, isrc TEXT, video_url TEXT, track_type TEXT,
                    key_signature TEXT, bpm INT, title TEXT, release_year INT,
                    release_month TEXT, release_day TEXT, original_format TEXT,
                    original_content_size INT, license TEXT, uri TEXT,
                    permalink_url TEXT, artwork_url TEXT, waveform_url TEXT,
                    sc_user_permalink TEXT, sc_user_username TEXT,
                    sc_user_uri TEXT, sc_user_permalink_url TEXT,
                    sc_user_avatar_url TEXT, stream_url TEXT, download_url TEXT,
                    playback_count INT, download_count INT, favoritings_count INT,
                    attachments_uri TEXT, last_crawled TIMESTAMP);""")
            self.conn.commit()
        except psycopg2.DatabaseError, e:
            app.logger.error(e.pgerror)
            if self.conn:
                self.conn.rollback()
