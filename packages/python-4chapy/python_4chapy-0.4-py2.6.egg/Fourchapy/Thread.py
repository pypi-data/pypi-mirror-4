'''
Created on Sep 9, 2012

@author: Paulson McIntyre (GpMidi) <paul@gpmidi.net>
'''
#===============================================================================
#    This file is part of 4chapy. 
#
#    4chapy is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    4chapy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with 4chapy.  If not, see http://www.gnu.org/licenses/old-licenses/gpl-2.0.html 
#===============================================================================

# Setup logging
import logging
logger = logging.getLogger("Fourchapy." + __name__)
log = logger.log

from Fetcher import Fetch4chan
from Post import FourchapyPost
from Errors import NoDataReturnedError, ThreadNotFoundError  # Don't import *; it will overwrite logging vars

class FourchapyThread(Fetch4chan):
    """ Represent a thread from a 4chan board
    
    """    

    def __init__(self, boardID, threadID, proto = 'http', **kw):
        self.Proto = proto
        self.Board = boardID
        self.Thread = threadID
        
        log(10, "Creating %r - board:%r thread:%r", self, boardID, threadID)
        self.URL = '%s://api.4chan.org/%s/res/%d.json' % (self.Proto, self.Board, self.Thread)
        
        Fetch4chan.__init__(self, **kw)

    @Fetch4chan.addLazyDataObjDec(attrName = 'Posts')
    def updatePostsList(self, sleep = True):
        """ Download and update local data with data from 4chan. """
        ret = []
        try:
            json = self.fetchJSON(sleep = sleep)
        except NoDataReturnedError:
            raise ThreadNotFoundError, "Thread ID %r from %r was not found on the server. " % (self.Thread, self.Board)
        
        index = 0
        for postData in json['posts']:
            ret.append(FourchapyPost(
                                     board = self.Board,
                                     postData = postData,
                                     proto = self.Proto,
                                     index = index,
                                     proxies = self.Proxies,
                                     ))
            index += 1
            
        log(10, 'Found %d posts for %r', len(ret), self)
        return ret
    
    @Fetch4chan.addLazyDataObjDec(attrName = 'PostsDict')
    def updatePostsDict(self, sleep = True):
        """ Download and update local data with data from 4chan. """
        ret = {}
        
        for post in self.Posts:
            ret[post.Number] = post
            
        log(10, 'Found %d posts for %r', len(ret), self)
        return ret
    
    def __repr__(self):
        return "<Thread %r %r>" % (self.Board, self.Thread)
