import os
import sys
import time
import urlparse
import urllib
import optparse
import logging
import multiprocessing
import mimetypes

from distlib.locators import SimpleScrapingLocator, DistlibException
import lockfile
from bottle import get, abort, run, static_file, HTTPResponse
from proxypypi.daemon import Daemon

locator = None
pkgdir = None

log = logging.getLogger(__name__)

# HTML templates
HEADER = """<html><head><title>Links for %(package)s</title></head>
    <body><h1>Links for %(package)s</h1>"""
ITEM = '<a href="%(prefix)s/%(package)s">%(package)s</a><br/>'
FOOTER = "</body></html>"


@get('/simple/')
def simple_index():
    return search("../../package")


@get('/simple/<package>/')
def simple_package(package):
    return search("../../package", package)


@get('/package/')
def package_index():
    return search(".")


@get('/package/<package>/<filename>')
def package_package_file(package, filename):
    return package_file(os.path.join(package, filename))


@get('/package/<filename>')
def package_file(filename):
    if filename[0] in './':
        abort(403, 'Forbidden')

    log.info('request for %s', filename)

    # if there's a ".url" file then we need to fetch the file; otherwise the
    # file is already on disk and whole
    if not os.path.exists(filename + '.url'):
        return static_file(filename, './')

    # There will be something already fetching the file if there's also a
    # ".size" file; there's a race condition here but it's handled by the
    # download process
    if not os.path.exists(filename + '.size'):
        log.info('%s needs to be downloaded', filename)
        with open(filename + '.url') as f:
            url = f.read()
        p = multiprocessing.Process(target=download, args=(url, filename))
        p.start()

    # We may enter this code before the download process has had a chance to
    # set up the size file correctly; check it exists and also has valid
    # contents before continuing. There's also the chance the download happens
    # so fast that the download completes before we read the ".size" file and
    # the ".url" file is removed.
    log.info('waiting for %s download to start', filename)
    size = None
    while not size:
        if os.path.exists(filename + '.size'):
            with open(filename + '.size') as f:
                size = f.read()
            if size:
                size = int(size)
            else:
                time.sleep(.1)
        elif not os.path.exists(filename + '.url'):
            # beaten; file's already downloaded
            log.info('%s appears to be fully downloaded now', filename)
            return static_file(filename, './')
        else:
            time.sleep(.1)

    log.info('following download of %s', filename)
    return partial_static_file(filename, './', size)


def download(url, filename):
    '''Download the file indicated from the url given.

    Store the expected size of the file alongside the partial file so watchers
    know when we're done.

    The downloading process will lock the size file to prevent other
    (race-conditioned) download processes running in parallel.
    '''
    lock = lockfile.FileLock(filename + '.size')
    # TODO if the process dies between here and the try/finally then the lock
    # file could be left on disk...
    try:
        lock.acquire(timeout=0)
        # lock the size file
    except lockfile.AlreadyLocked:
        # we've race-conditioned here and we should
        # defer to the process that actually locked the file
        log.info('process %s for %s beaten to it', os.getpid(), url)
        return

    log.info('downloading %s in process %s...', url, os.getpid())
    try:
        # open straight away so the file's on disk
        local_path = os.path.join(pkgdir, filename)
        with open(local_path, 'wb') as content_file:
            content = urllib.urlopen(url)

            # get file size and store it away
            size = int(content.info()['Content-Length'])
            with open(filename + '.size', 'w') as size_file:
                size_file.write(str(size))

            # grab data
            total = 0
            while 1:
                try:
                    # read in chunks so we can write out as we go
                    chunk = content.read(10000)
                except Exception:
                    log.exception('reading from %s' % url)
                    break
                if not chunk:
                    break
                total += len(chunk)
                content_file.write(chunk)
            if total != size:
                log.error('%s fetched %dB != Content-Length %dB', filename,
                    total, size)
                # remove partial and size file
                os.remove(filename)
                os.remove(filename + '.size')
                # TODO cancel current downloads of partial!
                return

        log.info('... fetched into %s', filename)
        os.remove(filename + '.url')
        os.remove(filename + '.size')
    finally:
        lock.release()


def partial_static_file(filename, root, actual_size):
    '''Serve a static file to the client where the file contents (expecting
    actual_size bytes in size) are not all present yet. Extends and modifies
    the standard bottle static_file function.
    '''
    root = os.path.abspath(root) + os.sep
    filename = os.path.abspath(os.path.join(root, filename.strip('/\\')))
    headers = dict()

    log.info('serving %s which is being download', filename)

    if not filename.startswith(root):
        return abort(403, "Access denied.")
    if not os.path.exists(filename) or not os.path.isfile(filename):
        return abort(404, "File does not exist.")
    if not os.access(filename, os.R_OK):
        return abort(403, "You do not have permission to access this file.")

    mimetype, encoding = mimetypes.guess_type(filename)
    if mimetype:
        headers['Content-Type'] = mimetype

    # the file on disk lies about its size
    headers['Content-Length'] = actual_size

    # work through partial data as it appears until the whole thing has been
    # read
    def reader(filename, actual_size):
        log.info('going to read %dB from %s', actual_size, filename)
        with open(filename, 'rb') as f:
            total = 0
            position = 0
            while 1:
                # we need to manually tell/read/seek because Python's read()
                # will just stop otherwise
                f.seek(position)
                content = f.read()
                position = f.tell()
                if not content:
                    # nothing was read
                    time.sleep(.5)
                    continue
                total += len(content)
                # log.info('got another %dB to write (%dB total, %dB left)',
                #     len(content), total, actual_size - total)
                yield content
                if total == actual_size:
                    log.info('all read')
                    break

    return HTTPResponse(reader(filename, actual_size), **headers)


def find_files(directory):
    for root, dirs, files in os.walk(directory, followlinks=True):
        for file in files:
            if file[0] == '.':
                continue
            if file.endswith('.url'):
                # this is a file-that-could-be
                yield (file[:-4], os.path.relpath(os.path.join(root,
                    file[:-4]), directory))
            elif file.endswith('.size'):
                continue
            else:
                yield (file, os.path.relpath(os.path.join(root, file),
                    directory))


def search(prefix, name=''):
    assert pkgdir is not None, 'configure_pkgdir() not called!'
    if name:
        # TODO use distlib to find the appropriate files?
        packages = [path for f, path in find_files(pkgdir)
            if f.startswith(name)]
        if not packages:
            packages = locate(name)
    else:
        name = 'All Packages'
        packages = [path for f, path in find_files(pkgdir)]

    if packages:
        l = []
        l.append(HEADER % {'package': name})
        for pkg in packages:
            l.append(ITEM % {'prefix': prefix, 'package': pkg})
        l.append(FOOTER)
        return '\n'.join(l)
    else:
        if name:
            abort(404, "Not Found (%s does not have any releases)" % name)
        else:
            abort(404, "Not Found")


def locate(pkgname):
    if locator is None:
        log.debug('no locator, not proxying')
        return []

    log.info('locating %s', pkgname)
    try:
        releases = locator.get_project(pkgname)
    except DistlibException:
        return []

    filenames = []
    for version in releases:
        p = releases[version]
        log.info('Found %s', p)
        url = urlparse.urlparse(p.download_url)
        filename = os.path.basename(url.path)
        filename = os.path.join(p.name, filename)
        if not os.path.exists(p.name):
            os.mkdir(p.name)
        filenames.append(filename)
        with open(filename + '.url', 'w') as f:
            f.write(p.download_url)

    return filenames


def configure_locator(url):
    global locator
    locator = SimpleScrapingLocator(url)


def configure_pkgdir(directory):
    global pkgdir
    pkgdir = directory
    os.chdir(directory)


class Server(Daemon):
    handle_signals = False

    def __init__(self, opt):
        super(Server, self).__init__(pid_file=opt.pidfile,
            console_out_file=opt.console)
        self.opt = opt

    def start(self):
        logging.basicConfig(filename=self.opt.logfile, level=logging.INFO)

        if self.opt.should_proxy:
            configure_locator(self.opt.url)
            log.info("proxying to %s" % self.opt.url)
        else:
            log.info("NOT proxying to fetch missing packages")

        log.info("caching packages in %s" % self.opt.cache)
        configure_pkgdir(self.opt.cache)

    def process(self):
        # note: I specify a *large* gunicorn timeout here as I saw timeouts
        # on even modest (<10MB) file download attempts by clients :-(
        run(host=self.opt.bind, port=self.opt.port, debug=True,
            server='gunicorn', workers=4, timeout=60 * 60)

COMMAND_HELP = """
Commands:
    "run"           run in the foreground
    "start"         start the daemon - run self.main()
    "stop"          stop the active process
    "restart"       stop & start the active process
    "forcerestart"  forcibly stop & start the active process
    "condstart"     start the daemon if it's not running
    "maybestop"     stop the active process only if it's running
    "status"        display the status of the active process

When specifying anything other than "run" you must supply the pidfile, logfile
and console out file arguments.
"""


class HelpOptionParser(optparse.OptionParser):
    def format_help(self, formatter=None):
        # old school super()
        help = optparse.OptionParser.format_help(self, formatter)
        return help + COMMAND_HELP


def main():
    from proxypypi import __version__
    parser = HelpOptionParser(usage="usage: %prog [options] command",
        version="%prog " + __version__)

    parser.add_option("-d", "--cache", dest="cache", default=".",
        type="str", help="directory to cache packages in (default: %default)")
    parser.add_option("-b", "--bind", dest="bind", default="0.0.0.0",
        type="str", help="address to bind to (default: %default)")
    parser.add_option("-p", "--port", dest="port", default=8000, type="int",
        help="port to listen on  (default: %default)")
    parser.add_option("-P", "--pid", dest="pidfile", default='', type="str",
        help="file to store the PID in (default: %default)")
    parser.add_option("-l", "--log", dest="logfile", default='', type="str",
        help="file to log messages to (default: %default)")
    parser.add_option("-o", "--out", dest="console", default='', type="str",
        help="file to send console messages to (default: %default)")
    parser.add_option("-i", "--index-url", dest="url", type="str",
        default="https://pypi.python.org/simple/",
        help="base URL of Python Package Simple Index (default: %default)")
    parser.add_option("-n", "--no-proxy", dest="should_proxy", default=True,
        action="store_false",
        help="turn off proxying to fetch missing packages")

    opt, arg = parser.parse_args()
    if len(arg) != 1:
        parser.error("incorrect number of arguments")

    # absolute-ify all these
    if opt.pidfile and not os.path.isabs(opt.pidfile):
        opt.pidfile = os.path.abspath(opt.pidfile)
    if opt.logfile and not os.path.isabs(opt.logfile):
        opt.logfile = os.path.abspath(opt.logfile)
    if opt.console and not os.path.isabs(opt.console):
        opt.console = os.path.abspath(opt.console)
    if opt.cache and not os.path.isabs(opt.cache):
        opt.cache = os.path.abspath(opt.cache)

    if not os.path.exists(opt.cache):
        parser.error("invalid cache directory")

    dopts = [opt.logfile, opt.console]
    if opt.pidfile and not all(dopts):
        parser.error('you must specity log file and console out file with PID'
            ' file')

    # gunicorn wishes to ownz0r all the arguments unless I make them disappear
    sys.argv[:] = sys.argv[:1]

    Server(opt).control(arg[0])

if __name__ == '__main__':
    main()

#
# Copyright (c) 2013, ekit.com Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
