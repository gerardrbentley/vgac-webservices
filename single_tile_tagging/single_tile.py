from klein import Klein
from twisted.web.static import File
from twisted.internet.defer import inlineCallbacks
from twisted.logger import Logger

import treq

import json
import os
import base64
import random

def err_with_logger(the_logger, err_str):
    the_logger.error(err_str)
    return json.dumps({'output': {'status': 500, 'message': err_str}})

def dict_decode(bytes_keys_values):
    return {k.decode('utf-8'):list(map(lambda x: x.decode('utf-8'), v)) for (k,v) in bytes_keys_values.items()}

class SingleTileTagger(object):
    app = Klein()
    log = Logger()

    def __init__(self):
        self.deployment = str(os.getenv('TARGET', 'dev'))
        self.DATABASE_URL = 'http://dbapi:5000'
        if self.deployment == 'staging':
            self.DATABASE_URL = 'http://dbapi-staging:5000'
        self.log.info(f'Single Tile Tagger on {self.deployment} running, dbapi: {self.DATABASE_URL}')

    #--------- Debug ----------#
    @app.route("/test")
    def test(self, request):
        return json.dumps({'message': f'single tile test from {self.deployment}'})

    @app.route("/testhtml")
    def testhtml(self, request):
        return File('./single_tile_page.html')

    @app.route("/testjs")
    def testhtml(self, request):
        return File('./single_tile.js')

    @app.route("/")
    def base(self, request):
        return json.dumps({'message': f'single tile base from {self.deployment}'})

    #--------- Routes ---------#
    @app.route("/get_image", methods=['GET'])
    @inlineCallbacks
    def get_image_with_tile(self, request):
        """Return random image and one tile and its locations in the image"""
        str_args = dict_decode(request.args)
        tagger_id = str_args.get(
            'tagger', ['default-tagger'])[0]
        if tagger_id == 'default-tagger':
            self.log.info("NO TAGGER ID IN GET IMAGE")

        self.log.info(f'Fetching for {tagger_id}: Single Tile Tagger on {self.deployment}, dbapi: {self.DATABASE_URL}')

        try:
            image_data = yield treq.get(self.DATABASE_URL+'/screenshot', params={'tagger': tagger_id})
        except:
            return err_with_logger(self.log, f'Fetch at {self.DATABASE_URL}/screenshot failed')
        try:
            image_data = yield image_data.json()
            self.log.info(f'image data type: {type(image_data)}')
            if isinstance(image_data, dict):
                self.log.info(f'image data keys: {list(image_data.keys())}')
            image_data = image_data[0]
        except:
            return err_with_logger(self.log, f'Bad json from {self.DATABASE_URL}/screenshot')
        
        self.log.info(f'image data type: {type(image_data)}')
        if isinstance(image_data, dict):
            self.log.info(f'image data keys: {list(image_data.keys())}')
        
        image_id = image_data['image_id']

        self.log.info(f'Fetching tiles for image: {image_id}')
        try:
            unique_tiles = yield treq.get(self.DATABASE_URL+'/screenshot_tiles/'+image_id)
        except:
            return err_with_logger(self.log, f'Fetch at {self.DATABASE_URL}/screenshot_tiles/{image_id} failed')
        try:
            tiles_to_tag = yield unique_tiles.json()
        except:
            return err_with_logger(self.log, f'Bad json from {self.DATABASE_URL}/screenshot_tiles/{image_id}')

        self.log.info(f'tiles type: {type(tiles_to_tag)}')
        if isinstance(tiles_to_tag, dict):
            self.log.info(f'tiles keys: {list(tiles_to_tag.keys())}')

        self.log.info('Tiles in image, LEN: {}'.format(len(tiles_to_tag)))
        choice_keys = list(tiles_to_tag.keys())
        random.shuffle(choice_keys)

        for tile_key in choice_keys:
            tile_id = tiles_to_tag[tile_key]['tile_id']
            if not isinstance(tile_id, int):
                break
            self.log.info(f'bad id, test idx: {tile_key}, test id: {tile_id}')

        if isinstance(tile_id, int):
            return err_with_logger(self.log, f'No tiles in db for image from {self.DATABASE_URL}/screenshot_tiles/{image_id}')

        output = {
            'image': image_data['data'],
            'image_id': image_id,
            'tile': tiles_to_tag[tile_key],
        }
        self.log.info(f'Good Fetch: Single Tile Tagger on {self.deployment}, dbapi: {self.DATABASE_URL}')
        return json.dumps({'output': output})

if __name__ == '__main__':
    webapp = SingleTileTagger()
    webapp.app.run('0.0.0.0', 5000)
