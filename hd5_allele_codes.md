# why #

The data from Matt State's lab @ yale has ~533K sites. ~8K are tri(or more)-allelic. Although we will only discuss snps here, the method described here should naturally lend itself to CNVs (provided there are not more than 8 variant alleles).

# what #

Spse a line in our vcf file:

chr1   454545   A   C,T,G   0/0   0/2   1/2   1/3   3/3

VCF > HD5 codes:
```
./.    0
0/0    1
0/1    2
1/1    3
0/2    4
2/2    5
0/3    6
3/3    7
1/2    35
2/3    57
```
# how #

We now have to change...

How we count the number of mutation carriers:
  * This is the rowsum of the 0,1 coded boolean array which (calls > 1).
  * Try rowsum of the proper masked array.

How we distinguish htz from hmz:
  * All ref/obs htz are odd-valued.
  * All obs/obs htz are also odd-valued.
  * For a given code n > 1, mod(n+1,2) gives the array mask upon which to rowsum.