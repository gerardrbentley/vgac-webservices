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


def affords_from_csv_file(file, id_col, file_name):
    if os.path.isfile(file):
        with open(file, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            out = []
            for row in csv_reader:
                if row[id_col] == file_name:
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


def stack_numpy_channels(affordance_images):
    height, width, *_ = affordance_images[0].shape
    output = np.zeros((height, width, 10))
    print(
        f'GEN numpy array of dims {output.shape} for aff_image {affordance_images[0].shape}')
    for i in range(10):
        one_channel = affordance_images[i].copy()
        output[:, :, i] = one_channel // 255
    return output


class DB_Manager(object):
    def __init__(self, **kwargs):
        keys = {'host': os.getenv('POSTGRES_HOST', 'vgac-db'),
                'port': os.getenv('POSTGRES_PORT', '5432'),
                'dbname': os.getenv('POSTGRES_DB', 'affordances_db'),
                'user': os.getenv('POSTGRES_USER', 'faim_lab'),
                'password': os.getenv('POSTGRES_PASSWORD', 'dev'),
                'cursor_factory': DictCursor
                }
        print(keys)
        self.connection = psycopg2.connect(**keys)
        # self.cursor = connection.cursor()

    def ingest_filesystem_data(self, dir=os.path.join('/app/games')):
        total_ingested = {}
        for game in list_games(dir):
            num_images, num_tags, num_skipped = self.ingest_screenshots(
                game, os.path.join(dir, game, 'screenshots'))

            num_textures, num_texture_tags, num_texture_skipped = self.ingest_textures(
                game, os.path.join(dir, game, 'textures'))
            # ingest_sprite_files(sprite_files, game), dir
            total_ingested[game] = {
                'num_images': num_images, 'num_screenshot_tags': num_tags, 'num_textures': num_textures, 'skipped_images': num_skipped}
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
            is_in = self.check_uuid_in_table(
                'screenshots', 'image_id', screenshot_uuid)
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

            # TODO: Load known labels from numpy
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

            one_channel = stacked_array[:, :, i].astype(np.uint8) * 255
            image_buffer = Image.fromarray(one_channel)

            image_bytes = io.BytesIO()
            image_buffer.save(image_bytes, format='PNG')
            image_bytes = image_bytes.getvalue()
            # image_bytes = image_buffer.tobytes()
            # _, image_buffer = cv2.imencode('.png', one_channel)
            # print('one channel shape', one_channel.shape, 'buff shape', type(image_bytes))

            channels_dict[AFFORDANCES[i]] = image_bytes
        print('INGESTING SCREENSHOT: {}'.format(image_id))
        if (channels) == 9:
            print('9 channel map, adding blank permeable')

            new_channel = np.zeros_like(one_channel)
            image_buffer = Image.fromarray(new_channel)
            image_bytes = io.BytesIO()
            image_buffer.save(image_bytes, format='PNG')
            image_bytes = image_bytes.getvalue()
            # _, image_buffer = cv2.imencode('.png', new_channel)

            channels_dict["permeable"] = image_bytes
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

    def ingest_textures(self, game, textures_dir):
        ctr = 0
        tag_ctr = 0
        skip_ctr = 0
        for texture_file in glob.glob(os.path.join(textures_dir, '*.png')):
            file_name = os.path.split(texture_file)[1]
            texture_id = os.path.splitext(file_name)[0]
            is_in = self.check_uuid_in_table('textures', 'texture_id', texture_id)
            if is_in:
                print(f'SKIPPED INGESTING TEXTURE: {texture_id}')
                skip_ctr += 1
            else:
                with open(texture_file, 'rb') as f:
                    data = f.read()
                tex_image = Image.open(texture_file)
                to_insert = {
                    'texture_id': texture_id,
                    'game': game,
                    'width': tex_image.width,
                    'height': tex_image.height,
                    'data': data,
                    'dt': datetime.now()
                }
                result = self.insert_texture(to_insert)
                # texture_id = result['texture_id']

                csv_file = os.path.join(textures_dir, 'texture_affordances.csv')
                texture_entries = affords_from_csv_file(csv_file, 'texture_id', texture_id)
                if len(texture_entries) > 0:
                    print('texture HAD AFFORDS')
                    for texture_entry in texture_entries:
                        to_insert = {
                            'texture_id': texture_id,
                            'tagger_id': texture_entry['tagger_id'],
                            'solid': texture_entry['solid'],
                            'movable': texture_entry['movable'],
                            'destroyable': texture_entry['destroyable'],
                            'dangerous': texture_entry['dangerous'],
                            'gettable': texture_entry['gettable'],
                            'portal': texture_entry['portal'],
                            'usable': texture_entry['usable'],
                            'changeable': texture_entry['changeable'],
                            'ui': texture_entry['ui'],
                            'permeable': texture_entry['permeable'],
                            'dt': datetime.now()
                        }
                        self.insert_texture_tag(to_insert)
                        tag_ctr += 1
                ctr += 1
        return ctr, tag_ctr, skip_ctr

    def export_to_filesystem(self, dest='/app/out_dataset'):
        game_names = self.get_game_names()
        print(type(game_names))
        print(f'exporting data for games: {game_names}')
        total_exported = {}
        for game in game_names:
            game = game['game']
            screenshot_ctr = 0

            game_path = os.path.join(dest, game)
            os.makedirs(os.path.join(game_path, 'screenshots'), exist_ok=True)
            textures_folder = os.path.join(game_path, 'textures')
            os.makedirs(textures_folder, exist_ok=True)            
            os.makedirs(os.path.join(game_path, 'sprites'), exist_ok=True)

            print(f'Made Directories for game: {game}, {game_path}')
            screenshots = self.get_screenshots_by_game(game)
            print(type(screenshots))
            print(f'Exporting {len(screenshots)} screenshots for {game}')
            for screenshot in screenshots:
                image_id = screenshot['image_id']
                image_folder = os.path.join(
                    game_path, 'screenshots', str(image_id))
                os.makedirs(image_folder, exist_ok=True)

                image_file = os.path.join(image_folder, f'{image_id}.png')
                with open(image_file, 'wb') as file:
                    file.write(screenshot['data'].tobytes())
                # orig_cv, encoded_img = P.from_data_to_cv(screenshot['data'])
                # print(
                #     f'saving file: {image_file}  -- {orig_cv.shape} {type(orig_cv)}')
                # cv2.imwrite(image_file, orig_cv)
                self.save_labels(image_id, image_folder)
                meta = {
                    'y_offset': screenshot['y_offset'],
                    'x_offset': screenshot['x_offset'],
                    'crop_l': screenshot['crop_l'],
                    'crop_r': screenshot['crop_r'],
                    'crop_b': screenshot['crop_b'],
                    'crop_t': screenshot['crop_t'],
                    'ui_x': screenshot['ui_x'],
                    'ui_y': screenshot['ui_y'],
                    'ui_width': screenshot['ui_width'],
                    'ui_height': screenshot['ui_height'],
                }
                with open(os.path.join(
                        image_folder, f'{str(image_id)}.json'), 'w') as file:
                    json.dump(meta, file)

            textures = self.get_textures_by_game(game)
            print(f'Exporting {len(textures)} textures for {game}')

            to_csv = []
            for texture in textures:
                texture_id = texture['texture_id']

                texture_file = os.path.join(textures_folder, f'{texture_id}.png')
                with open(texture_file, 'wb') as file:
                    file.write(texture['data'].tobytes())
                # orig_cv, encoded_img = P.from_data_to_cv(texture['data'])
                # print(
                #     f'saving file: {texture_file}  -- {orig_cv.shape} {type(orig_cv)}')
                # cv2.imwrite(texture_file, orig_cv)

                texture_tag_entries = self.get_texture_affordances(texture_id)
                for db_entry in texture_tag_entries:
                    print(db_entry)
                    print(type(db_entry))
                    print(db_entry.items())

                    to_insert = {k: v for k, v in db_entry.items()}
                    # db_entry['file_name'] = db_entry.pop('texture_id')
                    to_csv.append(to_insert)
            with open(os.path.join(textures_folder, 'texture_affordances.csv'), mode='w') as csv_file:
                fieldnames = ["texture_id", "solid", "movable", "destroyable",
                              "dangerous", "gettable", "portal", "usable", "changeable", "ui", "permeable", "tagger_id"]
                writer = csv.DictWriter(
                    csv_file, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                for row in to_csv:
                    writer.writerow(row)
        return 1

    def save_labels(self, image_uuid, image_folder):
        # label_file = os.path.join(image_folder, 'label', f'{image_uuid}.npy')
        db_entries = self.get_screenshot_affordances(image_uuid)
        row_ctr = 0
        if len(db_entries) % 10 != 0:
            print('NOT MOD 10 TAG ENTRIES FOR IMAGE: {}'.format(image_uuid))
        # print('NUM ROWS OF AFFORDANCES {} FOR IMAGE {}'.format(
        #     len(db_entries), image_uuid))
        to_insert = {}
        for db_entry in db_entries:
            # label_to_convert = []
            tagger_id = db_entry['tagger_id']
            if tagger_id not in to_insert:
                to_insert[tagger_id] = {}
            aff = db_entry['affordance']
            # for affordance in AFFORDANCES:
            #     db_entry = db_entries[row_ctr]
            # print(type(db_entry.data))
            # if db_entry.affordance != affordance:
            #     print('AFFORDANCES IN WRONG ORDER, ', db_entry.affordance)
            # tag_cv, encoded = P.from_data_to_cv(db_entry['tags'])
            to_insert[tagger_id][aff] = db_entry['data']
            # row_ctr += 1
        for tagger in to_insert:
            # print(tagger)
            # print(to_insert[tagger].keys())
            label_to_convert = []
            for affordance in AFFORDANCES:
                # print(affordance)
                d = to_insert[tagger][affordance].tobytes()
                # print(type(d))
                # print((d))

                # arrayform = np.frombuffer(d, dtype=np.uint8)
                conv = np.asarray(Image.open(
                    io.BytesIO(d)).convert("L"), dtype=np.uint8)
                # print(type(conv))
                label_to_convert.append(conv)

            stacked_array = stack_numpy_channels(label_to_convert)
            pth = os.path.join(image_folder, f'{tagger}.npy')
            print(f'NUMPY SAVE: saving file: {pth}')
            np.save(os.path.join(image_folder, f'{tagger}.npy'), stacked_array)

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
        texture_table = sql.SQL(
            """CREATE TABLE IF NOT EXISTS textures(
            texture_id UUID PRIMARY KEY,
            game VARCHAR (50) NOT NULL,
            width integer,
            height integer,
            created_on TIMESTAMP NOT NULL,
            data bytea
            )"""
        )
        texture_tags_table = sql.SQL(
            """CREATE TABLE IF NOT EXISTS texture_tags(
            texture_id UUID NOT NULL,
            created_on TIMESTAMP NOT NULL,
            tagger_id VARCHAR(50) NOT NULL,
            solid real NOT NULL,
            movable real NOT NULL,
            destroyable real NOT NULL,
            dangerous real NOT NULL,
            gettable real NOT NULL,
            portal real NOT NULL,
            usable real NOT NULL,
            changeable real NOT NULL,
            ui real NOT NULL,
            permeable real NOT NULL,
            PRIMARY KEY (texture_id, tagger_id),
            CONSTRAINT texture_tags_texture_id_fkey FOREIGN KEY (texture_id)
              REFERENCES textures (texture_id) MATCH SIMPLE
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
            solid real NOT NULL,
            movable real NOT NULL,
            destroyable real NOT NULL,
            dangerous real NOT NULL,
            gettable real NOT NULL,
            portal real NOT NULL,
            usable real NOT NULL,
            changeable real NOT NULL,
            ui real NOT NULL,
            permeable real NOT NULL,
            PRIMARY KEY (sprite_id, tagger_id),
            CONSTRAINT sprite_tags_sprite_id_fkey FOREIGN KEY (sprite_id)
              REFERENCES sprites (sprite_id) MATCH SIMPLE
              ON UPDATE NO ACTION ON DELETE NO ACTION
            )"""
        )
        to_exec = [screenshot_table, screenshot_tags_table, texture_table, texture_tags_table, sprite_table, sprite_tag_table]

        with self.connection:
            with self.connection.cursor() as cursor:
                for cmd in to_exec:
                    print(cmd.as_string(self.connection))
                    cursor.execute(cmd)

    def drop_all(self):
        print('Dropping All')
        tables = ['screenshots', 'screenshot_tags', 'textures', 'texture_tags', 'sprites', 'sprite_tags']
        BASE = "DROP TABLE IF EXISTS {} CASCADE"
        with self.connection:
            with self.connection.cursor() as cursor:
                for table in tables:
                    cmd = sql.SQL(BASE).format(sql.Identifier(table))
                    print(cmd.as_string(self.connection))
                    cursor.execute(cmd)

    def check_uuid_in_table(self, table='default', col='default', id='default'):
        cmd = sql.SQL(
            """SELECT EXISTS(SELECT 1 FROM {} where {} = %(id)s) as "exists"
            """
        ).format(sql.Identifier(table), sql.Identifier(col))
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

    def get_game_names(self):
        cmd = sql.SQL(
            """SELECT DISTINCT game FROM {};
            """
        ).format(sql.Identifier('screenshots'))
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(cmd)
                res = cursor.fetchall()
        if res is not None:
            return res
        return []

    def get_screenshots_by_game(self, game):
        cmd = sql.SQL(
            """SELECT * FROM {}
            WHERE game = %(game)s;
            """
        ).format(sql.Identifier('screenshots'))
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(cmd, {'game': game})
                res = cursor.fetchall()
        if res is not None:
            return res
        return []

    def get_screenshot_affordances(self, image_id='default'):
        cmd = sql.SQL(
            """SELECT image_id, affordance, data, tagger_id FROM screenshot_tags
            WHERE image_id = %(image_id)s ORDER BY tagger_id, affordance;
            """
        )
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(cmd, {'image_id': image_id})
                res = cursor.fetchall()
        if res is not None:
            return res
        return []
    
    def get_textures_by_game(self, game='default'):
        cmd = sql.SQL(
            """SELECT * FROM textures
            WHERE game = %(game)s;
            """
        )
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(cmd, {'game': game})
                res = cursor.fetchall()
        if res is not None:
            return res
        return []

    def get_texture_affordances(self, texture_id='default'):
        cmd = sql.SQL(
            """SELECT * FROM texture_tags
            WHERE texture_id = %(texture_id)s;
            """
        )
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(cmd, {'texture_id': texture_id})
                res = cursor.fetchall()
        if res is not None:
            return res
        return []

    # INSERTION SQL

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

    def insert_texture(self, kwargs):
        cmd = sql.SQL(
            """INSERT INTO textures(texture_id, game, width, height, created_on, data)
            VALUES(%(texture_id)s, %(game)s, %(width)s, %(height)s, %(dt)s, %(data)s)
            RETURNING texture_id
            """
        )
        with self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(cmd, kwargs)
                res = cursor.fetchone()
        return res[0]

    def insert_texture_tag(self, kwargs):
        cmd = sql.SQL(
            """INSERT INTO texture_tags(texture_id, created_on, tagger_id, solid, movable, destroyable, dangerous, gettable, portal, usable, changeable, ui, permeable)
            VALUES(%(texture_id)s, %(dt)s, %(tagger_id)s, %(solid)s, %(movable)s, %(destroyable)s, %(dangerous)s, %(gettable)s, %(portal)s, %(usable)s, %(changeable)s, %(ui)s, %(permeable)s)
            ON CONFLICT ON CONSTRAINT texture_tags_pkey
            DO UPDATE SET solid = %(solid)s, movable = %(movable)s, destroyable = %(destroyable)s, dangerous = %(dangerous)s, gettable = %(gettable)s, portal = %(portal)s, usable = %(usable)s, changeable = %(changeable)s, ui = %(ui)s, permeable = %(permeable)s
            RETURNING texture_id
            """
        )

        with self.connection:
            with self.connection.cursor() as cursor:
                print(cmd.as_string(self.connection))
                cursor.execute(cmd, kwargs)
                res = cursor.fetchone()
        return res[0]

    def close(self):
        self.connection.close()


if __name__ == '__main__':
    manage = DB_Manager()
    print('DB Manager made')
