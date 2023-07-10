from pipeline.BaseLinker import BaseLinker
from typing import TypedDict
from pipeline.WikidataObject import WikidataObject, from_uri
import os
import requests

# FALCON2_URL = os.environ["FALCON2_URL"]

class Falcon2Linker(BaseLinker):
  def __init__(self):
    super().__init__(name="Falcon2Base")
  
  def link(self, utterance: str):
    results = {
      "utterance": utterance,
      "ents": [],
      "rels": [],
    }

    falcon2_response = self.link_falcon2(utterance)
    entities = falcon2_response[0]
    relations = falcon2_response[1]

    for ent in entities:
      # Will always be wd:
      results["ents"].append(from_uri(ent, as_type="json"))
    
    for rel in relations:
      # Will always be wdt:
      rel = rel.replace("http://www.wikidata.org/entity/",
                        "http://www.wikidata.org/prop/direct/")
      results["rels"].append(from_uri(rel, as_type="json"))

    return results
  
  def link_falcon2(self, utterance):
    r = falcon2_call(utterance, mode='local')
    entities = [x["URI"] for x in r['entities_wikidata']]
    relations = [x["URI"] for x in r['relations_wikidata']]
    return entities, relations
    
    

def falcon2_call(text,mode='short'):
  headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
  try:
    text = text.replace("What's", "What is") # Code crashes if you use What's or whats
    text = text.replace("what's", "what is")
    text=text.replace('"','')
    text=text.replace("'","")
    if mode == 'local':
      url = 'http://localhost:6000/linker'
      payload = '{"text":"'+text+'"}'
      r = requests.post(url, data=payload.encode('utf-8'), headers=headers)
      if r.status_code == 200:
        response=r.json()
        # print(response)
        return response
      else:
        r = requests.post(url, data=payload.encode('utf-8'), headers=headers)
        if r.status_code == 200:
          response=r.json()
          return response
      raise Exception("No response recieved from SPARQL endpoint") 
    elif mode=='short':
      url = 'https://labs.tib.eu/falcon/falcon2/api?mode=short&db=1'
      entities_wikidata=[]
      payload = '{"text":"'+text+'"}'
      r = requests.post(url, data=payload.encode('utf-8'), headers=headers)
      if r.status_code == 200:
        response=r.json()
        print(response)
        for result in response['entities_wikidata']:
          entities_wikidata.append(result["URI"])
      else:
        r = requests.post(url, data=payload.encode('utf-8'), headers=headers)
        if r.status_code == 200:
          response=r.json()
          for result in response['entities_wikidata']:
            entities_wikidata.append(result[0])
      return map(lambda s: s.replace('<','').replace('>',''), entities_wikidata)
    else:
      url = 'https://labs.tib.eu/falcon/falcon2/api?mode=long&db=1'
      payload = '{"text":"'+text+'"}'
      r = requests.post(url, data=payload.encode('utf-8'), headers=headers)
      if r.status_code == 200:
        response=r.json()
        # print(response)
        return response
      else:
        r = requests.post(url, data=payload.encode('utf-8'), headers=headers)
        if r.status_code == 200:
          response=r.json()
          return response
      raise Exception("No response recieved from SPARQL endpoint") 

  except Exception as e:
    raise e

if __name__ == "__main__":
  sample_linker = Falcon2Linker()
  sample_utterance = "What is the operating income of Qantas and Delta Airlines?"
  sample_result = sample_linker.link_raw(sample_utterance)
  print(sample_result)