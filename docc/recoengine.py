"""

@author: Richil Bhalerao

"""

from data.storage import Storage
import pymongo
from inspect import Traceback
import traceback
from operator import itemgetter, attrgetter
from bson.objectid import ObjectId


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
            interests = newUser['reco_attributes']['interests']
            
            result = self.findMostSimilar(highest_degree, current_proficiency, current_status, programming_languages, interest_level, interests, username)
            return result    
        except:
            traceback.print_exc()
            
    
    def computeJaccardIndex(self, set1, set2):
        n = len(set1.intersection(set2))
        return float(n / float(len(set1)+len(set2)-n))
        #return float(n / float(len(set2)))
    
    
    def findMostSimilar(self, highest_degree, current_proficiency, current_status, programming_languages, interest_level, interests, username):
        try:
            result = {}
            list = [highest_degree, current_proficiency, current_status, programming_languages, interest_level]
            for l in interests:
                list.append(l)
            set1 = set(list)
            
            cursor = self.db['user'].find()
            user_records = [c for c in cursor]
            
            sim_contents = []
            for record in user_records:
                print record
                if record['username']!=username:
                    if 'reco_attributes' in record.keys():
                        if record['ContentId'] != []:
                            print 'in find most similar'
                            list = [
                                record['reco_attributes']['highest_degree'],
                                record['reco_attributes']['current_proficiency'],
                                record['reco_attributes']['current_status'],
                                record['reco_attributes']['programming_languages'],
                                record['reco_attributes']['interest_level']
                                
                            ]
                            
                            for l in record['reco_attributes']['interests']:
                                list.append(l)
                            set2 = set(list)
                            newRecord = [self.computeJaccardIndex(set1, set2), record['ContentId']]
                            sim_contents.append(newRecord)
                        else:
                            print 'in else part'
                        
            if sim_contents:
                print 'sim contents present'
                print sim_contents
                sim_contents = sorted(sim_contents, key=itemgetter(0), reverse=True)
            
            else:
                print 'not a single similar content, so display All contents'
                allcontents = self.db['content'].find()
                contents = [a for a in allcontents]
                for content in contents:
                    print 'CONTENT --> ', content
                    sim_contents.append([1.0, [ObjectId(content['_id'])]])
                
            print sim_contents
            return sim_contents
                                
        except:
            traceback.print_exc()
    
    
    def getMostViewedContent(self, sub_category):
        
        try:
            return self.db['content'].find({'sub_category': sub_category}).sort('count', pymongo.DESCENDING)
        except:
            traceback.print_exc()

            
    def getMostRatedContent(self, sub_category):
        
        try:

            return self.db['content'].find({'sub_category': sub_category}).sort('Rating', pymongo.DESCENDING)
        except:
            traceback.print_exc()
            
    def getViewAllContent(self, sub_category):
        
        try:
            return self.db['content'].find({'sub_category': sub_category})
        except:
            traceback.print_exc()
