import firebase_admin
import datetime
import asyncio
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db=firestore.client()




async def get_query_results(string_query):
    docs = db.collection('queries').where("name","==",string_query).get()
    for doc in docs:
        dict_query = doc.to_dict()
        list_query = list(dict_query.values())
        return(list_query) #returns results as list

        #id_doc = doc.id 
        #doc_ref = db.collection(u'queries').document(id_doc).get({u'entities'}).to_dict()
        #for value in doc_ref.values():
            #entities_list = [d['entity'] for d in value]
            #return(entities_list)
            #these lines above would return the actual entities fromm query in a list format if needed 
    else: 
        return None



async def get_entity(string_name):
    docx = db.collection('entities').where("name","==",string_name).get()
    for doc in docx:
        dict_ent = doc.to_dict() #returns all results of the entitiy as a dictionary
        list_ent = list(dict_ent.values())
        return(list_ent) #returns all results as list
    else: 
        return None



async def merge_entity(string_name, validCategories = [],invalidCategories = [],description = '', imageUrl = ''):
    docs = db.collection('entities').where("name","==",string_name).get()
    for doc in docs:
        ref = doc.to_dict()
        x = len(ref.keys())
        if x>0:
            key = doc.id
            db.collection('entities').document(key).set({'name':string_name,'description':description,'imageUrl':imageUrl},merge=True)
            ref = db.collection('entities').document(key)
            ref.update({u'invalidCategories':firestore.ArrayUnion([invalidCategories]),u'validCategories':firestore.ArrayUnion([validCategories])})
            break 
    else:
        db.collection('entities').add({'name':string_name,'validCategories':validCategories,'invalidCategories':invalidCategories,'description':description,'imageUrl':imageUrl})
#merges new data with specific existing entity in database
#if it doesn’t exist, the function create its



#this function assumes recommendations with be a list of dictionaries contatining the entities with the key 'entity'
#example --> [{'entity':'test','score':2},{'entity':'test2','score':4}]
def store_query_to_cache(string_query, string_category, string_googleResults,recommendations):
    check_query_exist = db.collection('queries').where('name','==',string_query).get()
    for doc in check_query_exist: #first checks to see if any documents exist with same string_query
        ref = doc.to_dict()
        x = len(ref.keys())
        if x>0:
            break
    else:
        for recs in recommendations:              
            entity_names = recs['entity']
            entity_list = [entity_names]
            for ent in entity_list:
                merge_entity(ent,'','','','')    #merges the entities from recommendations so we can get the path from each new document to store in query document
            else:
                entities_ref = db.collection('entities').where("name", "==", entity_names).get()
                for doc in entities_ref:
                    idd = doc.id 
                    ref = db.collection('entities').document(idd)
                    recs['entity'] = ref       #lines 67-72 are what convert the entity string to the path of each entity document
        db.collection('queries').add({'name':string_query,'string category':string_category, 'googleResults':string_googleResults,'lastValidated':datetime.datetime.now(tz=datetime.timezone.utc),'entities':recommendations})

