go-higgsml
==========

`go-higgsml` is a simple starting-kit for the HiggsML challenge, using the `ATLAS` OpenData dataset:
 http://opendata.cern.ch/education/ATLAS

## Installation

```sh
$ go get github.com/ATLAS-outreach/HiggsML2014/scripts/go-higgsml
```

## Example

Once you've downloaded the `atlas-higgs-challenge-2014-v2.csv` data file:

```sh
$ go-higgsml ./atlas-higgs-challenge-2014-v2.csv output.csv
::: read data file [./atlas-higgs-challenge-2014-v2.csv]
::: loop on dataset and compute the score
::: loop again to determine the AMS, using threshold=-22
::: only looking at Kaggle public data set ('b') ('t': training, 'v': private, 'u': unused)
::: one could make their own dataset (then the weight should be renormalized)
::: AMS with recomputed weight: 1.5445097433569694 (sig=461.2280962093439, bkg=89012.84498602658)
::: AMS with kaggle weight: 1.5445097433687833 (sig=461.22809620945833, bkg=89012.84498604067)
::: recomputed weight and Kaggle-weight should be identical if using a predefined Kaggle-subset
::: now building submission file a-la-Kaggle: [output.csv]...
::: sort on the score
::: build a map key=id, value=rank
::: now building submission file a-la-Kaggle: [output.csv]... [done]
::: timing: 16.523812632s
::: bye.
```
