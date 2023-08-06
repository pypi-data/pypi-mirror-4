"""Record Internet radio and make it available as a podcast."""

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

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

import argparse, ConfigParser, os, sys, time, urlparse, uuid
from urlparse import urljoin

import download, feeds

DEBUG = False

def _mutter(message):
    if DEBUG:
        print message

def add_to_feed(url, feedpath, title=''):
    """Add the specified url to the Atom feed

    Arguments
    ---------
    url: the url to use for accessing the file
    feedpath: the pathname of the feed to add the file to
      
    """

    if not os.path.exists(feedpath):
        print 'Creating new feed {0} with title {1}'.format(feedpath, title)
        feed = feeds.TimeshiftFeed.create(feedpath, 
                                          title=title, 
                                          feedurl=urljoin(url, feedpath))
    else:
        feed = feeds.TimeshiftFeed(feedpath)

    feed.add_entry(title=os.path.basename(urlparse.urlparse(url).path),
                   enclosure=url,
                   itemtype='audio/mpeg',
                   summary=url)
    feed.write()


def main(name, config_file):
    parser = ConfigParser.ConfigParser()
    successful = parser.read(config_file)
    if len(successful) == 0:
        raise ValueError('Cannot open configuration file {0}.'.format(
                         config_file))

    timestamp = time.strftime('%Y%m%d%H%M')
    filename = '{0}-{1}.mp3'.format(name, timestamp)
    filepath = os.path.join(parser.get(name, 'basedir'), filename)

    length = parser.getint(name, 'duration')

    _mutter("Recording to {0} at {1} for {2} seconds".format(
        filepath, timestamp, length))
    sys.stdout.flush()

    download.download_time_limit(parser.get(name, 'url'),
                                 filepath, 
                                 length)

    fileurl = os.path.join(parser.get(name, 'baseurl'),
                           os.path.basename(filepath))
    feedpath = os.path.join(parser.get(name, 'basedir'),
                            parser.get(name, 'feedfile'))

    add_to_feed(fileurl, feedpath, title=parser.get(name, 'title'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Record internet broadcast",)

    parser.add_argument('name', 
                        help="Name of the broadcast that should be recorded",
                        nargs=1)
    parser.add_argument('--config',
                        default='timeshift.conf',
                        help="Configuration file (default=timeshift.conf)",
                        nargs='?')
    parser.add_argument('--verbose', '-v', default=False,
                        help="Print output on what is being done",
                        action='store_true')

    args = parser.parse_args()
    if args.verbose:
        DEBUG=True
    sys.exit(main(args.name[0], args.config))
