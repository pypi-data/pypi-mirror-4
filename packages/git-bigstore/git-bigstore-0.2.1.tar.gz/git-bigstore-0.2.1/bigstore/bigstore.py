#!/usr/bin/env python

import time
import os
import fnmatch
from datetime import datetime

from .backends import S3Backend

import git
import boto
import errno
import hashlib
import os
import re
import shutil
import sys
import tempfile

attribute_regex = re.compile(r'(^[^\s]*)')
g = git.Git('.')
git_directory = g.rev_parse(git_dir=True)

try:
    default_hash_function_name = g.config("bigstore.hasher")
except git.exc.GitCommandError:
    default_hash_function_name = 'sha256'

hash_functions = {
    'md5': hashlib.md5,
    'sha1': hashlib.sha1,
    'sha224': hashlib.sha224,
    'sha256': hashlib.sha256,
    'sha384': hashlib.sha384,
    'sha512': hashlib.sha512
}

default_hash_function = hash_functions[default_hash_function_name]

def default_backend():
    try:
        backend_name = g.config("bigstore.backend", file=".bigstore")
    except git.exc.GitCommandError:
        backend_name = None

    if backend_name == "s3":
        access_key_id = g.config("bigstore.s3.key", file=".bigstore")
        secret_access_key = g.config("bigstore.s3.secret", file=".bigstore")
        bucket_name = g.config("bigstore.s3.bucket", file=".bigstore")
        return S3Backend(access_key_id, secret_access_key, bucket_name)
    else:
        sys.stderr.write("error: s3 is currently the only supported backend")
        sys.exit(0)

def object_directory(hash_function_name):
    return os.path.join(git_directory, "bigstore", "objects", hash_function_name)

def object_filename(hash_function_name, hash):
    return os.path.join(object_directory(hash_function_name), hash[:2], hash[2:])

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def upload_callback(filename):
    def inner(size, total):
        sys.stderr.write("\r")
        sys.stderr.write("{: <4.0%}\t{}".format(size / float(total), filename))

    return inner

def pathnames():
    """ Generator that will yield pathnames for files tracked under gitattributes """
    filters = []
    try:
        with open(".gitattributes") as file:
            for line in file:
                match = attribute_regex.match(line)
                groups = match.groups()
                if len(groups) > 0:
                    filters.append(groups[0])
    except IOError:
        pass
    else:
        results = g.ls_tree("HEAD", r=True).split('\n')
        filenames = {}
        for result in results:
            metadata, filename = result.split('\t')
            _, _, sha = metadata.split(' ')
            filenames[filename] = sha

        for filter in filters:
            for filename, sha in filenames.iteritems():
                if fnmatch.fnmatch(filename, filter):
                    yield sha, filename

def push():
    try:
        sys.stderr.write("pulling bigstore metadata...")
        g.fetch("origin", "refs/notes/bigstore:refs/notes/bigstore-remote", "--force")
    except git.exc.GitCommandError:
        g.notes("--ref=bigstore", "add", "HEAD", "-m", "bigstore")
        sys.stderr.write("done\n")
    else:
        g.notes("--ref=bigstore", "merge", "-s", "cat_sort_uniq", "refs/notes/bigstore-remote")
        sys.stderr.write("done\n")

    for sha, filename in pathnames():
        try:
            entries = g.notes("--ref=bigstore", "show", sha).split('\n')
        except git.exc.GitCommandError:
            # No notes exist for this object
            entries = []

        for entry in entries:
            if "upload" in entry:
                break
        else:
            firstline, hash_function_name, hash = g.show(sha).split('\n')
            if firstline == 'bigstore':
                backend = default_backend()
                if not backend.exists(hash):
                    with open(object_filename(hash_function_name, hash)) as file:
                        backend.push(file, hash, cb=upload_callback(filename))

                    sys.stderr.write("\n")

                    user_name = g.config("user.name")
                    user_email = g.config("user.email")
                    g.notes("--ref=bigstore", "append", sha, "-m", "{}	upload	s3	{} <{}>".format(time.time(), user_name, user_email))

    sys.stderr.write("pushing bigstore metadata...")
    g.push("origin", "refs/notes/bigstore")
    sys.stderr.write("done\n")

def pull():
    try:
        sys.stderr.write("pulling bigstore metadata...")
        g.fetch("origin", "refs/notes/bigstore:refs/notes/bigstore-remote", "--force")
    except git.exc.GitCommandError:
        g.notes("--ref=bigstore", "add", "HEAD", "-m", "bigstore")
        sys.stderr.write("done\n")
    else:
        g.notes("--ref=bigstore", "merge", "-s", "cat_sort_uniq", "refs/notes/bigstore-remote")
        sys.stderr.write("done\n")

    for sha, filename in pathnames():
        try:
            entries = g.notes("--ref=bigstore", "show", sha).split('\n')
        except git.exc.GitCommandError:
            entries = []

        for entry in entries:
            if "upload" in entry.split('\t'):
                firstline, hash_function_name, hash = g.show(sha).split('\n')
                if firstline == 'bigstore':
                    try:
                        with open(object_filename(hash_function_name, hash)):
                            pass
                    except IOError:
                        backend = default_backend()
                        if backend.exists(hash):
                            with open(filename, 'wb') as file:
                                backend.pull(file, hash, cb=upload_callback(filename))

                            sys.stderr.write("\n")

                            user_name = g.config("user.name")
                            user_email = g.config("user.email")
                            g.notes("--ref=bigstore", "append", sha, "-m", "{}	download	s3	{} <{}>".format(time.time(), user_name, user_email))
                            g.add(filename)

                break

    sys.stderr.write("pushing bigstore metadata...")
    g.push("origin", "refs/notes/bigstore")
    sys.stderr.write("done\n")

def filter_clean():
    file = tempfile.NamedTemporaryFile(mode='w+t', delete=False)
    hash = default_hash_function()

    for line in sys.stdin:
        if line == "bigstore\n":
            sys.stdout.write(line)
            sys.stdout.write(sys.stdin.next())
            sys.stdout.write(sys.stdin.next())
            break

        hash.update(line)
        file.write(line)
    else:
        file.close()

        hexdigest = hash.hexdigest()
        mkdir_p(os.path.join(object_directory(default_hash_function_name), hexdigest[:2]))
        shutil.copy(file.name, object_filename(default_hash_function_name, hexdigest))

        sys.stdout.write("bigstore\n")
        sys.stdout.write("{}\n".format(default_hash_function_name))
        sys.stdout.write("{}\n".format(hexdigest))


def filter_smudge():
    for line in sys.stdin:
        if line == "bigstore\n":
            hash_function_name = sys.stdin.next()
            hash = sys.stdin.next()
            source_filename = object_filename(hash_function_name[:-1], hash[:-1])

            try:
                with open(source_filename):
                    pass
            except IOError:
                sys.stdout.write(line)
                sys.stdout.write(hash_function_name)
                sys.stdout.write(hash)
            else:
                with open(source_filename, 'rb') as file:
                    for line in file:
                        sys.stdout.write(line)

                break

def request_s3_credentials():
    print "Please enter your S3 Credentials"
    print ""
    s3_key = raw_input("Access Key: ")
    s3_secret = raw_input("Secret Key: ")
    s3_bucket = raw_input("Bucket Name: ")

    g.config("bigstore.backend", "s3", file=".bigstore")
    g.config("bigstore.s3.key", s3_key, file=".bigstore")
    g.config("bigstore.s3.secret", s3_secret, file=".bigstore")
    g.config("bigstore.s3.bucket", s3_bucket, file=".bigstore")

def log():
    filename = sys.argv[2]
    trees = g.log("--pretty=format:%T", filename).split('\n')
    for tree in trees:
        entry = g.ls_tree('-r', tree, filename)
        metadata, filename = entry.split('\t')
        _, _, digest = metadata.split(' ')
        notes = g.notes("--ref=bigstore", "show", digest).split('\n')
        notes.reverse()
        for note in notes:
            if note == '':
                continue

            timestamp, action, backend, user = note.split('\t')
            dt = datetime.fromtimestamp(float(timestamp))
            if action == "upload":
                print "{}: uploaded to {} by {}".format(dt, backend, user)
            else:
                print "{}: downloaded from {} by {}".format(dt, backend, user)

def init():
    try:
        with open(".bigstore"):
            pass
    except IOError:
        request_s3_credentials()
    else:
        try:
            g.config("bigstore.s3.key", file=".bigstore")
            g.config("bigstore.s3.secret", file=".bigstore")
            g.config("bigstore.s3.bucket", file=".bigstore")
        except git.exc.GitCommandError:
            request_s3_credentials()
        else:
            print "Reading credentials from .bigstore configuration file."

    try:
        g.fetch("origin", "refs/notes/bigstore:refs/notes/bigstore-remote", "--force")
    except git.exc.GitCommandError:
        pass
    else:
        g.notes("--ref=bigstore", "merge", "-s", "cat_sort_uniq", "refs/notes/bigstore-remote")

    g.config("filter.bigstore.clean", "git-bigstore filter-clean")
    g.config("filter.bigstore.smudge", "git-bigstore filter-smudge")

    git_directory = g.rev_parse(git_dir=True)
    mkdir_p(object_directory(default_hash_function_name))

