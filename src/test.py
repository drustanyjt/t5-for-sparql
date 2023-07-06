from pipeline.baselines.LCQ2Processor import LCQ2WikidataProcessor
from pathlib import Path
import json
import argparse
import sys
from typing import Union


def main():
  baselines = Path(__file__).parent / "pipeline" / "baselines"

  parser = argparse.ArgumentParser()
  parser.add_argument("--data", nargs=1,
                      type=Union[str, Path], default=baselines / "train.json")
  parser.add_argument("--ents", nargs=1,
                      type=Union[str, Path], default=baselines / "ents.json")
  parser.add_argument("--rels", nargs=1,
                      type=Union[str, Path], default=baselines / "rels.json")
  parser.add_argument("--vocab", nargs=1,
                      type=Union[str, Path], default=baselines / "vocab.json")
  parser.add_argument("--saveto")
  parser.add_argument("--out", type=argparse.FileType('w'),
                      default=sys.stdout)
  
  args = parser.parse_args()

  processor = LCQ2WikidataProcessor(
    dataset_json_path=args.data,
    entities_json_path=args.ents,
    relations_json_path=args.rels,
    vocab_json_path=args.vocab
  )

  preprocessed = processor.preprocess_from_json()

  if args.saveto:
    with open(args.saveto, "w") as f:
      json.dump(preprocessed, f, indent=2)

# df = pd.DataFrame(preprocessed)

if __name__ == "__main__":
  main()
