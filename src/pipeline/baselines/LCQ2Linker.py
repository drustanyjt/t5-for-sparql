from pipeline.data_processing import BaseLinker

import re
import json
from pathlib import Path

class LCQ2WikiDataLinker(BaseLinker):

  def __init__(self, entities_json_path, relations_json_path):
    """Creates an ERL for the baseline dataset.

    Args:
        entities_json_path (str): Path to a json with (key, value) as
          (id, label). Example: {"q36970":"Jackie Chan"}
        relations_json_path (str): Path to a json with (key, value) as
          (capitalised id, label). Example: {"P26":"spouse"}
    """
    super(name="BaselineLCQ2Linker")

    assert Path(entities_json_path).exists()

    with open(entities_json_path, "r") as f:
      self.entities = json.load(f)
    
    with open(relations_json_path, "r") as f:
      self.relations = json.load(f)

  def link(self, utterance: str = None, sparql: str = None):
    
    assert sparql and len(sparql) > 0

    result = {
      "ents": [],
      "rels": [],
    }

    # Entity linking
    _ents = re.findall( r'wd: (?:.*?) ', sparql) # ['wd: q188920 ', 'wd: q1002697 ']
    _ents_for_labels = re.findall( r'wd: (.*?) ', sparql) # ['q188920', 'q1002697']
    
    for i in range(len(_ents_for_labels)):
      if "}" in _ents[i]:
        raise ValueError(f"}} found, \nSparql: {sparql}\nReg Entity: {_ents[i]}")
        _ents[i]=""
      
      uri = {
        "prefix": _ents[i].split(":")[0], # wd:
        "id": _ents_for_labels[i], # p2813
        "label": self.entities[_ents_for_labels[i]]
      }

      result["ents"].append(uri)

    # Relation linking
    _rels = re.findall( r'wdt: (?:.*?) ',sparql)
    _rels += re.findall( r' p: (?:.*?) ',sparql)
    _rels += re.findall( r' ps: (?:.*?) ',sparql)
    _rels += re.findall( r'pq: (?:.*?) ',sparql) # ['wdt: p2813 ', 'wdt: p31 ']
    # Missing rdfs:label, not sure if that is important
    
    _rels_for_labels = re.findall( r'wdt: (.*?) ',sparql)
    _rels_for_labels += re.findall( r' p: (.*?) ',sparql)
    _rels_for_labels += re.findall( r' ps: (.*?) ',sparql)
    _rels_for_labels += re.findall( r'pq: (.*?) ',sparql) # ['p2813', 'p31']

    
    for i in range(len(_rels_for_labels)):
      if _rels_for_labels[i].upper() not in self.relations:
        self.relations["P" + _rels_for_labels[i][1:]] = "null"
      
      _rels[i] = _rels[i] + self.relations["P" + _rels_for_labels[i][1:]] + " "
      # wdt: p26 -> wdt: p26 spouse

      uri = {
        "prefix": _rels[i].split(":")[0],
        "id": _rels_for_labels[i],
        "label": self.relations["P" + _rels_for_labels[i]],
      }

      result["rels"].append(uri)
    
    return result
