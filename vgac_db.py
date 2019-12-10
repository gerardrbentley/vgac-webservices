import json
import base64

from klein import Klein
from twisted.enterprise import adbapi
from twisted.internet import reactor
from psycopg2.extras import DictCursor
from psycopg2 import sql

class VGAC_Database(object):

    def succConnectionPool(conn):
        pid = conn.get_backend_pid()
        print("New DB connection created (backend PID {})".format(pid))

    dbpool = adbapi.ConnectionPool('psycopg2',
                                    host = '192.168.99.101',
                                    port = 5432,
                                    database = 'postgres',
                                    user = 'postgres',
                                    password = '',
                                    cp_min = 3,
                                    cp_max = 10,
                                    cp_noisy = True,
                                    cp_openfun = succConnectionPool,
                                    cp_reconnect = True,
                                    cp_good_sql = "SELECT 1",
                                    cursor_factory = DictCursor)
    table = 'screenshots'
    # dbpool.start()

    def _insert(self, cursor, first, last, age):
        insert_stmt = 'INSERT INTO %s (first_name, last_name, age) VALUES ("%s", "%s", %d)' % (self.table, first, last, age)
        cursor.execute(insert_stmt)

    def insert(self, first, last, age):
        return self.dbpool.runInteraction(self._insert, first, last, age)

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

    def get_screenshot_by_id(self, image_id='default'):
        cmd = sql.SQL(
            """SELECT * FROM screenshots
            WHERE image_id = %(image_id)s;
            """
        )
        return self.dbpool.runQuery(cmd, {"image_id":image_id})

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


class VGAC_App(object):

    app = Klein()
    db = VGAC_Database()

    #--------- Routes ---------#
    # @app.route('/insert', methods=['POST'])
    def insert(self, request):
        first_name = request.args.get('fname', [None])[0]
        last_name = request.args.get('lname', [None])[0]
        age = int(request.args.get('age', [0])[0])

        d = self.db.insert(first_name, last_name, age)
        d.addCallback(self.onSuccess, request, 'Insert success')
        d.addErrback(self.onFail, request, 'Insert failed')
        return d

    @app.route('/screenshot', methods=['GET'])
    def randScreenshot(self, request):
        d = self.db.get_random_screenshot()
        d.addCallback(self.screenshotJSON, request)
        d.addErrback(self.onFail, request, 'Failed to query db')
        return d

    @app.route('/untagged_screenshot/<string:tagger_id>', methods=['GET'])
    def queryUn(self, request, tagger_id):
        d = self.db.get_untagged_screenshot(tagger_id=tagger_id)
        d.addCallback(self.screenshotJSON, request)
        d.addErrback(self.onFail, request, 'Failed to query db')
        return d

    @app.route('/screenshot/<string:image_id>', methods=['GET'])
    def screenshotById(self, request, image_id):
        d = self.db.get_screenshot_by_id(image_id=image_id)
        d.addCallback(self.screenshotJSON, request)
        d.addErrback(self.onFail, request, 'Failed to query db')
        return d

    @app.route('/screenshot_tags/<string:image_id>', methods=['GET'])
    def tagsById(self, request, image_id):
        d = self.db.get_screenshot_affordances(image_id=image_id)
        d.addCallback(self.affordancesJSON, request)
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
            enc = base64.b64encode(data)
            strf = enc.decode('utf-8')
            mapper['data'] = strf
            responseJSON.append(mapper)
        return json.dumps(responseJSON)

    def affordancesJSON(self, results, request):
        request.setHeader('Content-Type', 'application/json')
        responseJSON = []
        for record in results:
            mapper = {
                    'image_id': record['image_id'],
                    'affordance': record['affordance'],
                    'tagger_id': record['tagger_id'],
                }
            data = record['data']
            enc = base64.b64encode(data)
            strf = enc.decode('utf-8')
            mapper['data'] = strf
            if record['affordance'] == 'destroyable':
                responseJSON.append(mapper)
        return json.dumps(responseJSON)

if __name__ == '__main__':
    webapp = VGAC_App()
    webapp.app.run('localhost', 5000)
