from src.pipeline.baselines.LCQ2Linker import LCQ2WikiDataLinker

import re
import json
from typing import Tuple, Union
from pathlib import Path

class LCQ2WikidataProcessor:

  def __init__(self,
               dataset_json_path: Union[str, Path],
               entities_json_path: Union[str, Path],
               relations_json_path: Union[str, Path],
               vocab_json_path: Union[str, Path],
               name="LCQ2WikidataProcessor"):
    """Processor for LCQ2 Wikidata

    Args:
        dataset_json_path: (Union[str, Path]): Path to dataset dict.
        entities_json_path (Union[str, Path]): Path to entities dict.
        relations_json_path (Union[str, Path]): Path to relations dict.
        vocab_json_path (Union[str, Path]): Path to SPARQL vocab dict.
        name (str, optional): Name of model. Defaults to "LCQ2WikidataProcessor".
    """
    assert Path(entities_json_path).exists()
    assert Path(relations_json_path).exists()

    self.linker = LCQ2WikiDataLinker(entities_json_path, relations_json_path)
    self.num_vars = 6
    self.masker = BaselineMasker(vocab_json_path=vocab_json_path)
    self.dataset_path = dataset_json_path
  
  def preprocess_from_json(self, dataset_json_path: Union[str, Path]=None) -> list:
    """Preprocessed from a json file.

    Args:
        dataset_json_path (Union[str, Path], optional): Path to dataset json file.
          If blank, the Processor will default to the json path that it was instantiated with.

    Returns:
        list: Where each item is a dictionary with keys ("input", "label").
    """
    if dataset_json_path is None:
      dataset_json_path = self.dataset_path
    assert Path(dataset_json_path).exists()

    with open(dataset_json_path) as f:
      data = json.load(f)
    
    preprocessed_dataset = []
    for i, inst in enumerate(data):
      wikisparql_gold = inst['sparql_wikidata']
      if inst['question'] is None:
        utterance = inst["NNQT_question"]
      else:
        utterance = inst["question"]
      utterance = utterance.replace("{", "").replace("}", "")
      try:
        new_utterance, new_sparql = self.preprocess(utterance, wikisparql_gold)
        preprocessed_dataset.append({"input":new_utterance, "label":new_sparql})
      except ValueError as e:
        print("Error found:", e)
        print("Skipping instance...")

    return preprocessed_dataset

  def preprocess(self, utterance: str, wikisparql_gold: str):

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
    sparql, hashi = self._mask_filter_literals(wikisparql_gold)
    
    for k, v in wikisparql_replacement_table.items():
        sparql = sparql.replace(k, v)
    
    sparql = sparql.lower()

    links = self.linker.link(utterance=utterance, sparql=sparql)

    sparql = self._standardize_vars(sparql)

    sparql = self.masker.mask(sparql)

    for keys, val in hashi.items():
      sparql = sparql.replace(keys, val)
    
    utterance = self._mask_ents_rels(utterance,
                                     links["ents"]+links["rels"])
    
    return utterance, sparql
    
  
  def _mask_ents_rels(self, utterance: str, ents_rels: list) -> str:
    vocab_dict = self.masker.vocab_mask

    for uri in ents_rels:
      item = uri["prefix"] + ":" + uri["id"] + " " + uri["label"]
      item=item.replace('wd:',vocab_dict['wd:']+' ')
      item=item.replace('wdt:',vocab_dict['wdt:']+' ')
      item=item.replace('p:',vocab_dict['p:']+' ')
      item=item.replace('ps:',vocab_dict['ps:']+' ')
      item=item.replace('pq:',vocab_dict['pq:']+' ')
      utterance=utterance+" "+vocab_dict["[DEF]"]+" "+item
    
    return utterance


  
  def _mask_filter_literals(self, wikisparql: str) -> Tuple[str, dict]:
    match_str = r"\'(.*?)\'"
    hashi = {}
    if re.search(match_str, wikisparql):
        lits=re.findall(match_str,wikisparql)
        # print(f"Old: {wikisparql}")
        for j, lit in enumerate(lits):
            idx = j + 1
            wikisparql = wikisparql.replace(f"'{lit.strip()}'", f"'###{idx}'")
            hashi[f'###{idx}'] = lit.strip()
        # print(f"New: {wikisparql}")
    return wikisparql, hashi
  
  def _unmask_filter_literals(self, sparql: str, hashi: dict) -> str:
    for keys in hashi:
      sparql = sparql.replace(keys, hashi[keys])
    



  def _standardize_vars(self, sparql):
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
      for k,v in self.vocab_mask.items():
        self.vocab_unmask[v] = k
  
  def _replace_with_dict(self, text_input, lut):
    split = text_input.split()

    for i, item in enumerate(split):
      if item in lut:
        split[i] = lut[item]

    return " ".join(split).strip()

  def mask(self, text_input):
    
    return self._replace_with_dict(text_input, self.vocab_mask)
  
  def unmask(self, text_input):

    return self._replace_with_dict(text_input, self.vocab_unmask)