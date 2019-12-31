from klein import Klein
from twisted.web.static import File
from twisted.internet.defer import inlineCallbacks

import treq

import json
import os
import base64

from klein_helpers import dict_decode, unique_tiles_using_meta

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

        meta = {i: image_data[i] for i in image_data if i
                != 'data' and i != 'game' and i != 'image_id'}
        y_offset = image_data['y_offset']
        x_offset = image_data['x_offset']
        print("Untagged Image data retrieved image_id: {}".format(image_id))
        print(f'image meta info: {meta}')

        unique_tiles = unique_tiles_using_meta(
            image_string, **meta)

        tiles_to_tag = yield self.get_tile_ids(unique_tiles, game)
        # map_dict(encode_tile_from_dict, tiles_to_tag)
        print("Unique TILES found: {}".format(len(unique_tiles)))
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

    @inlineCallbacks
    def get_tile_ids(self, unique_tiles, game):
        print('gettin ids')
        tile_data = yield treq.get(self.BASE_URL+'/tiles', params={'game': game})
        tile_data = yield tile_data.json()
        # print(tile_data)
        known_game_tiles = tile_data

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
                print(b64_tile)
                print('.')
                print(to_compare)
                print('...')
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
            enc = base64.b64encode(data)
            strf = enc.decode('utf-8')
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
            enc = base64.b64encode(data)
            strf = enc.decode('utf-8')
            mapper['data'] = strf
            # if record['affordance'] == 'solid':
            responseJSON.append(mapper)
        return json.dumps(responseJSON)

if __name__ == '__main__':
    webapp = ExpertTagger()
    webapp.app.run('0.0.0.0', 5000)
