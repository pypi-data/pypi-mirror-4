import os


def ensure_containing_directory_exists(path):
    dirname, basename = os.path.split(path)
    if dirname != '' and not os.path.exists(dirname):
        os.makedirs(dirname)


def touch(path):
    ensure_containing_directory_exists(path)
    with open(path, 'a'):
        pass


def write_file(path, content):
    ensure_containing_directory_exists(path)
    encoded_content = content
    if isinstance(content, unicode):
        encoded_content = content.encode('utf-8')
    with open(path, "w") as f:
        f.write(encoded_content)


class Writer(object):

    def write(self, package_files, path):
        for package_file in package_files:
            target_path = os.path.join(path, package_file.path)
            if not package_file.overwrite and os.path.exists(target_path):
                continue
            write_file(target_path, package_file.get_contents())
