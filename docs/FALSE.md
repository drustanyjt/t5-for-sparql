# Wrong examples

I have adopted the terminology used in Banerjee 2022 for some mistakes I spotted.
For each example, I list the entity and relation labels,
**only** the NLQ part of the input (ie without the entity and relations),
the unmasked gold SPARQL, and the unmasked generated SPARQL.

Note also that copying these queries into the [Wikidata Query Service](https://query.wikidata.org/#ask%20where%20%7B%20wd%3AQ1418%20wdt%3AP3362%20%3Fvr0%20filter%20%28%20%3Fvr0%20%3D%20-1100000000%20%29%20%7D)
does not work directly because the entities and relation ids are in lowercase,
and there is an extra space between the prefix and the id.

For example this query is invalid:
> select distinct ?vr0 where { wd: q282003 wdt: p2101 ?vr0 }

And the correct version is:
> select distinct ?vr0 where { wd:Q282003 wdt:P2101 ?vr0 }

## Triple Flip

One of the most common reasons for wrong outputs was the object and subject being swapped like so:

Entites:

```json
{
    "wd:Q282003": "lindane",
    "wdt:P2101": "melting point",
}
```

Input:
> Which is the melting point of lindane?

Gold:
> select distinct ?vr0 where { wd: q282003 wdt: p2101 ?vr0 }

Generated:
> select distinct ?vr0 where { ?vr0 wdt: p2101 wd: q282003 }

## Wrong Intent

ASK instead of SELECT:

Entites:

```json
{
    "wd:Q857640": "Tencent QQ",
    "wdt:P1401": "issue tracker URL",
}
```

Input:
> how many bug tracking systems does tencent qq have?

Gold:
> select ( count ( ?vr0 ) as ?vr1 ) { wd: q857640 wdt: p1401 ?vr0 }

Generated:
> ask where { wd: q857640 wdt: p1401 wd: qq }

## Copy Error

Copied over the wrong tokens from the query.
This first example copied the wrong labels.

Entities:

```json
{
    "wd:Q193507": "Saint Christopher",
    "wdt:P2348": "time period",
    "wdt:P122": "basic form of government",
}
```

Input:
> What is the type of government of Saint Christopher in the Historical Period?

Gold:
> select ?vr0 where { wd: q193507 wdt: p2348 ?vr1 . ?vr1 wdt: p122 ?vr0 }

Gene:
> select ?vr0 where { wd: q193507 wdt: p122 ?vr1 . ?vr1 wdt: p2348 ?vr0 }

This second example coped information from the question incorrectly.

Entities:

```json
{
    "wd:Q1418": "Nokia",
    "wdt:P3362": "operating income",
}
```

Input:
> Is Nokia's operating income -1.1 billion?

Gold:
> ask where { wd: q1418 wdt: p3362 ?vr0 filter ( ?vr0 = -1100000000 ) }

Gene:
> ask where { wd: q1418 wdt: p3362 ?vr0 filter ( ?vr0 = -1 . 1 ) }
