# T5 For SPARQL

I am trying to train an LLM model that can convert Natural Language Questions to SPARQL.

## Overview

This README sums up my research and experiments over the past 3 months on Text-2-SPARQL using T5.

## Current State of Text-2-SPARQL

The current approach for working on Text-2-SPARQL.

## Benchmarks

KGQA ([code](), [website]()), is an online leaderboard tracking results in Text-2-SPARQL conversion.
I made use of LC-QuAD 2.0 ([code](), [paper]()), because I found most of the papers I referenced to also make use of it.

## Entity + Relation Linking

In NLP research in general, entity linking is the task of linking entities in a text to some knowledge base.
For Text-2-SPARQL, there are however two kinds of objects we want to link to:

1. Entities (Nodes in a KG)
2. Relations (Edges in a KG)

Entity linking seems to be an easier task, and there are more solutions available for it.
A commonly cited method is **Falcon 2.0** ([code](), [paper]()).
It makes use of rules the author came up with to determine which phrases represent entities in a given utterance,
and then uses a search algorithm to match these entities to the likeliest human-readable labels.
**Entity Linking for Questions** with Blink ([code](), [paper]()) by Meta is an entity linker for Wikipedia, but also provides a mapping from Wikipedia pages to Wikidata entities.
ELQ is a Bert-based entity linker, and comes with a method for modifying the knowledge base it links too.

Relation linking is slightly more troublesome. It is also a problem more specific to Knowledge graphs than general Entity linking.
Falcon 2.0 has worse results on relation linking than on entity linking.

## Some useful Commands

For executing notebooks with sreen output [papermill docs](https://papermill.readthedocs.io/en/latest/usage-cli.html):

```bash
papermill text2sparql.ipynb test2sparql.papermill.ipynb --stdout-file --no-progress-bar
```


## Dev Log

### Week 3: 5 June - 11 June

This week I presented my findings on the Text 2 SPARQL task to Zhiyuan,
and we decided that it would be worthwhile to pursue the work by Bannerjee on finetuning T5.
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

### Week 4: 12 June - 17 June

FALCON seems to succeed on the identifying hidden relations with no corresponding natural language label.

Falcon has an F1 score of 83% on LC-QuAD
Falcon 2.0 has an F1 score of 53% on LC-QuAD 2.0
GenRL [2021](https://arxiv.org/pdf/2108.07337v1.pdf)
Learning Abstract Meaning Representation [2021](https://arxiv.org/pdf/2012.01707.pdf)
Implicit RL [2022](https://aclanthology.org/2022.findings-acl.312/0)
Entity Linking using AMR [2023](https://2023.eswc-conferences.org/wp-content/uploads/2023/05/paper_Steinmetz_2023_Entity.pdf)

#### 16 May

Found out today that I was training T5 on **10%** of the dataset, and evaluating on 90%.
This explained the overfitting issue, but also it was 80% accurate.

I switched it to **70%** and **30%**.

#### Plan

There are a few experiments that might be useful to try.
    1. Finetuning T5 without passing any schema information as inputs,
    relying on T5 to learn which words should be replaced with tokens.
    2. Testing the ability for Falcon and EARL to retrieve Entities and Relations.

It would probably speed up development if I convert this into a pipeline.

Training the model has taken more time than anticipated.
Even using `t5-small` sometimes CUDA runs out of memory during evaluation.
If we can convert this into a python pipeline, it should be trivial to wrap this in Docker/Singularity and train on NUS HPC.


### Problems

Falcon2 does not distinguish between different prefixes.
All prefixes default to wdt (wikidata entity).
These are valid links but do not work with the SPARQL endpoint

### How
[LC-QuAD 2.0](http://jens-lehmann.org/files/2019/iswc_lcquad2.pdf)
[QALD 9](https://ceur-ws.org/Vol-2241/paper-06.pdf)
[KGQA](https://kgqa.github.io/leaderboard/)

## Approaches
### Text 2 SQL
Well established problem with common benchmarks. (Dr.SPIDER)
T5 + Picard
Fine-tuning with "serialized inputs".

### LLM without any annotations.
SGPT_Q, Text2SPARQL4RDF

### Using an intermediary 
ValueNet4SPARQL

### Two Subtasks
Entity/Relation Linking & Query Generation

T5-Baseline (Entities and relations)
SGPT_Q,K (Entities only)

## Results for 2 Sub Tasks


### Entity/Relation Linking
Falcon 2.0 (without reranking)
1e1r
5e5r
10e10r

Blink/ELQ

### Qeury Generation
T5 Reported, T5 Actual

## Limitations


## Challenges
