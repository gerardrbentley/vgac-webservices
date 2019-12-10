import json
import os
import glob
import io
import csv
from datetime import datetime
import uuid

from psycopg2.extras import DictCursor
from psycopg2 import sql
import psycopg2

import numpy as np
from PIL import Image

AFFORDANCES = ["solid", "movable", "destroyable",
               "dangerous", "gettable", "portal", "usable", "changeable", "ui", "permeable"]

def load_label_from_tagger(label_file):
    if os.path.isfile(label_file):
        print('Label File Found {}'.format(label_file))
        stacked_array = np.load(label_file)
    else:
        print('New Label File for {}'.format(label_file))
        stacked_array = None
    return stacked_array

def list_games(dir=os.path.join('/games')):
    try:
        games = next(os.walk(dir))[1]
    except (StopIteration):
        games = []
        print('GAME FOLDERS NOT FOUND IN GAMES, NO FILES FOUND')
    return games

def affords_from_csv_file(file, file_name):
    if os.path.isfile(file):
        with open(file, mode='r') as tile_csv:
            csv_reader = csv.DictReader(tile_csv)
            out = []
            for row in csv_reader:
                if row['file_name'] == file_name:
                    out.append(row)
            return out
    return []

def metadata_from_json(screenshots_dir, file_uuid):
    pth = os.path.join(screenshots_dir, file_uuid, f'{file_uuid}.json')
    if os.path.isfile(pth):
        with open(pth, mode='r') as metadata_file:
            data = json.load(metadata_file)
            output = {
                'crop_l': data['crop_l'],
                'crop_r': data['crop_r'],
                'crop_b': data['crop_b'],
                'crop_t': data['crop_t'],
                'ui_x': data['ui_x'],
                'ui_y': data['ui_y'],
                'ui_width': data['ui_width'],
                'ui_height': data['ui_height'],
                'y_offset': data['y_offset'],
                'x_offset': data['x_offset']
            }
            return output
    return {
                'crop_l': 0,
                'crop_r': 0,
                'crop_b': 0,
                'crop_t': 0,
                'ui_x': 0,
                'ui_y': 0,
                'ui_width': 0,
                'ui_height': 0,
                'y_offset': 0,
                'x_offset': 0
            }

class DB_Manager(object):
    def __init__(self, **kwargs):
        connargs = {'dbname': 'postgres',
            'user': 'postgres',
            'host': '192.168.99.101',
            'port': '5432'}
        self.connection = psycopg2.connect(**connargs)
        # self.cursor = connection.cursor()

    def ingest_filesystem_data(self, dir):
        total_ingested = {}
        for game in list_games(dir):
            # num_images, num_tags = ingest_screenshot_files_with_offsets(
            #         screenshot_files, game, dir)
            num_images, num_tags, num_skipped = self.ingest_screenshots(
                game, os.path.join(dir, game, 'screenshots'))

            # num_tiles = ingest_tiles_from_pickle(game, dir)
            num_tiles, num_tile_tags, num_tile_skipped = ingest_tiles(game, os.path.join(dir, game, 'tiles'))
            # ingest_sprite_files(sprite_files, game), dir
            total_ingested[game] = {
                    'num_images': num_images, 'num_screenshot_tags': num_tags, 'num_tiles': num_tiles, 'skipped_images': num_skipped}
        print('TOTALS: {}'.format(total_ingested))

    def ingest_screenshots(self, game, screenshots_dir):
        ctr = 0
        tag_ctr = 0
        skip_ctr = 0
        tag_skip_ctr = 0
        image_folders = next(os.walk(screenshots_dir))[1]

        for screenshot_uuid in image_folders:
            screenshot_file = os.path.join(
                screenshots_dir, screenshot_uuid, f'{screenshot_uuid}.png')
            # screenshot_uuid = os.path.splitext(file_name)[0]
            is_in = self.check_uuid_in_table('screenshots', screenshot_uuid)
            if is_in:
                print(f'SKIPPED INGESTING IMAGE: {screenshot_uuid}')
                skip_ctr += 1
            else:
                metadata = metadata_from_json(
                    screenshots_dir, screenshot_uuid)
                print('offsets got for image num: {}, y:{}, x:{}'.format(
                    screenshot_uuid, metadata['y_offset'], metadata['x_offset']))

                # cv_image, encoded_png = P.load_image(screenshot_file)
                # h, w, *_ = cv_image.shape
                # data = encoded_png.tobytes()
                with open(screenshot_file, 'rb') as f:
                    data = f.read()
                to_insert = {
                        'image_id': screenshot_uuid,
                        'game': game,
                        'width': 256,
                        'height': 224,
                        'data': data,
                        'dt': datetime.now(),
                    }
                to_insert.update(metadata)
                result = self.insert_screenshot(
                    to_insert)
                print(result)

            #TODO: Load known labels from numpy
            label_files = glob.glob(os.path.join(
                screenshots_dir, screenshot_uuid, "*.npy"))
            if len(label_files) > 0:
                for label_file in label_files:
                    tagger_npy = os.path.split(label_file)[1]
                    tagger = os.path.splitext(tagger_npy)[0]
                    has_tagged = self.check_tagger_tagged_screenshot(
                        screenshot_uuid, tagger)
                    if has_tagged:
                        print(
                            f'SKIPPED INGESTING Tags:{tagger} on {screenshot_uuid}')
                        tag_skip_ctr += 1
                    else:
                        label = load_label_from_tagger(label_file)
                        if label is not None:
                            self.ingest_screenshot_tags(
                                label, screenshot_uuid, tagger=tagger)
                            tag_ctr += 1
            ctr += 1
        return ctr, tag_ctr, skip_ctr

    def ingest_screenshot_tags(self, stacked_array, image_id, tagger='ingested'):
        # channels_dict = P.numpy_to_images(stacked_array)
        _, _, channels = stacked_array.shape
        channels_dict = {}
        for i in range(channels):

            one_channel = stacked_array[:, :, i].copy() * 255
            image_buffer = Image.fromarray(one_channel, mode='L')
            # image_buffer.save('tmp/'+image_id+AFFORDANCES[i]+".png", format="PNG")
            image_bytes = io.BytesIO()
            image_buffer.save(image_bytes, format='PNG')
            image_bytes = image_bytes.getvalue()
            # _, image_buffer = cv2.imencode('.png', one_channel)
            # print('one channel shape', one_channel.shape, 'buff shape', type(image_bytes))

            channels_dict[AFFORDANCES[i]] = image_bytes
        print('INGESTING SCREENSHOT: {}'.format(image_id))
        if (channels) == 9:
            print('9 channel map, adding blank permeable')

            new_channel = np.zeros_like(one_channel)
            image_buffer = Image.fromarray(new_channel, mode='L')
            image_bytes = io.BytesIO()
            image_buffer.save(image_bytes, format='PNG')
            image_bytes = image_bytes.getvalue()
            # _, image_buffer = cv2.imencode('.png', new_channel)

            channels_dict["permeable"] = image_bytes
            # print('one channel shape', one_channel.shape, 'buff shape', type(image_bytes))

        for i, affordance in enumerate(AFFORDANCES):
            channel_data = channels_dict[affordance]
            # channel_data = encoded_channel.tobytes()

            to_insert = {
                'image_id': image_id,
                'affordance': affordance,
                'tagger': tagger,
                'data': channel_data,
                'dt': datetime.now(),
            }
            self.insert_screenshot_tag(to_insert)

    def ingest_tiles(self, game, tiles_dir):
        ctr = 0
        tag_ctr = 0
        skip_ctr = 0
        for tile_file in glob.glob(os.path.join(tiles_dir, '*.png')):
            file_name = os.path.split(tile_file)[1]
            tile_uuid = os.path.splitext(file_name)[0]
            is_in = check_uuid_in_table('tiles', tile_uuid)
            if is_in:
                print(f'SKIPPED INGESTING TILE: {tile_uuid}')
                skip_ctr += 1
            else:
                # cv, encoded_png = P.load_image(tile_file)
                # h, w, c = cv.shape
                # data = encoded_png.tobytes()
                with open(screenshot_file, 'rb') as f:
                    data = f.read()
                result = insert_tile(tile_uuid, game, 8, 8, data)
                # tile_id = result['tile_id']

                # TODO TILE AFFORDANCES
                csv_file = os.path.join(dir, game, 'tiles', 'tile_affordances.csv')
                tile_entries = affords_from_csv_file(csv_file, tile_uuid)
                if len(tile_entries) > 0:
                    print('TILE HAD AFFORDS')
                    for tile_entry in tile_entries:
                        insert_tile_tag(
                            tile_uuid, tile_entry['tagger_id'], int(
                                tile_entry['solid']),
                            int(tile_entry['movable']), int(tile_entry['destroyable']), int(tile_entry['dangerous']), int(tile_entry['gettable']), int(tile_entry['portal']), int(tile_entry['usable']), int(tile_entry['changeable']), int(tile_entry['ui']))
                        tag_ctr += 1
                ctr += 1
        return ctr, tag_ctr, skip_ctr

    def init_tables(self):
        print('Making Tables')
        screenshot_table = sql.SQL(
            """CREATE TABLE IF NOT EXISTS screenshots(
            image_id UUID PRIMARY KEY,
            game VARCHAR (50) NOT NULL,
            width integer,
            height integer,
            y_offset integer,
            x_offset integer,
            crop_l integer,
            crop_r integer,
            crop_b integer,
            crop_t integer,
            ui_x integer,
            ui_y integer,
            ui_width integer,
            ui_height integer,
            created_on TIMESTAMP NOT NULL,
            data bytea
            )"""
        )
        screenshot_tags_table = sql.SQL(
            """CREATE TABLE IF NOT EXISTS screenshot_tags(
            image_id UUID NOT NULL,
            affordance VARCHAR(12) NOT NULL,
            tagger_id VARCHAR(50) NOT NULL,
            created_on TIMESTAMP NOT NULL,
            data bytea,
            PRIMARY KEY (image_id, affordance, tagger_id),
            CONSTRAINT screenshot_tags_image_id_fkey FOREIGN KEY (image_id)
              REFERENCES screenshots (image_id) MATCH SIMPLE
              ON UPDATE NO ACTION ON DELETE NO ACTION
            )"""
        )

        tile_table = sql.SQL(
            """CREATE TABLE IF NOT EXISTS tiles(
            tile_id UUID PRIMARY KEY,
            game VARCHAR (50) NOT NULL,
            width integer,
            height integer,
            created_on TIMESTAMP NOT NULL,
            data bytea
            )"""
        )
        tile_tags_table = sql.SQL(
            """CREATE TABLE IF NOT EXISTS tile_tags(
            tile_id UUID NOT NULL,
            created_on TIMESTAMP NOT NULL,
            tagger_id VARCHAR(50) NOT NULL,
            solid boolean NOT NULL,
            movable boolean NOT NULL,
            destroyable boolean NOT NULL,
            dangerous boolean NOT NULL,
            gettable boolean NOT NULL,
            portal boolean NOT NULL,
            usable boolean NOT NULL,
            changeable boolean NOT NULL,
            ui boolean NOT NULL,
            permeable boolean NOT NULL,
            PRIMARY KEY (tile_id, tagger_id),
            CONSTRAINT tile_tags_tile_id_fkey FOREIGN KEY (tile_id)
              REFERENCES tiles (tile_id) MATCH SIMPLE
              ON UPDATE NO ACTION ON DELETE NO ACTION
            )"""
        )
        sprite_table = sql.SQL(
            """CREATE TABLE IF NOT EXISTS sprites(
            sprite_id UUID PRIMARY KEY,
            game VARCHAR (50) NOT NULL,
            width integer,
            height integer,
            created_on TIMESTAMP NOT NULL,
            data bytea
            )"""
        )
        sprite_tag_table = sql.SQL(
            """CREATE TABLE IF NOT EXISTS sprite_tags(
            sprite_id UUID NOT NULL,
            created_on TIMESTAMP NOT NULL,
            tagger_id VARCHAR(50) NOT NULL,
            solid boolean NOT NULL,
            movable boolean NOT NULL,
            destroyable boolean NOT NULL,
            dangerous boolean NOT NULL,
            gettable boolean NOT NULL,
            portal boolean NOT NULL,
            usable boolean NOT NULL,
            changeable boolean NOT NULL,
            ui boolean NOT NULL,
            permeable boolean NOT NULL,
            PRIMARY KEY (sprite_id, tagger_id),
            CONSTRAINT sprite_tags_sprite_id_fkey FOREIGN KEY (sprite_id)
              REFERENCES sprites (sprite_id) MATCH SIMPLE
              ON UPDATE NO ACTION ON DELETE NO ACTION
            )"""
        )
        to_exec = [screenshot_table, screenshot_tags_table, tile_table,
                   tile_tags_table, sprite_table, sprite_tag_table]

        with self.connection:
            with self.connection.cursor() as cursor:
                for cmd in to_exec:
                    print(cmd.as_string(self.connection))
                    cursor.execute(cmd)

    def drop_all(self):
        print('Dropping All')
        tables = ['screenshots', 'screenshot_tags',
                  'tiles', 'tile_tags', 'sprites', 'sprite_tags']
        BASE = "DROP TABLE IF EXISTS {} CASCADE"
        with self.connection:
            with self.connection.cursor() as cursor:
                for table in tables:
                    cmd = sql.SQL(BASE).format(sql.Identifier(table))
                    print(cmd.as_string(self.connection))
                    cursor.execute(cmd)

    def check_uuid_in_table(self, table='default', id='default'):
        cmd = sql.SQL(
            """SELECT EXISTS(SELECT 1 FROM {} where image_id = %(id)s) as "exists"
            """
        ).format(sql.Identifier(table))
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(cmd, {'id': id})
                res = cursor.fetchone()
        if res is not None:
            return res[0]
        return False

    def check_tagger_tagged_screenshot(self, id, tagger_id):
        cmd = sql.SQL(
            """SELECT EXISTS(SELECT 1 FROM {} where image_id = %(id)s and tagger_id = %(tagger_id)s) as "exists"
            """
        ).format(sql.Identifier('screenshot_tags'))
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(cmd, {'id': id, 'tagger_id': tagger_id})
                res = cursor.fetchone()
        if res is not None:
            return res[0]
        return False

        ####SQL
    def insert_screenshot(self, kwargs):
        cmd = sql.SQL(
            """INSERT INTO screenshots(image_id, game, width, height, y_offset, x_offset, created_on, data, crop_l, crop_r, crop_t, crop_b, ui_x, ui_y, ui_height, ui_width)
            VALUES(%(image_id)s, %(game)s, %(width)s, %(height)s, %(y_offset)s, %(x_offset)s, %(dt)s, %(data)s, %(crop_l)s, %(crop_r)s, %(crop_t)s, %(crop_b)s, %(ui_x)s, %(ui_y)s, %(ui_height)s, %(ui_width)s)
            RETURNING image_id
            """
        )
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(cmd, kwargs)
                res = cursor.fetchone()
        return res[0]

    def insert_screenshot_tag(self, kwargs):
        cmd = sql.SQL(
            """INSERT INTO screenshot_tags(image_id, affordance, tagger_id, created_on, data)
            VALUES(%(image_id)s, %(affordance)s, %(tagger)s, %(dt)s, %(data)s)
            ON CONFLICT ON CONSTRAINT screenshot_tags_pkey
            DO UPDATE SET data = %(data)s
            RETURNING image_id
            """
        )
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(cmd, kwargs)
                res = cursor.fetchone()
        return res[0]

    def close(self):
        self.connection.close()

if __name__ == '__main__':
    print('ingesting')
    manage = DB_Manager()
    print('manage made')
    manage.drop_all()
    print('dropped all')
    manage.init_tables()
    print('made all tables')
    manage.ingest_screenshots('sm3', '../tagger/eventgames/sm3/screenshots/')
    print('ingested, closing')
    manage.close()
