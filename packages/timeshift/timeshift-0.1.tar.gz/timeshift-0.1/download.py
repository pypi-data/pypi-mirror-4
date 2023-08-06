"""Download for a specified amount of time."""

# Copyright (c) 2013, Neil Martinsen-Burrell <neilmartinsenburrell@gmail.com>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import sys, time, urllib

class TimeLimitElapsed(RuntimeError):
    pass

def download_time_limit(url, filename=None, time_limit=0):
    def callback(count, blocksize, filesize):
        pass

    starttime = time.time()
    if time_limit > 0:
        def callback(count, blocksize, filesize):
            elapsed = time.time() - starttime
            if elapsed > time_limit:
                raise TimeLimitElapsed

    try:
        f = open(filename, 'w')
    except IOError:
        raise IOError('Cannot write to {0}'.format(filename))
    else:
        f.close()

    try:
        urllib.urlretrieve(url, filename=filename, reporthook=callback)
    except TimeLimitElapsed:
        pass

def main(argv=None):
    if argv is None:
        argv = sys.argv

    url = argv[1]
    outfilename = argv[2]

    if len(argv) > 3:
        time_limit = int(argv[3])
    else:
        time_limit = 0

    download_time_limit(url, outfilename, time_limit)
    

if __name__ == '__main__':
    sys.exit(main())
