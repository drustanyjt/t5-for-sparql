# Wrong examples

One of the most common reasons for wrong outputs was the object and subject being swapped like so:

Input:
> How many have the facet polytope rectangle ?

Gold:
> select ( count ( ?vr0 ) as ?vr1 ) { ?vr0 wdt: p1312 wd: q209 }

Generated:
> select ( count ( ?vr0 ) as ?vr1 ) { wd: q209 wdt: p1312 ?vr0 }

