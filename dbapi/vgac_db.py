import json
import base64
from datetime import datetime
import os

from klein import Klein
from twisted.web.static import File
from twisted.enterprise import adbapi
from twisted.internet.defer import inlineCallbacks, ensureDeferred

from psycopg2.extras import DictCursor
from psycopg2 import sql

import numpy as np
import cv2

def dict_decode(bytes_keys_values):
    return {k.decode('utf-8'):list(map(lambda x: x.decode('utf-8'), v)) for (k,v) in bytes_keys_values.items()}

IMAGE_BASE = "data:image/png;base64,{}"

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

def unique_tiles_using_meta(image, y_offset=0, x_offset=0, width=256, height=224, crop_l=0, crop_r=0, crop_t=0, crop_b=0, ui_x=0, ui_y=0, ui_height=0, ui_width=0):
    print('Finding unique tiles in img')
    grid_size = 8
    myBytes = image
    # if isinstance(image, str):
    #     print('pass in string')
    #     myBytes = base64.b64decode(image[22:])
    #     print(type(myBytes))
    # else:
    #     print('not string img', type(image))
    #     myBytes = image.tobytes()
    print(type(myBytes))
    encoded_img = np.frombuffer(myBytes, dtype=np.uint8)
    print(type(encoded_img), encoded_img.shape)
    image = cv2.imdecode(encoded_img, cv2.IMREAD_UNCHANGED)
    print(type(image))

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
                    'tile_data': b64_string(data),
                    'locations': matches_dict
                    })
                tile_ctr += 1
            else:
                skip_ctr += 1

    print('VISITED {} tiles, sum of unique({}) + skip({}) = {}'.format(
        len(visited_locations), len(img_tiles), skip_ctr, (len(img_tiles)+skip_ctr)))
    # print(img_tiles[0]['tile_data'].shape)
    return img_tiles

def logInsert(op):
    # print('logInsert')
    if op:
        print(op)
    pass

def logErr(op):
    print('logErr')
    if op:
        print(op)
    else:
        print("no op on error")


class VGAC_Database(object):

    def succConnectionPool(conn):
        pid = conn.get_backend_pid()
        print("New DB connection created (backend PID {})".format(pid))

    deployment = str(os.getenv('TARGET', 'dev'))
    if deployment == 'staging':
        print('from staging dbapi')
        postgres_host = 'vgac-db-staging'
    else:
        postgres_host = 'vgac-db'
        print('from live dbapi')

    keys = {
        'host': postgres_host,
        'port': os.getenv('POSTGRES_PORT', '5432'),
        'database': os.getenv('POSTGRES_DB', 'affordances_db'),
        'user': os.getenv('POSTGRES_USER', 'faim_lab'),
        'password': os.getenv('POSTGRES_PASSWORD', 'dev'),
    }
    print(keys)
    dbpool = adbapi.ConnectionPool('psycopg2',
                                    cp_min = 3,
                                    cp_max = 10,
                                    cp_noisy = True,
                                    cp_openfun = succConnectionPool,
                                    cp_reconnect = True,
                                    cp_good_sql = "SELECT 1",
                                    cursor_factory = DictCursor,
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
        self.dbpool.runOperation(cmd, kwargs).addCallbacks(logInsert, logErr)
        # print('Insert Screenshot tag Called and Ended')

    def insert_tile(self, kwargs):
        cmd = sql.SQL(
            """INSERT INTO tiles(tile_id, game, width, height, created_on, data)
            VALUES(%(tile_id)s, %(game)s, %(width)s, %(height)s, %(dt)s, %(data)s)
            RETURNING tile_id
            """
        )
        self.dbpool.runOperation(cmd, kwargs).addCallbacks(logInsert, logErr)
        # print('Insert Tile Called and Ended')

    def insert_tile_tag(self, kwargs):
        cmd = sql.SQL(
            """INSERT INTO tile_tags(tile_id, created_on, tagger_id, solid, movable, destroyable, dangerous, gettable, portal, usable, changeable, ui, permeable)
            VALUES(%(tile_id)s, %(dt)s, %(tagger_id)s, %(solid)s, %(movable)s, %(destroyable)s, %(dangerous)s, %(gettable)s, %(portal)s, %(usable)s, %(changeable)s, %(ui)s, %(permeable)s)
            ON CONFLICT ON CONSTRAINT tile_tags_pkey
            DO UPDATE SET solid = %(solid)s, movable = %(movable)s, destroyable = %(destroyable)s, dangerous = %(dangerous)s, gettable = %(gettable)s, portal = %(portal)s, usable = %(usable)s, changeable = %(changeable)s, ui = %(ui)s, permeable = %(permeable)s
            RETURNING tile_id
            """
        )

        self.dbpool.runOperation(cmd, kwargs).addCallbacks(logInsert, logErr)
        # print('Insert Tile Tag Called and Ended')

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
        return self.dbpool.runQuery(cmd, {"tagger":tagger_id})

    def get_resource_by_id(self, table='default', col='default', resource_id='default'):
        cmd = sql.SQL(
            """SELECT * FROM {}
            WHERE {} = %(resource_id)s;
            """
        ).format(sql.Identifier(table), sql.Identifier(col))
        return self.dbpool.runQuery(cmd, {"resource_id":resource_id})

    def get_screenshot_affordances(self, image_id='default'):
        cmd = sql.SQL(
            """SELECT image_id, affordance, data, tagger_id FROM screenshot_tags
            WHERE image_id = %(image_id)s ORDER BY tagger_id, affordance;
            """
        )
        return self.dbpool.runQuery(cmd, {"image_id":image_id})

    @inlineCallbacks
    def get_unique_tiles(self, image_id='default'):
        # cmd = sql.SQL(
        #     """SELECT image_id, affordance, data, tagger_id FROM screenshots
        #     WHERE image_id = %(image_id)s ORDER BY tagger_id, affordance;
        #     """
        # )
        print('getting unique tiles for image: ', image_id)
        res = yield self.get_resource_by_id(table='screenshots', col='image_id', resource_id=image_id)
        record = res[0]
        mapper = {
                'data': record['data'],
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

        meta = {i: mapper[i] for i in mapper if i not in ['image_id', 'data', 'game']}
        print("Untagged Image data retrieved image_id: {}".format(image_id))
        print(f'image meta info: {meta}')

        unique_tiles = unique_tiles_using_meta(
            mapper['data'], **meta)
        print(len(unique_tiles))
        out = yield self.get_tile_ids(unique_tiles, mapper['game'])
        # output = unique_tiles_using_meta()
        return unique_tiles
        # return self.dbpool.runQuery(cmd, {"image_id":image_id})

    def tileJSON(self, results, request):
        request.setHeader('Content-Type', 'application/json')
        responseJSON = []
        for record in results:
            mapper = {
                    'tile_id': record['tile_id'],
                    'game': record['game'],
                    'width': record['width'],
                    'height': record['height'],
                }
            data = record['data']
            # enc = base64.b64encode(data)
            # strf = enc.decode('utf-8')
            strf = b64_string(data)
            mapper['data'] = strf
            # if record['affordance'] == 'solid':
            responseJSON.append(mapper)
        return json.dumps(responseJSON)

    @inlineCallbacks
    def get_tile_ids(self, unique_tiles, game):
        print('gettin ids')
        # tile_data = yield treq.get(self.BASE_URL+'/tiles', params={'game': game})
        # tile_data = yield tile_data.json()
        tile_data = yield self.get_tiles_by_game(game)

        print('tile_data got')
        known_game_tiles = yield self.tileJSON(tile_data, None)
        print('known tiles got')
        tiles_to_tag = {}
        print('LEN KNOWN TILES: {}'.format(len(known_game_tiles)))
        hit_ctr = 0
        miss_ctr = 0
        for idx, screenshot_tile in enumerate(unique_tiles):
            to_compare = screenshot_tile['tile_data']
            is_in_db = False
            for tile_info in known_game_tiles:
                # cv_img, encoded_img = P.from_data_to_cv(tile_info['data'])
                # err = P.mse(to_compare, (cv_img))
                # if err < 0.001:
                #     is_in_db = True
                #     hit_ctr += 1
                #     # print("MATCHED {}".format(tile_info['tile_id']))
                #     # print("NUM LOCS {}".format(
                #     #     len(screenshot_tile['locations'])))
                #     tiles_to_tag['tile_{}'.format(idx)] = {
                #         'tile_id': tile_info['tile_id'],
                #         'tile_data': b64_string(P.from_cv_to_bytes(to_compare)),
                #         'locations': screenshot_tile['locations']
                #         }
                #     break
                b64_tile = tile_info['data']
                # print(b64_tile)
                # print('.')
                # print(to_compare)
                # print('...')
                if b64_tile == to_compare:
                    is_in_db = True
                    hit_ctr += 1
                    # print("MATCHED {}".format(tile_info['tile_id']))
                    # print("NUM LOCS {}".format(
                    #     len(screenshot_tile['locations'])))
                    tiles_to_tag['tile_{}'.format(idx)] = {
                        'tile_id': tile_info['tile_id'],
                        'tile_data': to_compare,
                        'locations': screenshot_tile['locations']
                        }
                    break
            if not is_in_db:
                print("TILE NOT MATCHED IN DB")
                miss_ctr += 1
                tiles_to_tag['tile_{}'.format(idx)] = {
                    'tile_id': -1,
                    'tile_data': to_compare,
                    'locations': screenshot_tile['locations']
                    }
            # idx = 0
            # if idx == -1:
            #     print('NEW TILE FOUND')
            #     height, width, channels = screenshot_tile['tile_data'].shape
            #     tile_data = P.from_cv_to_bytes(screenshot_tile['tile_data'])
            #     db.insert_tile(game, width, height, tile_data)
        print(f'db tile hits: {hit_ctr}, misses: {miss_ctr}')
        return tiles_to_tag

    def get_game_names(self):
        cmd = sql.SQL(
            """SELECT DISTINCT game FROM screenshots;
            """
        )
        return self.dbpool.runQuery(cmd)


    def get_tile_affordances(self, tile_id='default'):
        cmd = sql.SQL(
            """SELECT * FROM tile_tags
            WHERE tile_id = %(tile_id)s;
            """
        )
        return self.dbpool.runQuery(cmd, {"tile_id":tile_id})

    def get_screenshots_by_game(self, game='default'):
        cmd = sql.SQL(
            """SELECT * FROM screenshots
            WHERE game = %(game)s;
            """
        )
        return self.dbpool.runQuery(cmd, {"game":game})

    def get_tiles_by_game(self, game='default'):
        cmd = sql.SQL(
            """SELECT * FROM tiles
            WHERE game = %(game)s;
            """
        )
        return self.dbpool.runQuery(cmd, {"game":game})


    def get_sprites_by_game(self, game='default'):
        cmd = sql.SQL(
            """SELECT * FROM sprites
            WHERE game = %(game)s;
            """
        )
        return self.dbpool.runQuery(cmd, {"game":game})


    def check_uuid_in_table(self, table='default', id='default'):
        cmd = sql.SQL(
            """SELECT EXISTS(SELECT 1 FROM {} where image_id = %(id)s) as "exists"
            """
        ).format(sql.Identifier(table))
        return self.dbpool.runQuery(cmd, {"id":id})


    def check_tagger_tagged_screenshot(self, image_id='defalut', tagger_id='default'):
        cmd = sql.SQL(
            """SELECT EXISTS(SELECT 1 FROM screenshot_tags where image_id = %(image_id)s and tagger_id = %(tagger_id)s) as "exists"
            """
        )
        return self.dbpool.runQuery(cmd, {"image_id":image_id, "tagger_id":tagger_id})


class VGAC_DBAPI(object):

    app = Klein()
    db = VGAC_Database()
    deployment = str(os.getenv('TARGET', 'dev'))
    if deployment == 'staging':
        print('from staging dbapi')
        postgres_host = 'vgac-db-staging'
    else:
        postgres_host = 'vgac-db'
        print('from live dbapi')

    @app.route('/')
    def test(self, request):
        return json.dumps({'message': f'{self.deployment}: Hello From VGAC DBAPI'})

    @app.route('/test')
    def base2(self, request):
        return json.dumps({'message': f'{self.deployment}: dbapi test'})


    #--------- Routes ---------#
    @app.route('/insert', methods=['POST'])
    def insert(self, request):
        print(type(request.args))
        data = json.loads(request.content.read())
        tagger_id = data.get('tagger_id', [None])
        image_id = data.get('image_id', [None])
        print(f'RECEIVED TAGS FROM: {tagger_id} FOR IMAGE: {image_id}')
        # print(f'data: {data}')
        tiles = (data.get('tiles', [None]))
        # print(tiles)

        insert_count = 0
        skip_count = 0
        first = True
        for tile in tiles:
            tile_id = tiles[tile]['tile_id']
            if not isinstance(tile_id, int):
                to_insert = {
                    'tile_id': tile_id,
                    'tagger_id': tagger_id,
                    'solid': bool(int(tiles[tile]['solid'])),
                    'movable': bool(int(tiles[tile]['movable'])),
                    'destroyable': bool(int(tiles[tile]['destroyable'])),
                    'dangerous': bool(int(tiles[tile]['dangerous'])),
                    'gettable': bool(int(tiles[tile]['gettable'])),
                    'portal': bool(int(tiles[tile]['portal'])),
                    'usable': bool(int(tiles[tile]['usable'])),
                    'changeable': bool(int(tiles[tile]['changeable'])),
                    'ui': bool(int(tiles[tile]['ui'])),
                    'permeable': bool(int(tiles[tile]['permeable'])),
                    'dt': datetime.now()
                }
                if first:
                    print('SAMPLE DB INSERT TILE TAGS ID: {}'.format(
                        tile_id))
                    print(f'to insert: {to_insert}')
                    first = False
                # db.insert_tile_tag(tiles[tile]['tile_id'], tagger, tiles[tile]['solid'], tiles[tile]['movable'],
                #                    tiles[tile]['destroyable'], tiles[tile]['dangerous'], tiles[tile]['gettable'], tiles[tile]['portal'], tiles[tile]['usable'], tiles[tile]['changeable'], tiles[tile]['ui'])
                insert_count += 1
                self.db.insert_tile_tag(to_insert)
            else:
                skip_count += 1

        print('INSERTED {} Tile Tags. SKIPPED {} Tiles. SUBMITTED: {}'.format(
            insert_count, skip_count, len(tiles)))

        tag_images = data['tag_images']
        affordance_count = 0
        # first = True
        count = 0
        for affordance in tag_images:
            b64_channel = tag_images[affordance]
            # print(b64_channel)
            # print('unbase 64', type(b64_channel))
            data_tag = b64_channel[:22]
            if data_tag == IMAGE_BASE[:22]:
                b64_channel = b64_channel[22:]
                tag_data_bytes = base64.b64decode(b64_channel)
                # affordance_num = P.AFFORDANCES.index(affordance)

                # print('DB INSERT IMAGE TAGS for afford: {}, data type: {}'.format(
                #     affordance, type(tag_data_bytes)))

                to_insert = {
                    'image_id': image_id,
                    'affordance': affordance,
                    'tagger_id': tagger_id,
                    'data': tag_data_bytes,
                    'dt': datetime.now(),
                }
                # print(f'to insert: {to_insert}')
                self.db.insert_screenshot_tag(to_insert)
                count += 1
            else:
                print(f'Wrong Data tag on {affordance} b64 prefix: {data_tag}')

            # db.insert_screenshot_tag(image_id, affordance_num, tagger, to_insert)
        print(f'num affordance channels inserted: {count}')

        return json.dumps(dict(the_data=data), indent=4)
        # d = self.db.insert(first_name, last_name, age)
        # d.addCallback(self.onSuccess, request, 'Insert success')
        # d.addErrback(self.onFail, request, 'Insert failed')
        # return d

    @app.route('/screenshot', methods=['GET'])
    def randScreenshot(self, request):
        str_args = dict_decode(request.args)
        tagger_id = str_args.get('tagger', ['default'])[0]
        d = self.db.get_untagged_screenshot(tagger_id=tagger_id)
        d.addCallback(self.screenshotJSON, request)
        d.addErrback(self.onFail, request, 'Failed to query db')
        return d

    # @app.route('/screenshots/<string:tagger_id>', methods=['GET'])
    # def queryUn(self, request, tagger_id):
    #     d = self.db.get_untagged_screenshot(tagger_id=tagger_id)
    #     d.addCallback(self.screenshotJSON, request)
    #     d.addErrback(self.onFail, request, 'Failed to query db')
    #     return d

    @app.route('/screenshots/<string:image_id>', methods=['GET'])
    def screenshotById(self, request, image_id):
        d = self.db.get_resource_by_id(table='screenshots', col='image_id', resource_id=image_id)
        d.addCallback(self.screenshotJSON, request)
        d.addErrback(self.onFail, request, 'Failed to query db')
        return d

    @app.route('/screenshot_tags/<string:image_id>', methods=['GET'])
    def tagsById(self, request, image_id):
        d = self.db.get_screenshot_affordances(image_id=image_id)
        d.addCallback(self.screenshot_tagJSON, request)
        d.addErrback(self.onFail, request, 'Failed to query db')
        return d

    @app.route('/screenshot_tiles/<string:image_id>', methods=['GET'])
    @inlineCallbacks
    def tilesByImage(self, request, image_id):
        # d = self.db.get_unique_tiles(image_id=image_id)
        res = yield self.db.get_resource_by_id(table='screenshots', col='image_id', resource_id=image_id)
        record = res[0]
        mapper = {
                'data': record['data'],
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

        meta = {i: mapper[i] for i in mapper if i not in ['image_id', 'data', 'game']}
        unique_tiles = unique_tiles_using_meta(mapper['data'], **meta)
        print('unique tiles got')
        out_tiles = yield (self.get_tile_ids(unique_tiles, mapper['game']))
        # out_tiles.addCallback(self.tile_locationJSON, request)
        # out_tiles.addErrback(self.onFail, request, 'Failed to query db')
        return json.dumps(out_tiles)

    @inlineCallbacks
    def get_tile_ids(self, unique_tiles, game):
        print('gettin ids')
        # tile_data = yield treq.get(self.BASE_URL+'/tiles', params={'game': game})
        # tile_data = yield tile_data.json()
        tile_data = yield self.db.get_tiles_by_game(game)

        print('tile_data got')
        # known_game_tiles = yield self.tileJSON(tile_data, None)
        known_game_tiles = []
        for record in tile_data:
            mapper = {
                    'tile_id': record['tile_id'],
                }
            data = record['data']
            # enc = base64.b64encode(data)
            # strf = enc.decode('utf-8')
            strf = b64_string(data)
            mapper['data'] = strf
            # if record['affordance'] == 'solid':
            known_game_tiles.append(mapper)
        print('known tiles got')
        tiles_to_tag = {}
        print('LEN KNOWN TILES: {}'.format(len(known_game_tiles)))
        print('LEN UNIQUE: {}'.format(len(unique_tiles)))
        hit_ctr = 0
        miss_ctr = 0
        for idx, screenshot_tile in enumerate(unique_tiles):
            to_compare = screenshot_tile['tile_data']
            is_in_db = False
            for tile_info in known_game_tiles:
                # cv_img, encoded_img = P.from_data_to_cv(tile_info['data'])
                # err = P.mse(to_compare, (cv_img))
                # if err < 0.001:
                #     is_in_db = True
                #     hit_ctr += 1
                #     # print("MATCHED {}".format(tile_info['tile_id']))
                #     # print("NUM LOCS {}".format(
                #     #     len(screenshot_tile['locations'])))
                #     tiles_to_tag['tile_{}'.format(idx)] = {
                #         'tile_id': tile_info['tile_id'],
                #         'tile_data': b64_string(P.from_cv_to_bytes(to_compare)),
                #         'locations': screenshot_tile['locations']
                #         }
                #     break
                b64_tile = tile_info['data']
                # print(b64_tile)
                # print('.')
                # print(to_compare)
                # print('...')
                if b64_tile == to_compare:
                    is_in_db = True
                    # print("TILE MATCHED")

                    hit_ctr += 1
                    # print("MATCHED {}".format(tile_info['tile_id']))
                    # print("NUM LOCS {}".format(
                    #     len(screenshot_tile['locations'])))
                    tiles_to_tag['tile_{}'.format(idx)] = {
                        'tile_id': tile_info['tile_id'],
                        'tile_data': to_compare,
                        'locations': screenshot_tile['locations']
                        }
                    break
            if not is_in_db:
                # print("TILE NOT MATCHED IN DB")
                miss_ctr += 1
                tiles_to_tag['tile_{}'.format(idx)] = {
                    'tile_id': -1,
                    'tile_data': to_compare,
                    'locations': screenshot_tile['locations']
                    }
            # print('end loop')
            # idx = 0
            # if idx == -1:
            #     print('NEW TILE FOUND')
            #     height, width, channels = screenshot_tile['tile_data'].shape
            #     tile_data = P.from_cv_to_bytes(screenshot_tile['tile_data'])
            #     db.insert_tile(game, width, height, tile_data)
        # print('done')
        # print('done 2')
        print(f'db tile hits: {hit_ctr}, misses: {miss_ctr}')
        # print('wtf')
        return tiles_to_tag

    @app.route('/tiles/<string:tile_id>', methods=['GET'])
    def tileById(self, request, tile_id):
        d = self.db.get_resource_by_id(table='tiles',col='tile_id', resource_id=tile_id)
        d.addCallback(self.tileJSON, request)
        d.addErrback(self.onFail, request, 'Failed to query db')
        return d

    @app.route('/tiles/<string:tile_id>/affordances', methods=['GET'])
    def tileAffordanceById(self, request, tile_id):
        d = self.db.get_tile_affordances(tile_id=tile_id)
        d.addCallback(self.tileJSON, request)
        d.addErrback(self.onFail, request, 'Failed to query db')
        return d

    @app.route('/tiles', methods=['GET'])
    def tilesBase(self, request):
        str_args = dict_decode(request.args)
        game_name = str_args.get('game', ['default'])[0]

        d = self.db.get_tiles_by_game(game_name)
        d.addCallback(self.tileJSON, request)
        d.addErrback(self.onFail, request, 'Failed to query db')
        return d



    #---------- Callbacks -----------#
    def onSuccess(self, result, request, msg):
        request.setResponseCode(201)
        response = {'message': msg}
        return json.dumps(response)

    def onFail(self, failure, request, msg):
        request.setResponseCode(417)
        response = {'message': msg}
        print(failure)
        return json.dumps(response)

    def screenshotJSON(self, results, request):
        request.setHeader('Content-Type', 'application/json')
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
            # enc = base64.b64encode(data)
            # strf = enc.decode('utf-8')
            strf = b64_string(data)
            mapper['data'] = strf
            responseJSON.append(mapper)
        return json.dumps(responseJSON)

    def screenshot_tagJSON(self, results, request):
        request.setHeader('Content-Type', 'application/json')
        responseJSON = []
        for record in results:
            mapper = {
                    'image_id': record['image_id'],
                    'affordance': record['affordance'],
                    'tagger_id': record['tagger_id'],
                }
            data = record['data']
            # enc = base64.b64encode(data)
            # strf = enc.decode('utf-8')
            strf = b64_string(data)
            mapper['data'] = strf
            # if record['affordance'] == 'solid':
            responseJSON.append(mapper)
        return json.dumps(responseJSON)

    def tileJSON(self, results, request):
        request.setHeader('Content-Type', 'application/json')
        responseJSON = []
        for record in results:
            mapper = {
                    'tile_id': record['tile_id'],
                    'game': record['game'],
                    'width': record['width'],
                    'height': record['height'],
                }
            data = record['data']
            # enc = base64.b64encode(data)
            # strf = enc.decode('utf-8')
            strf = b64_string(data)
            mapper['data'] = strf
            # if record['affordance'] == 'solid':
            responseJSON.append(mapper)
        return json.dumps(responseJSON)

    def tile_locationJSON(self, results, request):
        request.setHeader('Content-Type', 'application/json')
        return json.dumps(results)
        # responseJSON = []
        # for record in results:
        #     mapper = {
        #             'tile_id': record['tile_id'],
        #             'game': record['game'],
        #             'width': record['width'],
        #             'height': record['height'],
        #         }
        #     data = record['data']
        #     # enc = base64.b64encode(data)
        #     # strf = enc.decode('utf-8')
        #     strf = b64_string(data)
        #     mapper['data'] = strf
        #     # if record['affordance'] == 'solid':
        #     responseJSON.append(mapper)
        # return json.dumps(responseJSON)

if __name__ == '__main__':
    webapp = VGAC_DBAPI()
    print('Begin DBAPI')
    webapp.app.run("0.0.0.0", 5000)
