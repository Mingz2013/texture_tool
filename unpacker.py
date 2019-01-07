#!/usr/bin/env python
import json
import os
import sys
from xml.etree import ElementTree

from PIL import Image


def tree_to_dict(tree):
    d = {}
    for index, item in enumerate(tree):
        if item.tag == 'key':
            if tree[index + 1].tag == 'string':
                d[item.text] = tree[index + 1].text
            elif tree[index + 1].tag == 'true':
                d[item.text] = True
            elif tree[index + 1].tag == 'false':
                d[item.text] = False
            elif tree[index + 1].tag == 'integer':
                d[item.text] = int(tree[index + 1].text)
            elif tree[index + 1].tag == 'dict':
                d[item.text] = tree_to_dict(tree[index + 1])
    return d


def frames_from_data(filename, ext):
    data_filename = filename + ext
    if ext == '.plist':
        return frames_from_data_ext_plist(data_filename)

    # elif ext == '.json':
    #     return frames_from_data_ext_json(data_filename)
    # elif ext == '.json':
    #     return frames_from_data_ext_json_2(data_filename)

    elif ext == '.json':
        return frames_from_data_ext_json_3(data_filename)
    elif ext == '.atlas':
        return frames_from_data_ext_atlas(data_filename)
    else:
        print("Wrong data format on parsing: '" + ext + "'!")
        exit(1)



def frames_from_data_ext_plist(data_filename):
    root = ElementTree.fromstring(open(data_filename, 'r').read())


    plist_dict = tree_to_dict(root[0])
    to_list = lambda x: x.replace('{', '').replace('}', '').split(',')
    frames = plist_dict['frames'].items()
    for k, v in frames:
        frame = v
    if plist_dict["metadata"]["format"] == 3:
        frame['frame'] = frame['textureRect']
    frame['rotated'] = frame['textureRotated']
    frame['sourceSize'] = frame['spriteSourceSize']
    frame['offset'] = frame['spriteOffset']

    rectlist = to_list(frame['frame'])
    width = int(float(rectlist[3] if frame['rotated'] else rectlist[2]))
    height = int(float(rectlist[2] if frame['rotated'] else rectlist[3]))
    frame['box'] = (
        int(float(rectlist[0])),
        int(float(rectlist[1])),
        int(float(rectlist[0])) + width,
        int(float(rectlist[1])) + height
    )
    real_rectlist = to_list(frame['sourceSize'])
    real_width = int(float(real_rectlist[1] if frame['rotated'] else real_rectlist[0]))
    real_height = int(float(real_rectlist[0] if frame['rotated'] else real_rectlist[1]))
    real_sizelist = [real_width, real_height]
    frame['real_sizelist'] = real_sizelist
    offsetlist = to_list(frame['offset'])
    offset_x = int(float(offsetlist[1] if frame['rotated'] else offsetlist[0]))
    offset_y = int(float(offsetlist[0] if frame['rotated'] else offsetlist[1]))

    if frame['rotated']:
        frame['result_box'] = (
            int(float((real_sizelist[0] - width) / 2 + offset_x)),
            int(float((real_sizelist[1] - height) / 2 + offset_y)),
            int(float((real_sizelist[0] + width) / 2 + offset_x)),
            int(float((real_sizelist[1] + height) / 2 + offset_y))
        )
    else:
        frame['result_box'] = (
            int(float((real_sizelist[0] - width) / 2 + offset_x)),
            int(float((real_sizelist[1] - height) / 2 - offset_y)),
            int(float((real_sizelist[0] + width) / 2 + offset_x)),
            int(float((real_sizelist[1] + height) / 2 - offset_y))
        )
    return frames


def frames_from_data_ext_json(data_filename):
    json_data = open(data_filename)
    data = json.load(json_data)
    frames = {}
    for f in data['frames']:
        x = int(float(f["frame"]["x"]))
        y = int(float(f["frame"]["y"]))
        w = int(float(f["frame"]["h"] if f['rotated'] else f["frame"]["w"]))
        h = int(float(f["frame"]["w"] if f['rotated'] else f["frame"]["h"]))
        real_w = int(float(f["sourceSize"]["h"] if f['rotated'] else f["sourceSize"]["w"]))
        real_h = int(float(f["sourceSize"]["w"] if f['rotated'] else f["sourceSize"]["h"]))
        d = {
            'box': (
                x,
                y,
                x + w,
                y + h
            ),
            'real_sizelist': [
                real_w,
                real_h
            ],
            'result_box': (
                int((real_w - w) / 2),
                int((real_h - h) / 2),
                int((real_w + w) / 2),
                int((real_h + h) / 2)
            ),
            'rotated': f['rotated']
        }
        frames[f["filename"]] = d
    json_data.close()
    return frames.items()


def frames_from_data_ext_atlas(data_filename):
    atlas = open(data_filename, 'r')

    frames = {}

    _ = atlas.readline()
    atlas_file_name = atlas.readline()
    atlas_size = atlas.readline()
    atlas_format = atlas.readline()
    atlas_filter = atlas.readline()
    atlas_repeat = atlas.readline()

    while True:
        texture_name = atlas.readline()
        if len(texture_name) == 0:
            break

        rotate = atlas.readline()
        xy = atlas.readline()
        size = atlas.readline()
        orig = atlas.readline()
        offset = atlas.readline()
        index = atlas.readline()

        print texture_name, rotate, xy, size, orig, offset, index

        texture_name = texture_name.strip()

        rotated = bool(rotate.split(':')[1])

        xy_ = xy.split(':')[1].split(',')
        x, y = int(float(xy_[0])), int(float(xy_[1]))

        size_ = size.split(':')[1].split(',')
        w = int(float(size_[0] if rotated else size_[1]))
        h = int(float(size_[1] if rotated else size_[0]))

        orig_ = orig.split(':')[1].split(',')
        real_w = int(float(orig_[0] if rotated else orig_[1]))
        real_h = int(float(orig_[1] if rotated else orig_[0]))

        offset_ = offset.split(':')[1].split(',')
        offset_x = int(float(offset_[0] if rotated else offset_[1]))
        offset_y = int(float(offset_[1] if rotated else offset_[0]))

        d = {
            'box': (
                x,
                y,
                x + w,
                y + h
            ),
            'real_sizelist': [
                real_w,
                real_h
            ],
            'result_box': (
                int((real_w - w) / 2 + offset_x),
                int((real_h - h) / 2 - offset_y),
                int((real_w + w) / 2 + offset_x),
                int((real_h + h) / 2 - offset_y)
            ),
            'rotated': rotated
        }
        frames[texture_name] = d

    atlas.close()

    return frames.items()


def frames_from_data_ext_json_2(data_filename):
    json_data = open(data_filename)
    data = json.load(json_data)
    frames = {}


    print "data: ", data['frames']

    for k, f in data['frames'].items():
        f = data['frames'][k]
        print "k,v: ", k, f

        x = int(float(f["x"]))

        y = int(float(f["y"]))
        w = int(float(f["h"]))
        h = int(float(f["w"]))

        d = {
            'box': (
                x,
                y,
                x + w,
                y + h
            ),
            'real_sizelist': [
                w,
                h
            ],
            'result_box': (
                0, 0, w, h
            ),
            'rotated': False
        }
        frames[k] = d
    json_data.close()
    return frames.items()


def frames_from_data_ext_json_3(data_filename):
    json_data = open(data_filename)
    data = json.load(json_data)
    frames = {}


    print "data: ", data['res']

    for k, f in data['res'].items():
        f = data['res'][k]
        print "k,v: ", k, f

        x = int(float(f["x"]))

        y = int(float(f["y"]))
        w = int(float(f["w"]))
        h = int(float(f["h"]))

        d = {
            'box': (
                x,
                y,
                x + w,
                y + h
            ),
            'real_sizelist': [
                w,
                h
            ],
            'result_box': (
                0, 0, w, h
            ),
            'rotated': False
        }
        frames[k] = d
    json_data.close()
    return frames.items()


def gen_png_from_data(filename, ext):
    big_image = Image.open(filename + ".png")
    frames = frames_from_data(filename, ext)

    for k, v in frames:
        frame = v
        box = frame['box']
        rect_on_big = big_image.crop(box)
        real_sizelist = frame['real_sizelist']
        result_image = Image.new('RGBA', real_sizelist, (0, 0, 0, 0))
        result_box = frame['result_box']
        result_image.paste(rect_on_big, result_box, mask=0)
        if frame['rotated']:
            result_image = result_image.transpose(Image.ROTATE_90)
        if not os.path.isdir(filename):
            os.mkdir(filename)
        outfile = (filename + '/' + k).replace('gift_', '')
        if not outfile.endswith('.png'):
            outfile += '.png'
        print(outfile, "generated")
        result_image.save(outfile)


def endWith(s, *endstring):
    array = map(s.endswith, endstring)
    if True in array:
        return True
    else:
        return False


# Get the all files & directories in the specified directory (path).   
def get_file_list(path):
    current_files = os.listdir(path)
    all_files = []
    for file_name in current_files:
        full_file_name = os.path.join(path, file_name)
        if endWith(full_file_name, '.plist'):
            full_file_name = full_file_name.replace('.plist', '')
            all_files.append(full_file_name)
        if endWith(full_file_name, '.json'):
            full_file_name = full_file_name.replace('.json', '')
            all_files.append(full_file_name)
        if endWith(full_file_name, '.atlas'):
            full_file_name = full_file_name.replace('.atlas', '')
            all_files.append(full_file_name)
        if os.path.isdir(full_file_name):
            next_level_files = get_recursive_file_list(full_file_name)
            all_files.extend(next_level_files)
    return all_files


def get_sources_file(filename):
    data_filename = filename + ext
    png_filename = filename + '.png'
    if os.path.exists(data_filename) and os.path.exists(png_filename):
        gen_png_from_data(filename, ext)
    else:
        print("Make sure you have both " + data_filename + " and " + png_filename + " files in the same directory")


# Use like this: python unpacker.py [Image Path or Image Name(but no suffix)] [Type:plist or json]
if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print("You must pass filename as the first parameter!")
        exit(1)
    # filename = sys.argv[1]
    path_or_name = sys.argv[1]
    ext = '.plist'
    if len(sys.argv) < 3:
        print("No data format passed, assuming .plist")
    elif sys.argv[2] == 'plist':
        print(".plist data format passed")
    elif sys.argv[2] == 'json':
        ext = '.json'
        print(".json data format passed")
    elif sys.argv[2] == 'atlas':
        ext = '.atlas'
        print('.atlas data format passed')
    else:
        print("Wrong data format passed '" + sys.argv[2] + "'!")
        exit(1)
    # supports multiple file conversions
    if os.path.isdir(path_or_name):
        files = get_file_list(path_or_name)
        print("files", files)
        for file0 in files:
            print "file0", file0
            get_sources_file(file0)
    else:
        get_sources_file(path_or_name)
