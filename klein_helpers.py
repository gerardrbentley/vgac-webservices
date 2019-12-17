import base64
import numpy as np
import cv2

def dict_decode(bytes_keys_values):
    return {k.decode('utf-8'):list(map(lambda x: x.decode('utf-8'), v)) for (k,v) in bytes_keys_values.items()}

def unique_tiles_using_meta(image, y_offset=0, x_offset=0, width=256, height=224, crop_l=0, crop_r=0, crop_t=0, crop_b=0, ui_x=0, ui_y=0, ui_height=0, ui_width=0):
    print('Finding unique tiles in img')
    grid_size = 8

    if isinstance(image, str):
        print('pass in string')
        myBytes = base64.b64decode(image)
        print(type(myBytes))
    else:
        print('not string img', type(image))
        myBytes = image.tobytes()
    print(type(myBytes))
    encoded_img = np.frombuffer(myBytes, dtype=np.uint8)
    print(type(encoded_img), encoded_img.shape)
    image = cv2.imdecode(encoded_img, cv2.IMREAD_UNCHANGED)
    print(type(image))

    h, w, *_ = image.shape
    print(f'h: {h}, w: {w}')
    new_image = image[crop_t: h - crop_b, crop_l: w - crop_r, :]
    new_h, new_w, *_ = new_image.shape
    return []

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
                    'tile_data': template_np,
                    'locations': matches_dict
                    })
                tile_ctr += 1
            else:
                skip_ctr += 1

    print('VISITED {} tiles, sum of unique({}) + skip({}) = {}'.format(
        len(visited_locations), len(img_tiles), skip_ctr, (len(img_tiles)+skip_ctr)))
    print(img_tiles[0]['tile_data'].shape)
    return img_tiles
