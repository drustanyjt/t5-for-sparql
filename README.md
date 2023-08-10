# T5 For SPARQL

## Overview

This README sums up my research and experiments over the past 3 months on Text-2-SPARQL.
1. Splitting Text-2-SPARQL into entity/relation linking and query generation might be effective.
1. An LLM can be trained to change the prefix of the annotations when necessary.
1. A dataset with higher recall and lower precision results in a better model when finetuning if not
all entities/relations are guaranteed,
and a worse model when correct entities/relations are not guaranteed.

## Benchmarks

KGQA ([code](https://github.com/KGQA/leaderboard), [website](https://kgqa.github.io/leaderboard/)), is an online leaderboard tracking results in Text-2-SPARQL conversion.
I made use of LC-QuAD 2.0 ([data](https://figshare.com/projects/LCQuAD_2_0/62270), [paper](https://jens-lehmann.org/files/2019/iswc_lcquad2.pdf)), because I found most of the papers I referenced to also make use of it.

## Entity + Relation Linking

In NLP research in general, entity linking is the task of linking entities in a text to some knowledge base.
For Text-2-SPARQL, there are however two kinds of objects we want to link to:

1. Entities (Nodes in a KG)
2. Relations (Edges in a KG)

Entity linking seems to be an easier task, and there are more solutions available for it.
A commonly cited method is **Falcon 2.0** ([code](https://github.com/SDM-TIB/falcon2.0), [paper](https://arxiv.org/pdf/1912.11270.pdf)).
It makes use of rules the author came up with to determine which phrases represent entities in a given utterance,
and then uses a search algorithm to match these entities to the likeliest human-readable labels.
**Entity Linking for Questions** with Blink ([code](https://github.com/facebookresearch/BLINK/tree/main/elq), [paper](https://aclanthology.org/2020.emnlp-main.522.pdf)) by Meta is an entity linker for Wikipedia, but also provides a mapping from Wikipedia pages to Wikidata entities.
ELQ is a Bert-based entity linker, and comes with a method for modifying the knowledge base it links too.

Relation linking is slightly more troublesome. It is a problem more specific to Knowledge graphs than general Entity linking.
Falcon 2.0 attempts to do relation linking, but fairs worse in this regard than on entity linking, and there is much less study on Relation Linking so far.
Additionally unlike entities, relations do not have corresponding Wikidata page entries.

Due to the access to WikiData being rate limited,
I modified Falcon 2.0 to not rerank entities/relations by querying an actual knowledge graph
(this was originally used to favour entities and relations that did exist as triples).
It might be possible to set up a locally hosted for of WikiData,
but it would require a substantial amount of disk space,
and approximately 2 weeks to load indexes into memory.

I measured the Recall of using Falcon 2.0 on Entity Linking and Relation Linking.
Recall is the number of correctly mentioned entites/relation over the total number of desired entites/relations.
Results are as so:

|   |  Entity Recall | Entity All Present | Relation Recall  | Relation All Present |
|---|---|---|---|---|
| k=1  | 0.56  | 0.45  | 0.30  |  0.16 |
| k=5  | 0.61  |  0.50 |  0.30 | 0.17  |
| k=10  | 0.68  | 0.57  | 0.41  |  0.26 |

The **All Present** columns show the number of utterances where all entities/relations needed in the WikiSPARQL query
were succesfully linked. The **k** value represents the number of entites/relations listed per mention detected.

The results for using ELQ are as so:

|   |  Entity Recall | Entity All Present |
|---|---|---|
| Fine Tuned on Wikipedia  | 0.716  | 0.587  |
| Fine Tuned on WebQSP  | 0.671  |  0.533 |

While the dataset generated by ELQ was not used for query generation, their high F1 score on entity linking is promising.
However, relation linking would still need to be done by some other method in this case.

## Query Generation

In Modern Baselines for SPARQL semantic parsing ([code](https://github.com/debayan/sigir2022-sparqlbaselines), [paper](https://arxiv.org/abs/2204.12793)) Bannerjee showed that when utterances are annotated with entities and relations,
an LLM can be finetuned to convert these annotated questions to SPARQL quite reliably.

My intuition is that T5 and other LLMs are able to learn the structure of a SPARQL query well,
but due to the sheer number of complex Entity and Relation URIs,
no LLM would be effective at converting an Natural Language Question into a SPARQL query without extra information
about the URIs of the relevant entities/relations.

In the experiments I conducted, it also seems that the correctness of the prefix of relations is not too important.
Bannerjee uses the exact correct prefix in his annotations (such as p: or ps:) when needed.
Howver I did my experiments always assuming the default wdt: prefix,
and T5 was able to learn to adjust the prefixes as needed for the SPARQL query.
This probably goes to show the type of prefix to be used can be somewhat inferred from the given Natural Language Question.

The previously mentioned SGPT uses another technique in training where he masks the entity ID as well in the annotations.
This might be useful to try.

I tried various experiments to investigate how the quality of annotations affects the finetuned model.
Not all required entities and relations were guaranteed to be present,
having more annotations would increase performance.
When all required entites and relations were present, having additional annotations (ie lower precision) would decrease performance.
The results are summarised below:

|   |  kE, kR | kE+G | kE+G, kR+G |
|---|---|---|---|
| k=1  | 0.191  | 0.520  | 0.801  |  
| k=5  | 0.201  |  0.472 |  0.690 |
| k=10  | 0.278  | 0.469  | 0.640 |

The **kE, kR** column uses the Falcon 2.0 generated dataset, with top k entities/relations appended.
The **kE+G** column uses the Falcon 2.0 generated dataset with top k entities, modified to include any missing but necessary entities.
The **kE+G, kR+G** column uses the Falcon 2.0 generated dataset with top k entities and relations,
modified to include all missing but necessary entities or relations.

## Using This Repo

### Setup Conda Environment

Use the `environment.yml` file to create a new conda environment like so:

```bash
conda create --name text2sparql --file environment.txt
```

Then activate it as you would any other environment.

```bash
conda activate text2sparql
```

### Running Code

Run the `experiments.ipynb` notebook to replicate the fine-tuning process using specified training data.
Currently the `LINKS_PATH` variable must point to a json file containing a list of lists of JSON objects, an example would be:

```json
[
  [
    {
      "utterance":"What periodical literature does Delta Air Lines use as a moutpiece?", // Must have an utterance in the first json
      "ents":[],
      "rels":[]
    },
    {
      "utterance":"What periodical literature does Delta Air Lines use as a moutpiece?", 
      "fragments":[]
    },
    {
      "inputs":"What periodical literature does Delta Air Lines use as a moutpiece? ", // Must have an input in the third json
      "labels":"<extra_id_6> <extra_id_21> <extra_id_39> <extra_id_19> <extra_id_33> <extra_id_53> q188920 <extra_id_54> p2813 <extra_id_39> <extra_id_38> <extra_id_39> <extra_id_54> p31 <extra_id_53> q1002697 <extra_id_15>" // Must have a masked label in the third json
    }
  ],
]
```

This is just the structure of the data I output by default when annotating with Falcon 2.0.
`experiments.ipynb` accesses the fields I commented to generate a train, val and test dataset.

Additionally, to view the results of falcon links you can use the `linking.ipynb` notebook.

### Using Papermill

Papermill ([docs](https://papermill.readthedocs.io/en/latest/)) module allows us to run python notebooks from the command line,
and should be available in the conda environment.

To run `experiments.ipynb` for example use:

```bash
papermill experiments.ipynb experiments.papermill.ipynb --no-progress-bar --stdout-file 
```

This can be used in conjunction with `tmux` or `screen` to run the notebook in the background.

## Various Other Setups

### LC-QuAD 2.0
The file for LC-QuAD 2.0 cannot be downloaded directly from [FigShare](https://figshare.com/projects/LCQuAD_2_0/62270) on DSO network.
Instead, you should download the dataset on your personal computer, and then upload it to
a data sharing website that can be accessed by DSO (such as Google Drive),
and download it from there instead.

### Falcon 2.0
I have a seperate [repository](https://github.com/drustanyjt/falcon2.0) for this, with instructions there.
The modified version of Falcon 2.0 comes with a script for generating a dataset
that can be easily used with this repository's finetuning notebook.
If you want to use Falcon 2.0 without modifications, you can access their API online through their [website](https://labs.tib.eu/falcon/falcon2/)
or HTTP requests.

### Blink/ELQ
The Titan server does not have enough RAM to load Blink for ELQ.
You should try to use gpuserver 1 instead for any data processing that it might require.

## Idea Logs
### Text 2 SQL

Originally we wanted to try using methods from Text-2-SQL to Text-2-SPARQL.
This lead us to a few papers

Spider ([website](yale-lily.github.io/spider), [code](https://github.com/taoyds/spider)) is a oft cited benchmark dataset for scehma agnostic Text 2 SQL.

Dr.Spider ([paper](https://arxiv.org/abs/2301.08881)) is a modified version of the Spider dataset, meant to be more difficult.

Picard ([paper](https://arxiv.org/abs/2109.05093), [code](https://github.com/ServiceNow/picard), [huggingface](https://huggingface.co/tscholak/cxmefzzi)) is an algorithm that increases the effectiveness of Text-2-SQL models by modifying beam search to favour producing tokens that form valid SQL,
in consideration of SQL syntax as well as the table and column names in a given schema.
The authors used T5 as a baseline LLM.

We were unable to use these approaches because they relied on fine-tuning with "serialized inputs",
where the schema for each Relational Database was appended to the utterance as annotations, which Knowledge Graphs don't exactly have.

### Using an intermediary 

ValueNet4SPARQL aims to generate an intermediary language (SemQL) that can be converted to both SQL and SPARQL,
and use models finetuned for SQL. The paper is unfortunately removed from online as of writing.

### Other LLMs.
SGPT ([code](https://github.com/rashad101/SGPT-SPARQL-query-generation), [paper](https://jens-lehmann.org/files/2022/ieee_access_sgpt.pdf)) uses GPT2 and a custom encoder architecture that relies on more conventional NLP tokenization and grammar rules.
During the fine-tuning process they also mask the URIs of entities, in the hopes of increasing generalisability.

#### Development Notes

We decided that it would be worthwhile to pursue the work by Bannerjee on finetuning T5.
ValueNet4SPARQL might prove useful for validation of data between knowledge graphs and databases,
but otherwise that and SGPT ill be left alone for now.

From my research, the method that Bannerjee used to retrieve gold entity and questions was as follows:
    0. Where `question` is the original NLQ, `sparql` is the golden SPARQL and `vocab_dict` is a hashtable of SPARQL tokens to special masks.
    1. From the `sparql`, retrieve the listed entities and relations.
    2. Replace relation labels that cannot be found with some null value: `vocab_dict['null']`.
    3. Collate all entities (`wd: q36970`) and entity labels (`Jackie Chan`), as well as relations and relation labels.
    4. Replace tokens in gold sparql query with their masks from `vocab_dict`.
    5. Replace prefixes in collated prefixes with their masks from `vocab_dict`, and append this to the `question`.

This gives a set of modifited NLQs, and modified SPARQL queries, that are used for training.

The scripts are quite messy, so it would probably be better to reorganise the code into functions.

FALCON seems to succeed on the identifying hidden relations with no corresponding natural language label.

Falcon has an F1 score of 83% on LC-QuAD
Falcon 2.0 has an F1 score of 53% on LC-QuAD 2.0
GenRL [2021](https://arxiv.org/pdf/2108.07337v1.pdf)
Learning Abstract Meaning Representation [2021](https://arxiv.org/pdf/2012.01707.pdf)
Implicit RL [2022](https://aclanthology.org/2022.findings-acl.312/0)
Entity Linking using AMR [2023](https://2023.eswc-conferences.org/wp-content/uploads/2023/05/paper_Steinmetz_2023_Entity.pdf)


There are a few experiments that might be useful to try.
    1. Finetuning T5 without passing any schema information as inputs,
    relying on T5 to learn which words should be replaced with tokens.
    2. Testing the ability for Falcon and EARL to retrieve Entities and Relations.

It would probably speed up development if I convert this into a pipeline.

Training the model has taken more time than anticipated.
Even using `t5-small` sometimes CUDA runs out of memory during evaluation.
If we can convert this into a python pipeline, it should be trivial to wrap this in Docker/Singularity and train on NUS HPC.
