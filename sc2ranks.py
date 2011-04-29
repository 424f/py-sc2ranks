#!/usr/bin/env python

"""
Implements part of the sc2ranks.com API as described on http://sc2ranks.com

Currently not supported are:
    - Mass base character
    - Mass base character + team information
    - Listing custom divisions
    - Manage custom divisions 
    - Profile search
    - Linking to SC2 Ranks
    
"""
# == Imports ==================================================================

import json
import urllib

# == Module code ==============================================================

class _Enum(object):
    @classmethod
    def is_valid(cls, value):
        values = [v for k, v in cls.__dict__.iteritems() if k.strip('_') == k]
        return value in values

    @classmethod
    def parse(cls, value):
        members = [(k, v) for k, v in cls.__dict__.iteritems() if k.strip('_') == k]
        return members.get(k, None)

class SearchTypes(_Enum):
    Exact = 'exact'
    Contains = 'contains'
    Starts = 'starts'
    Ends = 'ends'

class Regions(_Enum):    
    All = 'all'
    Europe = 'eu'
    Russia = 'ru'
    China = 'cn'
    LatinAmerica = 'ln'
    NorthAmerica = 'us'
    Taiwan = 'tw'
    Korea = 'kr'
    SouthEastAsia = 'sea'

class CharacterDetails(_Enum):
    Character = 'char'
    Teams = 'teams'

class NoSuchCharacterException(Exception):
    pass

class InvalidResponseException(Exception):
    pass    

class SC2Ranks(object):
    def __init__(self, api_key=None, endpoint='http://sc2ranks.com/api'):
        if api_key is None:
            raise ValueError("%s is not a valid API key." % api_key)
    
        self.api_key = api_key
        self.endpoint = endpoint
    
    def search(self, name=None, region=None, search_type='exact', offset=None):
        if region is None or not Regions.is_valid(region):
            raise ValueError('%s is not a valid region.' % region)
        if name is None:
            raise ValueError('%s is not a valid name.' % name)
    
        if offset is None:
            return self._execute('search/%s/%s/%s' % (search_type, region, name))
        else:
            return self._execute('search/%s/%s/%s/%d' % (search_type, region, name, offset))
    
    def get_character(self, name, region, code=None, bnet_id=None, details=CharacterDetails.Character):
        if code is None and bnet_id is None:
            raise ValueError("You must either give a character code or a battle.net identifier.")
        
        if bnet_id is not None:
            return self._execute('base/%s/%s/%s!%s' % (details, region, name, bnet_id))
        elif code is not None:
            return self._execute('base/%s/%s/%s$%s' % (details, region, name, code))
    
    def maximum_bonus_pool(self):
        return self._execute('bonus/pool')
    
    def _handle_error(self, response):
        error = response['error']
        if error == 'no_characters':
            raise NoSuchCharacterException()
        else:
            raise Exception("An unknown error occured: %s" % error)
        
    def _execute(self, path):
        url = '%s/%s?appKey=%s' % (self.endpoint, path, self.api_key)
        
        f = urllib.urlopen(url)
        response_data = f.read()
        f.close()
        
        try:  
            response = json.loads(response_data)
        except Exception, e:
            raise InvalidResponseException("Received an invalid JSON response: %s" % e)
        
        if 'error' in response:
            self._handle_error(response)
        
        return response
        
def main():
    api = SC2Ranks(api_key='sc2sng.com')
    region = Regions.NorthAmerica
    
    print api.maximum_bonus_pool()
    
    characters = api.search(name='BaconEmbargo', region=region)
    
    for character in characters['characters']:
        info = api.get_character(region=region, details=CharacterDetails.Teams, **character)
        print info

# == Script code ==============================================================
    
if __name__ == '__main__':
    main()    
    
# == Authorship information ===================================================
    
__author__  = "Boris Bluntschli"
__credits__ = ""
__licence__ = "GPL"
__version__ = "$Format:%H$"  

# =============================================================================  