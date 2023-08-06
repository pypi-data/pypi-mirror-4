''' Fetch 4chan API data in a 4chan-friendly fashion
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

from urllib import urlopen
import datetime
from json import loads
import time

class InvalidDataReturnedError(ValueError):
    """ The data from 4chan's servers isn't valid """

class NoDataReturnedError(InvalidDataReturnedError):
    """ An empty JSON file was downloaded from 4chan. This usually means that the thread
    is dead/deleted. 
    """

class Fetch404Error(ValueError):
    """ Got a 404 when trying to load a URL """

class ThreadNotFoundError(Fetch404Error):
    """ The requested thread doens't exist anymore. 
    """

class RequestRateTooHigh(RuntimeError):
    """ We're making requests faster than 4chan allows. 
    See https://github.com/4chan/4chan-API#api-rules for request rate details.
    """ 
    
    
