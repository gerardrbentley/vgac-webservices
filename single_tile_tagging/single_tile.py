from klein import Klein
from twisted.web.static import File
from twisted.internet.defer import inlineCallbacks

import treq

import json
import os
import base64
import random

def dict_decode(bytes_keys_values):
    return {k.decode('utf-8'):list(map(lambda x: x.decode('utf-8'), v)) for (k,v) in bytes_keys_values.items()}

class SingleTileTagger(object):
    app = Klein()

    def __init__(self):
        self.deployment = str(os.getenv('TARGET', 'dev'))
        self.BASE_URL = str(os.getenv('HOST', 'http://dbapi:5000'))
        #TODO: ACTUALLY POINT AT RIGHT DB
        if self.deployment == 'staging':
            print('from staging expert')
            # self.BASE_URL = self.BASE_URL + '/staging'
        else:
            print('from live expert')

    @app.route("/test")
    def test(self, request):
        return json.dumps({'message': f'single tile test from {self.deployment}'})

    @app.route("/testjs")
    def testjs(self, request):
        return File('./')

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
            print("NO TAGGER ID IN GET IMAGE")

        print('Fetching image for tagger: {}'.format(tagger_id))

        image_data = yield treq.get(self.BASE_URL+'/screenshot', params={'tagger': tagger_id})
        image_data = yield image_data.json()
        image_data = image_data[0]

        image_id = image_data['image_id']
        game = image_data['game']
        image_string = image_data['data']

        y_offset = image_data['y_offset']
        x_offset = image_data['x_offset']

        unique_tiles = yield treq.get(self.BASE_URL+'/screenshot_tiles/'+image_id)
        tiles_to_tag = yield unique_tiles.json()

        print('Tiles id-d, LEN: {}'.format(len(tiles_to_tag)))
        num_tiles = len(tiles_to_tag)
        tile_idx = random.randint(0,num_tiles-1)
        tile_id = tiles_to_tag[tile_idx]['tile_id']
        print(f'test idx: {tile_idx}, test id: {tile_id}')
        while isinstance(tile_id, int):
            tile_idx = random.randint(0,num_tiles-1)
            tile_id = tiles_to_tag[tile_idx]['tile_id']
            print(f'bad id, test idx: {tile_idx}, test id: {tile_id}')

        output = {
            'image': image_string,
            'image_id': image_id,
            'tile': tiles_to_tag[tile_idx],
        }
        print('send single tile with image')
        return json.dumps({'output': output})


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

if __name__ == '__main__':
    webapp = SingleTileTagger()
    webapp.app.run('0.0.0.0', 5000)
