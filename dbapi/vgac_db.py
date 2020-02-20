import json
import base64
from datetime import datetime
import os

from klein import Klein
from twisted.web.static import File
from twisted.web.util import Redirect
from twisted.enterprise import adbapi
from twisted.internet.defer import inlineCallbacks, ensureDeferred
from twisted.internet import defer
from twisted.logger import Logger

from werkzeug.exceptions import HTTPException, NotFound

from psycopg2.extras import DictCursor
from psycopg2 import sql

import numpy as np
import cv2

AFFORDANCES = []
NUM_AFFORDANCES = 10
IMAGE_BASE = "data:image/png;base64,{}"


def err_with_logger(request, the_logger, err_str):
    the_logger.error(err_str)
    request.setResponseCode(500)
    # return Redirect(b'/500.html')
    return json.dumps({'status': 500, 'message': err_str})


def dict_decode(bytes_keys_values):
    return {k.decode('utf-8'): list(map(lambda x: x.decode('utf-8'), v)) for (k, v) in bytes_keys_values.items()}


def b64_string(data):
    return IMAGE_BASE.format((base64.b64encode(data)).decode('utf-8'))


def mse(a, b):
    if a.shape != b.shape:
        print('WRONG SHAPE')
        return 1
    diffs = np.square(np.subtract(a, b))
    total_diff = np.sum(diffs)
    return np.divide(total_diff, (a.shape[0] * a.shape[1]))


def point_on_grid(c, r, cols, rows):
    return c in cols and r in rows


def grid_using_crop(width, height, grid_size=8, grid_offset_x=0, grid_offset_y=0, crop_l=0, crop_r=0, crop_t=0, crop_b=0):
    row_num = (height - crop_t - crop_b) // grid_size
    if (row_num * grid_size) + crop_t + grid_offset_y > height - crop_b:
        row_num -= 1
    col_num = (width - crop_l - crop_r) // grid_size
    if (col_num * grid_size) + crop_l + grid_offset_x > width - crop_r:
        col_num -= 1

    rows, cols = np.indices((row_num, col_num))
    rows = rows * grid_size
    cols = cols * grid_size

    rows = rows + crop_t + grid_offset_y
    cols = cols + crop_l + grid_offset_x

    return rows, cols


def unbuffer_and_decode(image_bytes):
    try:
        print('unbuffering {type(image_bytes)}')
        encoded_img = np.frombuffer(image_bytes, dtype=np.uint8)
        print('decoding', type(encoded_img), encoded_img.shape)
        image = cv2.imdecode(encoded_img, cv2.IMREAD_UNCHANGED)
        print(type(image))
    except:
        return defer.fail()
    return defer.succeed(image)

@inlineCallbacks
def unique_textures_from_image(image):
    return defer.fail()

@inlineCallbacks
def unique_tiles_using_meta(image, y_offset=0, x_offset=0, width=256, height=224, crop_l=0, crop_r=0, crop_t=0, crop_b=0, ui_x=0, ui_y=0, ui_height=0, ui_width=0):
    print('Finding unique tiles in img')
    grid_size = 8
    try:
        image = yield unbuffer_and_decode(image)
    except:
        return defer.fail()

    h, w, *_ = image.shape
    print(f'h: {h}, w: {w}')
    new_image = image[crop_t: h - crop_b, crop_l: w - crop_r, :]
    new_h, new_w, *_ = new_image.shape

    img_tiles = []
    visited_locations = []
    tile_ctr = 0
    skip_ctr = 0
    rows, cols = grid_using_crop(
        width, height, grid_size, x_offset, y_offset, crop_l, crop_r, crop_t, crop_b)
    for r in np.unique(rows):
        for c in np.unique(cols):
            if((r, c) not in visited_locations):
                template_np = image[r:r+grid_size if r+grid_size <= height else height,
                                    c:c+grid_size if c+grid_size <= width else width].copy()
                orig, encoded = cv2.imencode('.png', template_np)
                data = encoded.tobytes()

                res = cv2.matchTemplate(
                    template_np, image, cv2.TM_SQDIFF_NORMED)
                loc = np.where(res <= 5e-6)
                matches = list(zip(*loc[::1]))
                matches = [(y, x) for (y, x) in matches if point_on_grid(
                    x, y, cols, rows)]

                matches_dict = {}
                for i in range(len(matches)):
                    y, x = matches[i]
                    matches_dict['location_{}'.format(i)] = {
                        'x': int(x), 'y': int(y)}
                if len(matches) != 0:
                    for match_loc in matches:
                        visited_locations.append(match_loc)
                else:
                    print(
                        'ERROR MATCHING TILE WITHIN IMAGE: (r,c) ({},{})'.format(r, c))

                img_tiles.append({
                    'texture_data': b64_string(data),
                    'locations': matches_dict
                })
                tile_ctr += 1
            else:
                skip_ctr += 1

    print('VISITED {} tiles, sum of unique({}) + skip({}) = {}'.format(
        len(visited_locations), len(img_tiles), skip_ctr, (len(img_tiles)+skip_ctr)))
    # print(img_tiles[0]['tile_data'].shape)
    return img_tiles


def get_texture_ids(unique_textures, known_textures):
    textures_to_tag = {}
    print('LEN UNIQUE: {}'.format(len(unique_textures)))
    try:
        hit_ctr = 0
        miss_ctr = 0
        for idx, screenshot_texture in enumerate(unique_textures):
            to_compare = screenshot_texture['texture_data']
            is_in_db = False
            for texture_info in known_textures:
                b64_texture = texture_info['data']
                if b64_texture == to_compare:
                    is_in_db = True

                    hit_ctr += 1

                    textures_to_tag['texture_{}'.format(idx)] = {
                        'texture_id': texture_info['texture_id'],
                        'texture_data': to_compare,
                        'locations': screenshot_texture['locations']
                    }
                    break
            if not is_in_db:
                miss_ctr += 1
                textures_to_tag['texture_{}'.format(idx)] = {
                    'texture_id': -1,
                    'texture_data': to_compare,
                    'locations': screenshot_texture['locations']
                }
    except:
        return defer.fail()
    # print('done')
    # print('done 2')
    print(f'db texture hits: {hit_ctr}, misses: {miss_ctr}')
    # print('wtf')
    return defer.succeed(textures_to_tag)


def succConnectionPool(conn):
    pid = conn.get_backend_pid()
    print("New DB connection created (backend PID {})".format(pid))


class VGAC_Database(object):

    def __init__(self):
        self.deployment = str(os.getenv('TARGET', 'dev'))
        self.POSTGRES_HOST = 'vgac-db'
        if self.deployment == 'staging':
            self.POSTGRES_HOST = 'vgac-db-staging'
        elif self.deployment == 'test':
            self.POSTGRES_HOST = 'vgac-db-test'

        keys = {
            'host': self.POSTGRES_HOST,
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'affordances_db'),
            'user': os.getenv('POSTGRES_USER', 'faim_lab'),
            'password': os.getenv('POSTGRES_PASSWORD', 'dev'),
        }

        self.dbpool = adbapi.ConnectionPool('psycopg2',
                                            cp_min=3,
                                            cp_max=10,
                                            cp_noisy=True,
                                            cp_openfun=succConnectionPool,
                                            cp_reconnect=True,
                                            cp_good_sql="SELECT 1",
                                            cursor_factory=DictCursor,
                                            **keys)

    def insert_screenshot_tag(self, kwargs):
        cmd = sql.SQL(
            """INSERT INTO screenshot_tags(image_id, affordance, tagger_id, created_on, data)
            VALUES(%(image_id)s, %(affordance)s, %(tagger_id)s, %(dt)s, %(data)s)
            ON CONFLICT ON CONSTRAINT screenshot_tags_pkey
            DO UPDATE SET data = %(data)s
            RETURNING image_id
            """
        )
        return self.dbpool.runOperation(cmd, kwargs)
        # print('Insert Screenshot tag Called and Ended')

    def insert_texture(self, kwargs):
        cmd = sql.SQL(
            """INSERT INTO textures(texture_id, game, width, height, created_on, data)
            VALUES(%(texture_id)s, %(game)s, %(width)s, %(height)s, %(dt)s, %(data)s)
            RETURNING texture_id
            """
        )
        return self.dbpool.runOperation(cmd, kwargs)
        # print('Insert texture Called and Ended')

    def insert_texture_tag(self, kwargs):
        cmd = sql.SQL(
            """INSERT INTO texture_tags(texture_id, created_on, tagger_id, solid, movable, destroyable, dangerous, gettable, portal, usable, changeable, ui, permeable)
            VALUES(%(texture_id)s, %(dt)s, %(tagger_id)s, %(solid)s, %(movable)s, %(destroyable)s, %(dangerous)s, %(gettable)s, %(portal)s, %(usable)s, %(changeable)s, %(ui)s, %(permeable)s)
            ON CONFLICT ON CONSTRAINT texture_tags_pkey
            DO UPDATE SET solid = %(solid)s, movable = %(movable)s, destroyable = %(destroyable)s, dangerous = %(dangerous)s, gettable = %(gettable)s, portal = %(portal)s, usable = %(usable)s, changeable = %(changeable)s, ui = %(ui)s, permeable = %(permeable)s
            RETURNING texture_id
            """
        )

        return self.dbpool.runOperation(cmd, kwargs)
        # print('Insert texture Tag Called and Ended')

    def queryAll(self, table):
        select_stmt = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table))
        return self.dbpool.runQuery(select_stmt)

    def get_random_screenshot(self):
        cmd = sql.SQL(
            """SELECT * FROM screenshots
            OFFSET floor(random() * (SELECT COUNT (*) FROM screenshots))
            LIMIT 1;
            """
        )
        return self.dbpool.runQuery(cmd)

    def get_untagged_screenshot(self, tagger_id='default'):
        cmd = sql.SQL(
            """SELECT * FROM screenshots
            WHERE NOT EXISTS
                (SELECT 1
                FROM screenshot_tags
                WHERE screenshots.image_id = screenshot_tags.image_id AND screenshot_tags.tagger_id = %(tagger)s)
            ORDER BY random()
            LIMIT 1;
            """
        )
        return self.dbpool.runQuery(cmd, {"tagger": tagger_id})

    def get_resource_by_id(self, table='default', col='default', resource_id='default'):
        cmd = sql.SQL(
            """SELECT * FROM {}
            WHERE {} = %(resource_id)s;
            """
        ).format(sql.Identifier(table), sql.Identifier(col))
        return self.dbpool.runQuery(cmd, {"resource_id": resource_id})

    def get_screenshot_affordances(self, image_id='default'):
        cmd = sql.SQL(
            """SELECT image_id, affordance, data, tagger_id FROM screenshot_tags
            WHERE image_id = %(image_id)s ORDER BY tagger_id, affordance;
            """
        )
        return self.dbpool.runQuery(cmd, {"image_id": image_id})

    def get_game_names(self):
        cmd = sql.SQL(
            """SELECT DISTINCT game FROM screenshots;
            """
        )
        return self.dbpool.runQuery(cmd)

    def get_texture_affordances(self, texture_id='default'):
        cmd = sql.SQL(
            """SELECT * FROM texture_tags
            WHERE texture_id = %(texture_id)s;
            """
        )
        return self.dbpool.runQuery(cmd, {"texture_id": texture_id})

    def get_screenshots_by_game(self, game='default'):
        cmd = sql.SQL(
            """SELECT * FROM screenshots
            WHERE game = %(game)s;
            """
        )
        return self.dbpool.runQuery(cmd, {"game": game})

    def get_textures_by_game(self, game='default'):
        cmd = sql.SQL(
            """SELECT * FROM textures
            WHERE game = %(game)s;
            """
        )
        return self.dbpool.runQuery(cmd, {"game": game})

    def get_sprites_by_game(self, game='default'):
        cmd = sql.SQL(
            """SELECT * FROM sprites
            WHERE game = %(game)s;
            """
        )
        return self.dbpool.runQuery(cmd, {"game": game})

    def check_uuid_in_table(self, table='default', id='default'):
        cmd = sql.SQL(
            """SELECT EXISTS(SELECT 1 FROM {} where image_id = %(id)s) as "exists"
            """
        ).format(sql.Identifier(table))
        return self.dbpool.runQuery(cmd, {"id": id})

    def check_tagger_tagged_screenshot(self, image_id='defalut', tagger_id='default'):
        cmd = sql.SQL(
            """SELECT EXISTS(SELECT 1 FROM screenshot_tags where image_id = %(image_id)s and tagger_id = %(tagger_id)s) as "exists"
            """
        )
        return self.dbpool.runQuery(cmd, {"image_id": image_id, "tagger_id": tagger_id})


class VGAC_DBAPI(object):
    app = Klein()
    db = VGAC_Database()
    log = Logger()

    def __init__(self):
        self.deployment = str(os.getenv('TARGET', 'test'))
        self.POSTGRES_HOST = 'vgac-db'
        if self.deployment == 'staging':
            self.POSTGRES_HOST = 'vgac-db-staging'
        elif self.deployment == 'test':
            self.POSTGRES_HOST = 'vgac-db-test'

        self.log.info(
            f'DB API on {self.deployment} running, database connection: {self.POSTGRES_HOST}')

    #--------- Debug ----------#
    @app.route('/test')
    def message(self, request):
        request.setHeader('Content-Type', 'application/json')
        return json.dumps({'status': 200, 'message': f'{self.deployment}: dbapi test'})

    #--------- Error Handling ----------#
    @app.handle_errors(NotFound)
    def not_found_handler(self, request, failure):
        request.setResponseCode(404)
        return Redirect(b'/404.html')

    @app.handle_errors
    def error_handler(self, request, failure):
        request.setResponseCode(500)
        return Redirect(b'/500.html')

    #--------- Routes ---------#
    @app.route('/')
    def documentation(self, request):
        return Redirect(b'/html/dbapi_documentation.html')

    @app.route('/insert', methods=['POST'])
    @inlineCallbacks
    def insert(self, request):
        self.log.info(f'POST received type: {type(request.args)}')
        try:
            data = json.loads(request.content.read())
        except:
            return err_with_logger(request, self.log, f'Bad JSON in POST request')

        tagger_id = data.get('tagger_id', None)
        image_id = data.get('image_id', None)
        if tagger_id is None:
            return err_with_logger(request, self.log, f'Bad tagger id or image id in POST request')

        self.log.info(f'RECEIVED TAGS FROM: {tagger_id} FOR IMAGE: {image_id}')

        # We use [] instead of None to just ignore the iteration and still log, don't have to handle error
        textures = (data.get('textures', []))
        try:
            texture_insertion = yield self.textures_to_db(textures, tagger_id)
            self.log.info(f'{texture_insertion}')
        except:
            return err_with_logger(request, self.log, f'Bad JSON inserting textures')

        tag_images = data.get('tag_images', [])
        if len(tag_images) > 0 and image_id is None:
            return err_with_logger(request, self.log, f'No image id from POST request with tag images')
        elif len(tag_images) % NUM_AFFORDANCES == 0:
            try:
                tag_insertion = yield self.screenshot_tags_to_db(tag_images, image_id, tagger_id)
                self.log.info(f'{tag_insertion}')
            except:
                return err_with_logger(request, self.log, f'Bad JSON inserting screenshot tags')
        request.setHeader('Content-Type', 'application/json')
        return json.dumps({'status': 200, 'message': 'Inserted into db'})

    @app.route('/screenshots', methods=['GET'])
    @inlineCallbacks
    def randScreenshot(self, request):
        str_args = dict_decode(request.args)
        tagger_id = str_args.get('tagger', ['default'])[0]
        try:
            d = yield self.db.get_untagged_screenshot(tagger_id=tagger_id)
        except:
            return err_with_logger(request, self.log, 'Failed to query DB')
        try:
            d = yield self.screenshotJSON(d)
        except:
            return err_with_logger(request, self.log, 'Failed to get screenshot data')
        request.setHeader('Content-Type', 'application/json')
        return d

    @app.route('/screenshots/<string:image_id>', methods=['GET'])
    @inlineCallbacks
    def screenshotById(self, request, image_id):
        try:
            d = yield self.db.get_resource_by_id(table='screenshots', col='image_id', resource_id=image_id)
        except:
            return err_with_logger(request, self.log, 'Failed to query DB')
        try:
            d = yield self.screenshotJSON(d)
        except:
            return err_with_logger(request, self.log, 'Failed get screenshot data')
        request.setHeader('Content-Type', 'application/json')
        return d

    @app.route('/screenshots/<string:image_id>/affordances', methods=['GET'])
    @inlineCallbacks
    def tagsById(self, request, image_id):
        try:
            d = yield self.db.get_screenshot_affordances(image_id=image_id)
        except:
            return err_with_logger(request, self.log, 'Failed to query DB')
        try:
            d = yield self.screenshot_tagJSON(d)
        except:
            return err_with_logger(request, self.log, 'Failed to get screenshot affordances')
        request.setHeader('Content-Type', 'application/json')
        return d

    @app.route('/screenshots/<string:image_id>/tiles', methods=['GET'])
    @inlineCallbacks
    def tilesByImage(self, request, image_id):
        try:
            result = yield self.db.get_resource_by_id(table='screenshots', col='image_id', resource_id=image_id)
            record = result[0]
        except:
            return err_with_logger(request, self.log, 'Failed to get screenshot by id')
        try:
            image_data = record['data']
            image_id = record['image_id']
            game = record['game']
            meta = {
                'width': record['width'],
                'height': record['height'],
                'y_offset': record['y_offset'],
                'x_offset': record['x_offset'],
                'crop_l': record['crop_l'],
                'crop_r': record['crop_r'],
                'crop_b': record['crop_b'],
                'crop_t': record['crop_t'],
                'ui_x': record['ui_x'],
                'ui_y': record['ui_y'],
                'ui_width': record['ui_width'],
                'ui_height': record['ui_height'],
            }
        except:
            return err_with_logger(request, self.log, 'Bad Screenshot JSON or meta')

        try:
            unique_tiles = yield unique_tiles_using_meta(image_data, **meta)
        except:
            return err_with_logger(request, self.log, 'Failed to get tiles for image')
        try:
            game_texture_data = yield self.db.get_textures_by_game(game)
        except:
            return err_with_logger(request, self.log, f'Failed to get tiles for game: {game}')
        try:
            known_game_textures = []
            for record in game_texture_data:
                mapper = {
                    'texture_id': record['texture_id'],
                }
                data = record['data']
                strf = b64_string(data)
                mapper['data'] = strf
                known_game_textures.append(mapper)
            self.log.info(f'len known tiles: {len(known_game_textures)}')
            out_tiles = yield get_texture_ids(unique_tiles, known_game_textures)
        except:
            return err_with_logger(request, self.log, 'Failed to match tiles for ids')

        request.setHeader('Content-Type', 'application/json')
        return json.dumps(out_tiles)

    # TODO: Write get image textures function
    @app.route('/screenshots/<string:image_id>/textures', methods=['GET'])
    @inlineCallbacks
    def texturesByImage(self, request, image_id):
        try:
            result = yield self.db.get_resource_by_id(table='screenshots', col='image_id', resource_id=image_id)
            record = result[0]
        except:
            return err_with_logger(request, self.log, 'Failed to get screenshot by id')
        try:
            image_data = record['data']
            image_id = record['image_id']
            game = record['game']
            meta = {
                'width': record['width'],
                'height': record['height'],
                'y_offset': record['y_offset'],
                'x_offset': record['x_offset'],
                'crop_l': record['crop_l'],
                'crop_r': record['crop_r'],
                'crop_b': record['crop_b'],
                'crop_t': record['crop_t'],
                'ui_x': record['ui_x'],
                'ui_y': record['ui_y'],
                'ui_width': record['ui_width'],
                'ui_height': record['ui_height'],
            }
        except:
            return err_with_logger(request, self.log, 'Bad Screenshot JSON or meta')

        try:
            unique_textures = yield unique_textures_from_image(image_data)
        except:
            return err_with_logger(request, self.log, 'Failed to get textures for image')
        try:
            game_texture_data = yield self.db.get_textures_by_game(game)
        except:
            return err_with_logger(request, self.log, f'Failed to get textures for game: {game}')
        try:
            known_game_textures = []
            for record in game_texture_data:
                mapper = {
                    'texture_id': record['texture_id'],
                }
                data = record['data']
                strf = b64_string(data)
                mapper['data'] = strf
                known_game_textures.append(mapper)
            self.log.info(f'len known textures: {len(known_game_textures)}')
            out_textures = yield get_texture_ids(unique_textures, known_game_textures)
        except:
            return err_with_logger(request, self.log, 'Failed to match textures for ids')

        request.setHeader('Content-Type', 'application/json')
        return json.dumps(out_textures)

    @app.route('/textures/<string:texture_id>', methods=['GET'])
    @inlineCallbacks
    def textureById(self, request, texture_id):
        try:
            d = yield self.db.get_resource_by_id(table='textures', col='texture_id', resource_id=texture_id)
        except:
            return err_with_logger(self.log, request, 'Failed to Query DB')
        try:
            d = yield self.textureJSON(d)
        except:
            return err_with_logger(self.log, request, 'Bad JSON from db for textures')

        request.setHeader('Content-Type', 'application/json')
        return d

    @app.route('/textures/<string:texture_id>/affordances', methods=['GET'])
    @inlineCallbacks
    def textureAffordanceById(self, request, texture_id):
        try:
            d = yield self.db.get_texture_affordances(texture_id=texture_id)
        except:
            return err_with_logger(self.log, request, 'Failed to Query DB')
        try:
            d = yield self.texture_affordanceJSON(d)
        except:
            return err_with_logger(self.log, request, 'Bad JSON from db for textures')

        request.setHeader('Content-Type', 'application/json')
        return d

    @app.route('/textures', methods=['GET'])
    @inlineCallbacks
    def texturesBase(self, request):
        str_args = dict_decode(request.args)
        game_name = str_args.get('game', ['default'])[0]

        try:
            d = yield self.db.get_textures_by_game(game_name)
        except:
            return err_with_logger(self.log, request, 'Failed to Query DB')
        try:
            d = yield self.textureJSON(d)
        except:
            return err_with_logger(self.log, request, 'Bad JSON from db for textures')
        request.setHeader('Content-Type', 'application/json')
        return d

    #--------- Helpers ----------#
    @inlineCallbacks
    def textures_to_db(self, textures, tagger_id):
        insert_count = 0
        skip_count = 0
        # first = True
        for texture in textures:
            # textures not in DB have texture id -1
            texture_id = textures[texture].get('texture_id', -1)
            if not isinstance(texture_id, int):
                try:
                    to_insert = {
                        'texture_id': texture_id,
                        'tagger_id': tagger_id,
                        'solid': textures[texture]['solid'],
                        'movable': textures[texture]['movable'],
                        'destroyable': textures[texture]['destroyable'],
                        'dangerous': textures[texture]['dangerous'],
                        'gettable': textures[texture]['gettable'],
                        'portal': textures[texture]['portal'],
                        'usable': textures[texture]['usable'],
                        'changeable': textures[texture]['changeable'],
                        'ui': textures[texture]['ui'],
                        'permeable': textures[texture]['permeable'],
                        'dt': datetime.now()
                    }

                    insert_count += 1
                    yield self.db.insert_texture_tag(to_insert)
                except:
                    self.log.error('Defer insert failure')
                    return defer.fail()
            else:
                skip_count += 1
        log_str = f'Inserted {insert_count} texture Tags. SKIPPED {skip_count} textures. SUBMITTED: {len(textures)}'
        # self.log.info(log_str)
        return log_str

    @inlineCallbacks
    def screenshot_tags_to_db(self, tag_images, image_id, tagger_id):
        count = 0
        for affordance in tag_images:
            # self.log.info(f'affordance: {affordance}')
            try:
                b64_channel = tag_images[affordance]
                # self.log.info(b64_channel)
                data_tag = b64_channel[:22]
                # self.log.info(data_tag)
                if data_tag == IMAGE_BASE[:22]:
                    b64_channel = b64_channel[22:]
                    # self.log.info('got b64 chan')
                    tag_data_bytes = base64.b64decode(b64_channel)
                    # self.log.info('got decoded bytes')

                    to_insert = {
                        'image_id': image_id,
                        'affordance': affordance,
                        'tagger_id': tagger_id,
                        'data': tag_data_bytes,
                        'dt': datetime.now(),
                    }
                    # self.log.info(f'to insert: {to_insert}')

                    yield self.db.insert_screenshot_tag(to_insert)
                    count += 1
                else:
                    self.log.error(
                        f'Wrong Data tag on {affordance} b64 prefix: {data_tag}')
                    return defer.fail()
            except:
                return defer.fail()
        log_str = f'Num affordance channels inserted: {count}'
        return log_str

    #---------- Callbacks -----------#
    def screenshotJSON(self, results):
        try:
            responseJSON = []
            for record in results:
                mapper = {
                    'image_id': record['image_id'],
                    'game': record['game'],
                    'width': record['width'],
                    'height': record['height'],
                    'y_offset': record['y_offset'],
                    'x_offset': record['x_offset'],
                    'crop_l': record['crop_l'],
                    'crop_r': record['crop_r'],
                    'crop_b': record['crop_b'],
                    'crop_t': record['crop_t'],
                    'ui_x': record['ui_x'],
                    'ui_y': record['ui_y'],
                    'ui_width': record['ui_width'],
                    'ui_height': record['ui_height'],
                }
                data = record['data']
                strf = b64_string(data)
                mapper['data'] = strf
                responseJSON.append(mapper)
        except:
            return defer.fail()
        return json.dumps(responseJSON)

    def screenshot_tagJSON(self, results):
        try:
            responseJSON = []
            for record in results:
                mapper = {
                    'image_id': record['image_id'],
                    'affordance': record['affordance'],
                    'tagger_id': record['tagger_id'],
                }
                data = record['data']
                strf = b64_string(data)
                mapper['data'] = strf
                responseJSON.append(mapper)
        except:
            return defer.fail()
        return json.dumps(responseJSON)

    def tileJSON(self, results):
        try:
            responseJSON = []
            for record in results:
                mapper = {
                    'tile_id': record['tile_id'],
                    'game': record['game'],
                    'width': record['width'],
                    'height': record['height'],
                }
                data = record['data']
                strf = b64_string(data)
                mapper['data'] = strf
                responseJSON.append(mapper)
        except:
            return defer.fail()
        return json.dumps(responseJSON)

    def tile_affordanceJSON(self, results):
        try:
            responseJSON = []
            for record in results:
                mapper = {
                    'tile_id': record['tile_id'],
                    'tagger_id': record['tagger_id'],
                    'solid': record['solid'],
                    'movable': record['movable'],
                    'destroyable': record['destroyable'],
                    'dangerous': record['dangerous'],
                    'gettable': record['gettable'],
                    'portal': record['portal'],
                    'usable': record['usable'],
                    'changeable': record['changeable'],
                    'ui': record['ui'],
                    'permeable': record['permeable'],
                }
                responseJSON.append(mapper)
        except:
            return defer.fail()
        return json.dumps(responseJSON)


if __name__ == '__main__':
    webapp = VGAC_DBAPI()
    webapp.app.run("0.0.0.0", 5000)
