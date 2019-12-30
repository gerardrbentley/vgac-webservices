import json
import base64
from datetime import datetime
import os

from klein import Klein
from twisted.web.static import File
from twisted.enterprise import adbapi
from psycopg2.extras import DictCursor
from psycopg2 import sql

def dict_decode(bytes_keys_values):
    return {k.decode('utf-8'):list(map(lambda x: x.decode('utf-8'), v)) for (k,v) in bytes_keys_values.items()}

IMAGE_BASE = "data:image/png;base64,{}"
def b64_string(data):
    return IMAGE_BASE.format((base64.b64encode(data)).decode('utf-8'))

def logInsert(op):
    print('logInsert')
    if op:
        print(op)
    else:
        print("no operation done")
def logErr(op):
    print('logErr')
    if op:
        print(op)
    else:
        print("no operation done, error")


class VGAC_Database(object):

    def succConnectionPool(conn):
        pid = conn.get_backend_pid()
        print("New DB connection created (backend PID {})".format(pid))
    keys = {    'host': os.getenv('POSTGRES_HOST', 'vgac-db'),
        'port': os.getenv('POSTGRES_PORT', '5432'),
        'database': os.getenv('POSTGRES_DB', 'vgac-db'),
        'user': os.getenv('POSTGRES_USER', 'faim-lab'),
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
    table = 'screenshots'
    # dbpool.start()


    def _insert(self, cursor, first, last, age):
        insert_stmt = 'INSERT INTO %s (first_name, last_name, age) VALUES ("%s", "%s", %d)' % (self.table, first, last, age)
        cursor.execute(insert_stmt)

    def insert(self, first, last, age):
        return self.dbpool.runInteraction(self._insert, first, last, age)

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
        print('Insert Screenshot tag Called and Ended')

    def insert_tile(self, kwargs):
        cmd = sql.SQL(
            """INSERT INTO tiles(tile_id, game, width, height, created_on, data)
            VALUES(%(tile_id)s, %(game)s, %(width)s, %(height)s, %(dt)s, %(data)s)
            RETURNING tile_id
            """
        )
        self.dbpool.runOperation(cmd, kwargs).addCallbacks(logInsert, logErr)
        print('Insert Tile Called and Ended')

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
        print('Insert Tile Tag Called and Ended')

    def queryAll(self):
        select_stmt = sql.SQL("SELECT * FROM {}").format(sql.Identifier(self.table))
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

    @app.route('/devstatic/', branch=True)
    def static(self, request):
        return File("./static")

    @app.route('/')
    def test(self, request):
        return json.dumps({'message': 'Hello World'})

    #--------- Routes ---------#
    @app.route('/insert', methods=['POST'])
    def insert(self, request):
        print(type(request.args))
        data = json.loads(request.content.read())
        tagger_id = data.get('tagger_id', [None])
        image_id = data.get('image_id', [None])
        print(f'RECEIVED TAGS FROM: {tagger_id} FOR IMAGE: {image_id}')
        print(f'data: {data}')
        tiles = (data.get('tiles', [None]))
        print(tiles)

        insert_count = 0
        skip_count = 0
        for tile in tiles:
            tile_id = tiles[tile]['tile_id']
            if not isinstance(tile_id, int):
                print('DB INSERT TILE TAGS ID: {}'.format(
                    tile_id))

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
                print(f'to insert: {to_insert}')
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
        for affordance in tag_images:
            b64_channel = tag_images[affordance]
            print(b64_channel)
            print('unbase 64', type(b64_channel))
            b64_channel = b64_channel[22:]
            tag_data_bytes = base64.b64decode(b64_channel)
            # affordance_num = P.AFFORDANCES.index(affordance)
            print('DB INSERT IMAGE TAGS for afford: {}, data type: {}'.format(
                affordance, type(tag_data_bytes)))

            to_insert = {
                'image_id': image_id,
                'affordance': affordance,
                'tagger_id': tagger_id,
                'data': tag_data_bytes,
                'dt': datetime.now(),
            }
            print(f'to insert: {to_insert}')
            self.db.insert_screenshot_tag(to_insert)
            # db.insert_screenshot_tag(image_id, affordance_num, tagger, to_insert)
        print(f'num affordance channels: {len(tag_images)}')

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

if __name__ == '__main__':
    webapp = VGAC_DBAPI()
    print('Let Us Begin')
    webapp.app.run("0.0.0.0", 5000)
