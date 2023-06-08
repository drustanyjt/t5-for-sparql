
## Picard

The main principle of Picard (Tscholak) is to modify the beam search algorithm used by T5
to generate its output. It is only used at **inference time**
It's like a slightly less functional linter that checks whether
the code being generated is valid or not.
Picard acts as a heuristic, if a given output is invalid, it will skip this example in
the beam search.

### Lexing

Checks if the tokens are valid SQL.

### Parsing Without Guards

Checks if the tokens match column names.

### Parsing With Guards

Checks if the tokens match column names and more.


## T5

A very good pretrained model. Some parts of it include:

### Tokenizer: Piecewise

Some kind of google tokenizer.

### Encoder-Decoder

Nothing to special, this is the normal transformer architecture.


## Idea

Continue to replicate Picard+T5 by Tscholak. (Evaluation metric, Picard)
Try to replicate the results from T5 in Bannerjee 2022, (LC-QuAD). using the KGQA leaderboard.
Convert SQL to SPARQL?.


