from pathlib import Path
import argparse

from pipeline.data_processing import BaseLinker, BaseModel, BaseProcessor

LINKER_DICT = {
    "base": BaseLinker,
}

MODEL_DICT = {
    "base": BaseModel,
}

PROCESSOR_DICT = {
    "base": BaseProcessor,
}


def main():
    dataset_path = Path()
    linker_key = "base"
    model_key = "base"
    processor_key = "base"

    _linker = LINKER_DICT[linker_key]
    _model = MODEL_DICT[model_key]
    _processor = PROCESSOR_DICT[processor_key]

    processor = _processor(dataset_path = dataset_path)
    processor.process_to_json()
    processor.process_to_df()



if __name__ == "__main__":
    main()