"""Utilities to support tests"""


from collections import deque
import datetime
import hashlib
import os
import random
import shutil
import string
import tempfile
import time
import uuid


RANDOM_DATA = 'Thisdatamaybefarfromrandom,butithasnoduplicatebigrAms.'


def walk_tree(root_dir, include_dirs=False):
    for root, dirs, files in os.walk(root_dir):
        if include_dirs:
            for dir_name in dirs:
                yield os.path.join(root, dir_name)
        for name in files:
            yield os.path.join(root, name)


def make_temp_dir(description='test_temp'):
    """Return the path to a temporary directory"""
    abs_path = tempfile.mkdtemp(suffix=description)
    print 'Made temporary directory: {0}'.format(abs_path)
    return abs_path


def remove_dir(root):
    """Remove a directory"""
    if root is None:
        return
    try:
        shutil.rmtree(root)
    except Exception as err:
        print "Failed to remove dir: {0}, will retry once ({1})".format(root, err)
        time.sleep(1)
        shutil.rmtree(root)
    print 'Removed temporary directory: {0}'.format(root)


def write_file(src, seed, size=1000, initial=None):
    """Write a file that is reproduce-able given size, seed, and initial data

    :param src: Path to file that will be created / truncated and re-written
    :param seed: integer up to len of RANDOM_DATA - 1
    :param size: file size in bytes
    :param initial: string to write to the file first

    Returns a tuple of (checksum, mtime)
    """
    written = 0
    check = hashlib.md5()
    data_chunk_size = len(RANDOM_DATA)
    if seed >= data_chunk_size:
        print 'Warning: data uniqueness not guaranteed'
    data = deque(RANDOM_DATA)
    data.rotate(seed)
    data = ''.join(data)
    dirs = os.path.dirname(src)
    if not os.path.exists(dirs):
        try:
            os.makedirs(dirs)
        except Exception:
            pass  # might be a threading race if making lots in threads
    with open(src, 'wb') as fh:
        if initial:
            fh.write(initial[:size])
            written += len(initial)
            check.update(initial[:size])
        while written < size:
            if written + data_chunk_size <= size:
                chunk = str(data)
            else:
                chunk = str(data[:size - written])
            fh.write(chunk)
            check.update(chunk)
            written += len(chunk)
    return check.hexdigest(), os.path.getmtime(src)


def get_random_file_name(root='', prefix=None, name_len=10, extensions=None):
    """Return a random file name. If extensions is supplied, one will be chosen
    from the list. Will try to only return new names. If a root is suppled, a
    full path to the file will be formed.
    """
    while True:
        name = []
        if prefix:
            name.append(prefix)
            name_len -= len(prefix)
        for _ in xrange(name_len):
            name.append(random.choice(string.ascii_letters))
        if extensions:
            name.extend(random.choice(extensions))
        name = ''.join(name)
        full_path = os.path.join(root, name)
        if not os.path.exists(full_path):
            return full_path


def get_random_dir_path(root, max_depth=4, existing_dirs=None,
    new_dir_chance=.3, new_path_only=False):
    if existing_dirs is None:
        existing_dirs = set()
    while True:
        dir_count = random.randint(0, max_depth)
        dirs = [root]
        for i in range(dir_count):
            if existing_dirs and random.random() <= new_dir_chance:
                dirs.append(random.choice(list(existing_dirs)))
            else:
                dirs.append(get_random_file_name())
            existing_dirs.add(dirs[-1])
        dirs = os.path.join(*dirs)
        if not new_path_only or not os.path.exists(dirs):
            return dirs


def make_file_tree(root, file_count=10, extensions=None, file_size=1000):
    """Create a tree of files with various extensions off of root,
    returns a list if lists such as [[item, hash, mtime], [item, hash, mtime]]
    """
    if not extensions:
        extensions = ['.mov', '.mp3', '.png', '.jpg']
    file_list = []
    # this set is grown by the get_random_dir_path function
    existing_dirs = set()
    for i in xrange(file_count):
        fn = get_random_file_name(root=get_random_dir_path(root,
            existing_dirs=existing_dirs), extensions=extensions)
        src = os.path.join(root, fn)
        check, mtime = write_file(src, 0, size=file_size, initial=str(i))
        file_list.append([src, check, mtime])
    return file_list


def get_hash(src):
    check = hashlib.md5()
    with open(src, 'rb') as fh:
        d = fh.read(64000)
        while d:
            check.update(d)
            d = fh.read(64000)
    return check.hexdigest()


def apply_path_rules(osrc, nsrc, oroot, nroot, rules):
    new_path = [nroot]
    for rule in rules:
        if rule == 'mtime':
            time_stamp = datetime.datetime.fromtimestamp(
                os.path.getmtime(osrc))
            yyyy_mm = '{0}_{1:0>2}'.format(time_stamp.year, time_stamp.month)
            new_path.append(yyyy_mm)
        if rule == 'extension':
            new_path.append(os.path.splitext(osrc)[-1][1:])
    nsrc = nsrc.replace(nroot, '', 1)
    if nsrc.startswith(os.sep):
        nsrc = nsrc[1:]
    if rules and not 'no_change' in rules:
        new_path.append(os.path.basename(osrc))
    else:
        new_path.append(nsrc)
    return os.sep.join(new_path)


def verify_files(file_list):
    """Inspect a list of the form [[item, hash, mtime], [item, hash, mtime]]
    and return a tuple of (True|False, Message). True in the tuple indicates
    a match, if False, the message will contain the mismatches.
    """
    print 'Verifying {0} items'.format(len(file_list))
    success = True
    message = []
    for src, check, mtime in file_list:
        print ' ... {0}'.format(src)
        try:
            new_check = get_hash(src)
            new_mtime = os.path.getmtime(src)
            if not check == new_check:
                success = False
                message.append("Hash mismatch on {src}. Actual: {act} "
                    "Expected: {exp}".format(act=check, exp=new_check,
                        src=src))
            if not int(mtime) == int(new_mtime):
                success = False
                message.append("Mtime mismatch on {src}. Actual: {act} "
                    "Expected: {exp}".format(act=mtime, exp=new_mtime,
                        src=src))
        except Exception as err:
            msg = 'Failed to read {0}: {1}'.format(src, err)
            message.append(msg)
            print msg
            success = False
    return success, '\n'.join(message)


def gen_fake_manifest():
    """Imitate the type of data in a manifest"""
    manifest = {}
    file_a = '/a/b/c/{}.file'.format(random.getrandbits(16))
    file_b = '/c/b/{}.file'.format(random.getrandbits(16))
    sources = {file_a: None, file_b: None}
    manifest[str(uuid.uuid1())] = [
        [file_a,
            0L + random.randint(0, 10000), 1.0 * random.randint(0, 10000)]]
    manifest[str(uuid.uuid1())] = [
        [file_b, 0L + random.randint(0, 10000),
            1.0 * random.randint(0, 10000)]]
    return manifest, sources
