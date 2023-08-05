#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2010, Mads Sulau Joergensen <mads@sulau.dk>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the author nor the names of his/her contributors
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY Mads Sulau Joergensen ""AS IS"" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Mads Sulau Joergensen BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Newest version is always found at: http://bitbucket.org/madssj/s3vcp/

__author__ = u"Mads Sülau Jørgensen <mads@sulau.dk>"
__version__ = "0.2.2"
__license__ = "BSD"

import os
import sys
import threading
import logging

try:
    from hashlib import md5
except ImportError:
    from md5 import md5

from Queue import Queue

try:
    import boto
except ImportError:
    sys.stderr.write("error: could not import boto - it can be installed via setuptools using\n")
    sys.stderr.write("       sudo easy_install boto\n")
    sys.exit(1)


def thread_queue(producer, consumer, num_workers, queue=None):
    """
    Makes a very simple producer/consumer thread queue.

    Exceptions are not handled, so if an exception occurs in a
    consumer or producer, they will quit.

    :param producer: producer, first argumen is the queue
    :type producer: callable

    :param consumer: consumer, first argument is the queue
    :type consumer: callable

    :param queue: if None is given, a new queue will be created
    :type queue: :class:`Queue.Queue`

    :param num_workers: amount of consumer threads produced
    :type num_workers: int
    """
    workers = []

    if not queue:
        queue = Queue()

    for i in range(num_workers):
        worker = threading.Thread(target=consumer, args=[queue])
        worker.start()

        workers.append(worker)

    producer(queue)

    for worker in workers:
        queue.put(None)

    for worker in workers:
        worker.join()


def s3_copy(s3_bucket, source, target, num_workers):
    """
    Copies keys from ``source`` to ``target`` with the porpuse
    of speeding up uploads.

    :param s3_bucket: S3 bucket for operations
    :type s3_bucket: string

    :param source: source prefix
    :type source: string

    :param target: target prefix - replaced with source prefix on
        every key.
    :type target: string

    :param num_workers: amount of consumer threads to use
    :type num_workers: int
    """
    def consumer(queue):
        conn = boto.connect_s3()
        bucket = conn.get_bucket(s3_bucket)

        item = queue.get()
        while item:
            old_key, new_key = item

            logging.info("copying %s to %s", old_key, new_key)

            key = bucket.copy_key(new_key, s3_bucket, old_key)
            key.make_public()

            item = queue.get()

    def producer(queue):
        conn = boto.connect_s3()
        bucket = conn.get_bucket(s3_bucket)

        for key in bucket.list(prefix=source):
            queue.put((key.name, key.name.replace(source, target, 1)))

    thread_queue(producer, consumer, num_workers)


def s3_upload(s3_bucket, lpath, rpath, num_workers, add_expires=False, headers={}):
    """
    Uploads all files in ``lpath`` and prepend the prefix of ``rpath``
    before uploading.

    Every key created by this method will be public.

    :param s3_bucket: The S3 bucket to upload in
    :type s3_bucket: string

    :param lpath: local path for :meth:`os.walk` call
    :type lpath: string

    :param rpath: remote prefix - prepended to every new key
    :type rpath: string

    :param num_workers: amount of consumer threads to use
    :type num_workers: int

    :param add_expires: adds far future expires headers for every key
    :type add_expires: bool
    """
    if add_expires:
        headers.update({"Cache-Control": "public, max-age=31536000",
                        "Expires": "Thu, 20 Apr 2020 20:00:00 GMT"})

    def producer(queue):
        for root, dirs, files in os.walk(lpath):
            for lfile in files:
                if os.path.basename(lfile).startswith(".") or ".svn" in root + lfile:
                    pass
                else:
                    file = os.path.join(root, lfile).replace(lpath + "/", "", 1)

                    rfile = "%s%s" % (rpath, file)

                    queue.put((os.path.join(root, lfile), rfile))

    def consumer(queue):
        conn = boto.connect_s3()
        bucket = conn.get_bucket(s3_bucket)

        item = queue.get()

        while item:
            source, target = item
            upload = True

            key = bucket.get_key(target)

            if key:
                source_md5 = md5()

                for chunk in open(source):
                    source_md5.update(chunk)

                upload = key.etag[1:-1] != source_md5.hexdigest()
            else:
                key = bucket.new_key(target)

            for meta_key, meta_value in headers.iteritems():
                key.set_metadata(meta_key, meta_value)

            if upload:
                key.set_contents_from_filename(source,
                                               replace=True,
                                               policy="public-read")

                logging.info("uploaded %s", target)
            else:
                key.make_public()

            item = queue.get()

    thread_queue(producer, consumer, num_workers)


def s3_download(s3_bucket, lpath, num_workers, remote_path=None, matcher=None):
    """
    Downloads all files in ``s3_bucket`` into ``lpath``.

    Every key created by this method will be public.

    :param s3_bucket: The S3 bucket to upload in
    :type s3_bucket: string

    :param lpath: local base path for download
    :type lpath: string

    :param num_workers: amount of consumer threads to use
    :type num_workers: int

    :param remote_path: argument passed to bucket.list
    :type remote_path: string

    :param matcher: if defined will be called for every item to detirmine if
                    item should be downloaded.
    :type matcher: function
    """
    def producer(queue):
        conn = boto.connect_s3()
        bucket = conn.get_bucket(s3_bucket)

        for item in bucket.list(remote_path):
            if matcher and matcher(item) is not None:
                continue

            queue.put(item.name)

    def consumer(queue):
        conn = boto.connect_s3()
        bucket = conn.get_bucket(s3_bucket)

        item = queue.get()

        while item:
            source = item
            key = bucket.get_key(source)

            if key:
                target_dir = os.path.join(lpath, os.path.dirname(source))

                if not os.path.isdir(target_dir):
                    os.makedirs(target_dir)

                key.get_contents_to_filename(os.path.join(lpath, source))

                logging.info("downloaded %s", source)

            item = queue.get()

    thread_queue(producer, consumer, num_workers)


def main():
    from optparse import OptionParser

    parser = OptionParser("usage: %prog [options] <mode upload|download> <bucket> <local-source> [local-source ...]", version="s3vcp %s" % __version__)
    parser.add_option("-p", "--remote-prefix", dest="prefix", default="",
                      help="prefix all the new keys with PREFIX", metavar="PREFIX")
    parser.add_option("-t", "--num-threads", dest="num_workers", type="int",
                      help="use NUM worker threads", default=8, metavar="NUM")
    parser.add_option("-c", "--copy-from", dest="copy", default="",
                      help="""copy the keys on S3 from the location PATH before
                      uploading, the files md5 sum will be used to detirmine
                      if there are any changes between the local and
                      remote files""", metavar="PATH")
    parser.add_option("-e", "--add-expires", dest="add_expires", default=False,
                      help="add far future expires headers to all the files uploaded",
                      action="store_true")
    (options, args) = parser.parse_args(sys.argv[1:])

    s3_prefix = options.prefix.rstrip("/")
    s3_copy_from = options.copy.rstrip("/")
    add_expires = options.add_expires
    num_workers = options.num_workers

    local_paths = []

    logging.basicConfig(level=logging.INFO)

    prog_mode = args[0]

    try:
        s3_bucket = args[1]

        for local_path in args[2:]:
            local_paths.append(local_path.rstrip("/"))
    except IndexError:
        parser.error("required arguments are missing")

    conn = None
    try:
        conn = boto.connect_s3()
        conn.get_bucket(s3_bucket)
    except Exception, e:
        if prog_mode == "upload" and hasattr(e, 'code') and e.code == "NoSuchBucket":
            answer = raw_input("bucket %s was not found - want to create it? [y/N]: " % s3_bucket)
            if answer.lower().strip() == "y":
                conn.create_bucket(s3_bucket)
                logging.info("bucket %s created" % s3_bucket)
            else:
                parser.exit("failed to find target bucket")
        else:
            parser.exit("failed to connect to S3 - %s" % e)

    if prog_mode == "upload":
        if s3_copy_from and not s3_copy_from.endswith("/"):
            s3_copy_from = s3_copy_from + "/"

        if s3_prefix and not s3_prefix.endswith("/"):
            s3_prefix = s3_prefix + "/"

        if s3_copy_from and s3_prefix:
            s3_copy(s3_bucket, s3_copy_from, s3_prefix, num_workers)

        for local_path in local_paths:
            s3_upload(s3_bucket, local_path, s3_prefix, num_workers, add_expires)
    elif prog_mode == "download":
        s3_download(s3_bucket, local_path, num_workers)


if __name__ == "__main__":
    main()
