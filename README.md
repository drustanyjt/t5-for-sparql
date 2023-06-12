# T5 For SPARQL

I am trying to train an LLM model that can convert Natural Language Questions to SPARQL.


## Some useful Commands

For executing notebooks with sreen output [papaermill docs](https://papermill.readthedocs.io/en/latest/usage-cli.html):

```bash
papermill text2sparql.ipynb test2sparql.papermill.ipynb --stdout-file --no-progress-bar
```