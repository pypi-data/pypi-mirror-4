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

import string, time, uuid

import feedparser, rfc3339

class TimeshiftFeed(object):

    """A simple feed object for timeshifted podcasts."""
    
    HEADER_STRING = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
<title type="text">$title</title>
<link href="$feedurl" rel="self" />
<id>$uuid</id>
<updated>$now</updated>
"""
    HEADER = string.Template(HEADER_STRING)

    INITIAL = string.Template(HEADER_STRING+"</feed>")

    ENTRY = string.Template("""<entry>
<id>$id</id>
<title type="text">$title</title>
<updated>$update_time</updated>
<link rel="enclosure" href="$itemurl" type="$itemtype">
<summary type="text">$summary</summary>
</entry>
""")

    def __init__(self, filename):
        """Open an existing feed object."""
        self.filename = filename
        self.feed_dict = feedparser.parse(filename)

    @classmethod
    def create(cls, filename, title='', feedurl=''):
        """Create a new feed with filename."""
        with open(filename, 'w') as f:
            f.write(cls.INITIAL.substitute({
                'title': title,
                'feedurl': feedurl,
                'uuid': cls.new_uuid(),
                'now': cls.now(),
                })
                )
        return cls(filename)

    @classmethod
    def now(cls):
        return rfc3339.rfc3339(time.time())

    @classmethod
    def new_uuid(cls):
        return uuid.uuid4().urn

    def _generate(self):
        """Return a string generator of this feed."""
        yield self.HEADER.substitute({
            'title': self.feed_dict['feed']['title'],
            'feedurl': self.feed_dict['feed']['links'][0]['href'],
            'uuid': self.feed_dict['feed']['id'],
            'now': self.now()})

        for entry in self.feed_dict['entries']:
            yield self.ENTRY.substitute({
                'title': entry['title'],
                'id': entry['id'],
                'update_time': entry['updated'],
                'itemurl': entry['links'][0]['href'],
                'itemtype': entry['links'][0]['type'],
                'summary': entry['summary']})

        yield "</feed>\n"

    def write(self):
        with open(self.filename, 'w') as f:
            for chunk in self._generate():
                f.write(chunk)

    def add_entry(self, title='', enclosure='', itemtype='', summary=''):
        self.feed_dict['entries'].append({
            'title': title,
            'links': [{'href': enclosure, 'rel': 'enclosure', 'type': itemtype}],
            'summary': summary,
            'id': self.new_uuid(),
            'updated': self.now()})


