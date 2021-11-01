# Scripts used to generate results presented in the SciRob submission entitled "A Participatory Design Methodology for Building Shared Understanding Between Users and Designers in HRI"

## Behavior Tree Implemented Metrics

Three metrics are implemented at the moment:
- Complexity: Count of decision flow nodes (i.e., selectors, sequences, and conditions) and tree depth
- Primitive types: Count of leaf nodes that belong to manually, pre-defined social and functional categories
- Edit Distance: Number of changes (add, delete, rename) needed to transforms one tree into another. Rename operations include any changes to the attributes of leaf nodes, i.e., social or functional primitives.

### Dependencies
- [Anytree](https://github.com/c0fec0de/anytree)
- [Python APTED algorithm for the Tree Edit Distance](https://github.com/JoaoFelipe/apted)
- Data science libraries: pandas, numpy, matplotlib, seaborn, pickle

### How to run code

1. Install required dependencies

```
pip install numpy  pandas matplotlib seaborn anytree apted
```

2. Generate metrics and save results to pickle file. Input data required to compute metrics is:
- data folder where behavior trees are stored in json format
- configuration file that specifies which metrics to compute for each behavior tree or pair of behavior trees (see analysis_config_revision.json for an example)

```
python src_bt_metrics/rips_ws3_analysis.py
```

 This script stores computed metrics in two binary files. One file for single metrics (complexity and primitive counts) and one file for paired metrics (edt)

3. Generate plots for each group. Plots are based on binary files generated in the previous step

```
python src_bt_metricsevolution_plots.py
```

## Sentiment analysis
Three sentiment classifiers are provided in [src_sentiment](/src_sentiment), namyely the VADER sentiment classifier using NLTK, the T5 sentiment classifier, and the LIWC sentiment classifier. For dependencies of each classifier see the scripts for details.

## Causal analysis
Two causal discovery algorithms are implemented using the Causal Discovery Toolbox in [src_causal](/src_causal), namely GIES and PC. For dependencies of each classifier see the scripts for details.

## Other
pdf file with list of codes used to annotate transcripts is also included in [codes](data/Unified%20Annotation%20Scheme.pdf)
