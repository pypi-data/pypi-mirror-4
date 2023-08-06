import re
from xml.etree import ElementTree
from geom import Rect
from pkg_resources import resource_stream


def parse(filename):
    f = resource_stream('wildwest', filename)
    tree = ElementTree.parse(f)
    return tree


def images(tree):
    images = []
    doch = float(tree.getroot().get('height'))
    for node in tree.findall('.//{http://www.w3.org/2000/svg}image'):
        file = node.get('{http://www.w3.org/1999/xlink}href')
        if not file:
            continue
        mo = re.search(r'/([^/]+).png$', file)
        if mo:
            name = mo.group(1)
            r = get_rect(node, doch)
            images.append((name, r))
    return images


def round_to_int(v):
    return int(float(v) + 0.5)


def get_rect(node, doch):
    x = round_to_int(node.get('x'))
    width = round_to_int(node.get('width'))

    # Load and transform y
    y = float(node.get('y'))
    height = float(node.get('height'))
    y = round_to_int(doch - height - y)
    height = round_to_int(height)

    return Rect.from_blwh((x, y), width, height)


def rectangles(tree):
    rect = []
    doch = float(tree.getroot().get('height'))
    for node in tree.findall('.//{http://www.w3.org/2000/svg}rect'):
        r = get_rect(node, doch)
#        print node.get('id'), r
        rect.append(r)
    return rect


def load_geometry(obj_type):
    source = 'assets/geometry/%s.svg' % obj_type
    tree = parse(source)
    return rectangles(tree)


def load_level_data(name):
    source = 'assets/levels/%s.svg' % name
    tree = parse(source)
    return images(tree)


if __name__ == '__main__':
    print load_geometry('mailcar')
