import os

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

def process_masked_query(masked_string: str, path_to_vocab_text: os.PathLike = None) -> str:

    _, vocab_dict = get_vocab_dicts(path_to_vocab_text)
    
    return unmask(masked_query=masked_string, vocab_dict=vocab_dict) 
