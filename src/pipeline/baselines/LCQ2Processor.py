from LCQ2Linker import LCQ2WikiDataLinker

import json
from pathlib import Path

class LCQ2WikidataProcessor:

  def __init__(self, entities_json_path, relations_json_path, name="LCQ2WikidataProcessor"):

     assert Path(entities_json_path).exists()
     assert Path(relations_json_path).exists()

     super()

     self.linker = LCQ2WikiDataLinker(entities_json_path, relations_json_path)
     self.num_vars = 6

  def preprocess(self, utterance, wikisparql_gold):

    # Processing outputs
    wikisparql_replacement_table = {
      "(": " ( ", ")": " ) ",
      "{": " { ", "}": " } ",
      "wd:": "wd: ",
      "wdt:": "wdt: ",
      " p:": " p: ",
      " ps:": " ps: ",
      "pq:": "pq: ",
      ",": " , ",
      ",'": ", '",
      "'": " ' ",
      ".": " . ",
      "=": " = ",
      "  ": " ",
    }
    sparql = wikisparql_gold
    
    for k, v in wikisparql_replacement_table:
        sparql = sparql.replace(k, v)
    
    sparql = sparql.lower()

    links = self.linker.link(utterance=utterance, sparql=sparql)

    sparql = self.standardize_vars(sparql)
  
  def standardize_vars(self, sparql):
    newvars = [f"?vr{i}" for i in range(self.num_vars)]
    sparql_split = sparql.split()
    variables = set([x for x in sparql_split if x[0] == "?"]) # {?var, ?obj}
    
    for i, var in enumerate(sorted(variables)):
      sparql = sparql.replace(var, newvars[i]) # Standardize var names
    
    return sparql

class BaselineMasker:
  def __init__(self, vocab_json_path):
    super()

    assert Path(vocab_json_path).exists()

    with open(vocab_json_path, "r") as f:
      self.vocab_mask = json.load(f)
      self.vocab_unmask = {}
      for k,v in self.vocab_mask:
        self.vocab_unmask[v] = k
  
  def _replace_with_dict(self, text_input, lut):
    split = text_input.split()

    for i, item in enumerate(split):
      if item in lut:
        split[i] = lut[item]

    return " ".join(split).strip()

  def mask(self, text_input):
    
    return self._replace_with_dict(self, text_input, self.vocab_mask)
  
  def unmask(self, text_input):

    return self._replace_with_dict(self, text_input, self.vocab_unmask)