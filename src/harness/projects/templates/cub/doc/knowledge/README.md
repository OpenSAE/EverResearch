# Scientific knowledge and terminology

## Purpose

Maintaining the scientific concepts and project usage needed to understand the classification indicators and the basis of the experiment.

## Scope

Read the results of the classification and maintain the interpretation of the indicator.

| Concept | Definitions and project usage | Sources and linkages |
| --- | --- | --- |
| Top-1 accuracy rate | The highest category is given for each sample, with the correct number divided by the number of samples to assess the number of samples. The reported values range from 0 to 1 and the application is determined by the input and classification of the current assessment. | [Categorization](../../tasks/classification/operation.py),[Experimental report](../experiment.md)(Use to compare results and limits based on real operations, check for random initialization and fine-tuning of respective conditions) |
| Division of official training and testing | The CUB-200-2011 official label specifies which collections each of the maps belongs to. | [Data Read](../../datasets/cub200/dataset.py),[Description of the data set](../datasets.md)(For data selection and disaggregation, see how offline synthetic input is generated) |
