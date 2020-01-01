from klein import Klein
from twisted.web.static import File
from twisted.internet.defer import inlineCallbacks

import treq

import json
import os
import base64

def dict_decode(bytes_keys_values):
    return {k.decode('utf-8'):list(map(lambda x: x.decode('utf-8'), v)) for (k,v) in bytes_keys_values.items()}

class ExpertTagger(object):
    app = Klein()

    def __init__(self):
        self.BASE_URL = str(os.getenv('HOST', 'http://dbapi:5000'))


    @app.route("/test")
    def test(self, request):
        return json.dumps({'message': 'expert test'})

    #--------- Routes ---------#
    @app.route("/get_image", methods=['GET'])
    @inlineCallbacks
    def get_image_to_tag(self, request):
        """Return random image, list of unique tiles and locations"""
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

        # meta = {i: image_data[i] for i in image_data if i
        #         != 'data' and i != 'game' and i != 'image_id'}
        y_offset = image_data['y_offset']
        x_offset = image_data['x_offset']
        # print("Untagged Image data retrieved image_id: {}".format(image_id))
        # print(f'image meta info: {meta}')
        #
        # unique_tiles = unique_tiles_using_meta(
        #     image_string, **meta)
        unique_tiles = yield treq.get(self.BASE_URL+'/screenshot_tiles/'+image_id)
        tiles_to_tag = yield unique_tiles.json()
        # tiles_to_tag = yield self.get_tile_ids(unique_tiles, game)
        # map_dict(encode_tile_from_dict, tiles_to_tag)
        # print("Unique TILES found: {}".format(len(unique_tiles)))
        print('Tiles id-d, LEN: {}'.format(len(tiles_to_tag)))

        # tags = P.load_label(image_file)
        # tag_images = P.numpy_to_images(tags)
        # map_dict(b64_string, tag_images)
        output = {
            'image': image_string,
            'image_id': image_id,
            'tiles': tiles_to_tag,
            'y_offset': y_offset,
            'x_offset': x_offset
        }
        print('base route ok')
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
    webapp = ExpertTagger()
    webapp.app.run('0.0.0.0', 5000)
