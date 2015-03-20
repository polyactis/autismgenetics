1) web interface: add a query summary
2) boolean operator (in the future, plots)
3) use these commonly described variables

4) select the individuals first, and then, in a second query step,  decide who else besides the individuals will be included. The comparison step will list a series of options:
a) none (will return the individual data only 2) sibling, parents etc, or even some custom-made set

6) add a form for query by variants (chromosome, start, end, gene, and then will have to add variant type. this will be only in the first variant selection step

5) backup??

2) in terms of variants we need to build a variant database using hdf5 and find a way to deal with 1) 3-position variants, indel etc).

one way to deal with deletions and insertions is to store them as single events, and then treat them separately (expand etc) by code before running the overlap query etc.

one possibility to run the 3-way SNPs is to have more codes than 0-1-2.

3) after filtering patients, create a subtable with the variants and run basic summary statistics

4) gene or position based variants.