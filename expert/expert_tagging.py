from klein import Klein
from twisted.web.static import File
from twisted.internet.defer import inlineCallbacks
from twisted.logger import Logger

import treq

import json
import os
import base64


def err_with_logger(the_logger, err_str):
    the_logger.error(err_str)
    return json.dumps({'output': {'status': 500, 'message': err_str}})


def dict_decode(bytes_keys_values):
    return {k.decode('utf-8'): list(map(lambda x: x.decode('utf-8'), v)) for (k, v) in bytes_keys_values.items()}


class ExpertTagger(object):
    app = Klein()
    log = Logger()

    def __init__(self):
        self.deployment = str(os.getenv('TARGET', 'dev'))
        self.BASE_URL = 'http://dbapi:5000'
        if self.deployment == 'staging':
            self.BASE_URL = 'http://dbapi-staging:5000'
        self.log.info(
            f'Expert Tagger on {self.deployment} running, dbapi: {self.BASE_URL}')

    #--------- Debug ----------#
    @app.route("/test")
    def test(self, request):
        return json.dumps({'message': f'expert test from {self.deployment}'})

    @app.route("/")
    def base(self, request):
        return json.dumps({'message': f'expert base from {self.deployment}'})

    #--------- Routes ---------#
    @app.route("/get_image", methods=['GET'])
    @inlineCallbacks
    def get_image_to_tag(self, request):
        """Return random image, list of unique tiles and locations"""
        str_args = dict_decode(request.args)
        tagger_id = str_args.get(
            'tagger', ['default-tagger'])[0]
        if tagger_id == 'default-tagger':
            self.log.info("NO TAGGER ID IN GET IMAGE")

        self.log.info(
            f'Fetching for {tagger_id}: Expert Tagger on {self.deployment}, dbapi: {self.BASE_URL}')

        try:
            image_data = yield treq.get(self.BASE_URL+'/screenshots', params={'tagger': tagger_id})
        except:
            return err_with_logger(self.log, f'Fetch at {self.BASE_URL}/screenshots failed')
        try:
            image_data = yield image_data.json()
            self.log.info(f'image data type: {type(image_data)}')
            image_data = image_data[0]
        except:
            return err_with_logger(self.log, f'Bad json from {self.BASE_URL}/screenshots')

        # image_data = fetch_json_with_logger(self.log, self.BASE_URL+'/screenshot', params={'tagger': tagger_id})
        self.log.info(f'image data type: {type(image_data)}')
        image_id = image_data['image_id']

        self.log.info(f'Fetching tiles for image: {image_id}')
        try:
            unique_tiles = yield treq.get(f'{self.BASE_URL}/screenshots/{image_id}/tiles')
        except:
            return err_with_logger(self.log, f'Fetch at {self.BASE_URL}/screenshots/{image_id}/tiles failed')
        try:
            textures_to_tag = yield unique_tiles.json()
        except:
            return err_with_logger(self.log, f'Bad json from {self.BASE_URL}/screenshots/{image_id}/tiles')

        output = {
            'image': image_data['data'],
            'image_id': image_id,
            'textures': textures_to_tag,
            'y_offset': image_data['y_offset'],
            'x_offset': image_data['x_offset']
        }
        self.log.info(
            f'Good Fetch: Expert Tagger on {self.deployment}, dbapi: {self.BASE_URL}')
        return json.dumps({'output': output})


if __name__ == '__main__':
    webapp = ExpertTagger()
    webapp.app.run('0.0.0.0', 5000)
