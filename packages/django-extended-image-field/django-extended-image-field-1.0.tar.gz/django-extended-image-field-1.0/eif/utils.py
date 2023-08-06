import os
import string
import random


def gen_filename(name, storage=os.path):
    alphabet = '%s_%s' % (string.ascii_letters, string.digits)
    filename = u''
    ext = os.path.splitext(name)[-1].upper()

    for _ in xrange(10):
        filename += random.choice(alphabet)
    filename += ext.lower()

    if storage.exists(filename):
        filename = gen_filename(name, storage)
    return filename


def get_max_image_sizes(images, attr='image'):
    width = max([getattr(img, attr).width for img in images])
    height = min([getattr(img, attr).height for img in images if getattr(img, attr).width == width])
    return {'height': height, 'width': width}
