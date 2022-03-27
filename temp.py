import os
import uuid


def get_file_path(filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('instance.directory_string_var', filename)


if __name__ == '__main__':
    print(get_file_path('12345.text'))