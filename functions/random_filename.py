import uuid
from os import path


def random_filename(filename):
    ext = path.splitext(filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename
