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
from Thread import FourchapyThread
from Errors import NoDataReturnedError, ThreadNotFoundError  # Don't import *; it will overwrite logging vars

class FourchapyThreadPage(Fetch4chan):
    """ Represent a page of threads for a given board.     
    """

    def __init__(self, boardID, pageID, proto = 'http', **kw):
        self.Proto = proto
        self.Board = boardID
        self.Page = int(pageID)
        
        log(10, "Creating %r - board:%r page:%r", self, boardID, pageID)
        self.URL = '%s://api.4chan.org/%s/%d.json' % (self.Proto, self.Board, self.Page)
        
        Fetch4chan.__init__(self, **kw)
    
    @Fetch4chan.addLazyDataObjDec(attrName = 'Threads')
    def updateThreadsList(self, sleep = True):
        """ Download and update local data with data from 4chan. """
        threads = []
        try:
            json = self.fetchJSON(sleep = sleep)
        except NoDataReturnedError:
            raise ThreadNotFoundError, "Page number %d from %r was not found on the server. " % (self.Page, self.Board)
        
        for data in json['threads']:
            threads.append(FourchapyThread(
                                          boardID = self.Board,
                                          threadID = int(data['posts'][0]['no']),
                                          proto = self.Proto,
                                          proxies = self.Proxies,
                                          )) 
        log(10, 'Found %d threads for %r', len(threads), self)
        return threads
    
    @Fetch4chan.addLazyDataObjDec(attrName = 'ThreadsDict')
    def updateThreadsDict(self, sleep = True):
        """ Download and update local data with data from 4chan. """
        ret = {}
        
        for thread in self.Threads:
            ret[thread.Thread] = thread
            
        log(10, 'Found %d threads for %r', len(ret), self)
        return ret
    
    def __repr__(self):
        return "<ThreadPage %r %r>" % (self.Board, self.Page)
