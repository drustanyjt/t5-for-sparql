import argparse
import os
from pathlib import Path
from collections import OrderedDict

import transformers
from transformers import T5Tokenizer, T5ForConditionalGeneration

import torch

def filter_gpus(gpus: str):
    """Sets the envrionment variables needed for filtering GPU visibility.

    Args:
        gpus (str): The GPUs to use. Should be comma delimited.
    """
    os.environ["CUDA_VISIBLE_DEVICES"] = gpus

def get_model(model_name: str = None, model_path: str = None, state_dict_path: str = None):
    """Returns a model loaded in memory

    Args:
        model_name (str, optional): Name of a model.
        model_path (str, optional): Path to a model saved with
            `save_pretrained()`. Defaults to None.
        state_dict_path (str, optional): Path to a state_dict save with
            `torch.save()`. Defaults to None.
    """

    if model_path:
        model = T5ForConditionalGeneration.from_pretrained(model_path, device_map='auto')

    if state_dict_path:
        state_dict = torch.load(state_dict_path)
        new_dict = OrderedDict()

        for key, state in state_dict.items():
            new_dict[key.removeprefix(r"model.")] = state
        state_dict = new_dict

        # print("Model's state_dict:")
        # for param_tensor, tensor in state_dict.items():
        #     print(param_tensor, "\t", tensor.size())

        model = T5ForConditionalGeneration.from_pretrained(
            model_name, device_map = 'auto')
        model.load_state_dict(state_dict)

    assert model is not None

    return model


def unmask(masked_query: str, vocab_dict: dict):

    masked_query = masked_query.replace(">", "> ").replace("<", " <")
    tokens_to_remove = ["<pad>", "</s>", "<unk>", "<s>"]
    for token in tokens_to_remove:
        masked_query = masked_query.replace(token, "")
    masked_query_list = masked_query.strip().split()

    for i in range(len(masked_query_list)):
        if masked_query_list[i] in vocab_dict:
            masked_query_list[i] = vocab_dict[masked_query_list[i]]
        
    unmasked_query = " ".join(masked_query_list)
    

    return unmasked_query

def get_vocab_dicts(vocab_path: str) -> tuple:

    with open(vocab_path) as f:
        vocab = list(map(lambda x: x.strip(), f.readlines()))
        vocab.append('null')
    
    vocab_dict = {}
    reverse_vocab_dict = {}
    for i, text in enumerate(vocab):
        key = text
        value = f'<extra_id_{i}>'
        vocab_dict[key] = value
        reverse_vocab_dict[value] = key
    
    return vocab_dict, reverse_vocab_dict
        

def get_tokenizer(model_name: str = "t5-small"):

    tokenizer = T5Tokenizer.from_pretrained(model_name)

    return tokenizer

def main():
    """Main function.

    Raises:
        SystemExit: Generic error to terminate the script.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("model")
    parser.add_argument("vocab")
    parser.add_argument("--gpu")

    args = parser.parse_args()

    model_path = Path(args.model)
    vocab_path = Path(args.vocab)

    if args.gpu:
        filter_gpus(args.gpu)

    if not model_path.exists():
        print("The target dir does not exist")
        raise SystemExit(1)
    
    if not vocab_path.exists():
        print("The target vocab does not exits")
        raise SystemExit(1)

    model = get_model(model_name="t5-small", state_dict_path=model_path)
    print(model.hf_device_map)
    model.eval()
    tokenizer = get_tokenizer(model_name="t5-small")

    vocab_dict, reverse_vocab_dict = get_vocab_dicts(vocab_path)

    end = False
    while not end:
        utterance = input("Ask a question:\n")
        if utterance == "end":
            break
        model_inputs = tokenizer(utterance, padding=True, return_tensors="pt",
                                 max_length=512, truncation=True)
        model_inputs.to(0)
        outputs = model.generate(model_inputs.input_ids, max_length=200, num_beams=10,
            attention_mask=model_inputs.attention_mask, early_stopping=True,
            output_attentions=True, output_hidden_states=True)

        generated_query = tokenizer.batch_decode(outputs, skip_special_tokens=False)
        unmasked_utterance = unmask( utterance, reverse_vocab_dict )
        sparql = unmask( generated_query[0], reverse_vocab_dict )
        # print( generated_query[0] )
        print()
        print("Unmasked input:\n" + unmasked_utterance)
        print()
        print("Unmasked output:\n" + sparql )
        print()



if __name__ == "__main__":
    main()
