#
# Copyright 2012 keyes.ie
#
# License: http://jkeyes.mit-license.org/
#

from .media_range import MediaRange

class AcceptHeader(object):

    def __init__(self, raw_header):
        self.media_ranges = []
        
        mranges = raw_header.split(',')
        for mr in mranges:
            mr = mr.strip()
            self.media_ranges.append(MediaRange(mr))
        self.media_ranges.sort(reverse=True)
        
    def __iter__(self):
        for mr in self.media_ranges:
            yield mr
