"""

@author: Richil Bhalerao

"""

from data.storage import Storage
import pymongo
from inspect import Traceback
import traceback
from operator import itemgetter, attrgetter


class RecoEngine(object):
    
    def __init__(self):
        self.db = Storage().db
    
    
    def getWeSuggest(self, username):
        
        try:
            query = {"username": username}
            newUser = self.db['user'].find_one(query)
            
            highest_degree = newUser['reco_attributes']['highest_degree']
            current_proficiency = newUser['reco_attributes']['current_proficiency']
            current_status = newUser['reco_attributes']['current_status']
            programming_languages = newUser['reco_attributes']['programming_languages']
            interest_level = newUser['reco_attributes']['interest_level']
            
            result = self.findMostSimilar(highest_degree, current_proficiency, current_status, programming_languages, interest_level)
            return result    
        except:
            traceback.print_exc()
            
    
    def computeJaccardIndex(self, set1, set2):
        n = len(set1.intersection(set2))
        #return float(n / float(len(set1)+len(set2)-n))
        return float(n / float(len(set2)))
    
    
    def findMostSimilar(self, highest_degree, current_proficiency, current_status, programming_languages, interest_level):
        try:
            result = {}
            set1 = set([highest_degree, current_proficiency, current_status, programming_languages, interest_level])
            
            cursor = self.db['user'].find()
            user_records = [c for c in cursor]
            
            sim_contents = []
            for record in user_records:
                if 'reco_attributes' in record.keys():
                    set2 = set([
                        record['reco_attributes']['highest_degree'],
                        record['reco_attributes']['current_proficiency'],
                        record['reco_attributes']['current_status'],
                        record['reco_attributes']['programming_languages'],
                        record['reco_attributes']['interest_level']
                    ])
                    newRecord = [self.computeJaccardIndex(set1, set2), record['ContentCompleted']]
                    sim_contents.append(newRecord)
                
            
            sim_contents = sorted(sim_contents, key=itemgetter(0), reverse=True)
            return sim_contents
                                
        except:
            traceback.print_exc()
    
    
    def getMostViewedContent(self):
        
        try:
            return self.db['content'].find().sort('count', pymongo.DESCENDING)
        except:
            traceback.print_exc()

            
    def getMostRatedContent(self):
        
        try:
            return self.db['content'].find().sort('rating', pymongo.DESCENDING)
        except:
            traceback.print_exc()