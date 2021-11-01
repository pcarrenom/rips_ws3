import json
from tree_parser import load_json_from_file, parse_tree
import pandas as pd
import numpy as np
from custom_tree_metrics import *
from apted import APTED
from anytree import RenderTree, ContStyle
import sys

gettrace = getattr(sys, 'gettrace', None)

def parse_behaviors(behavior_info, group):
    results = {}
    for item in behavior_info:
        if gettrace():
            print(item['file'])
        results[item["name"]] = parse_tree("data/input/ws3_data/{}/{}".format(group, item["file"]))

    return results

def compute_single_metrics(trees, apply_to_list, group, condition, behavior):
    all_data = []
    for v in apply_to_list:
        complexity = list(compute_tree_complexity(trees[v]).values()) + [trees[v].height]
        prim_count = list(compute_tree_primitives_count(trees[v]).values())
        all_data.append([group, behavior, v, condition] + complexity + prim_count)
    return all_data

def compute_paired_metrics(trees, apply_to_list, group, condition, behavior):
    all_data = []
    for v in apply_to_list:
        if gettrace():
            print(RenderTree(trees[v[0]], style=ContStyle()))
            print(RenderTree(trees[v[1]], style=ContStyle()))
        apted = APTED(trees[v[0]], trees[v[1]], CustomTEDConfig())
        ted = apted.compute_edit_distance()
        mapping = apted.compute_edit_mapping()
        edt = apted.mapping_cost(mapping)
        all_data.append([group, behavior, "{}-{}".format(*v), condition] + list(edt.values()))
    return all_data
    
def run_all_comparisons(analysis_config_file="", output_file_path=""):

    if not analysis_config_file:
        return

    config = load_json_from_file(analysis_config_file)

    # Set up general structure of dataframes used to store metrics
    arrays_single = [['general']*4 + ['complexity']*5 + ['primitive_count']*3,
                    ["group", "behavior", "iteration", "condition", "total_seq", "total_sel", "total_cond", "overall", "depth", "total_primitives", "social", "functional"]]
    arrays_pairs = [['general']*4 + ['edt']*4,
                    ["group", "behavior", "condition", "comparison", "total", "insert", "delete", "rename"]]
    
    tuples_single = list(zip(*arrays_single))
    tuples_pairs = list(zip(*arrays_pairs))

    df_single_data = []
    df_paired_data = []

    for item in config["analysis"]:
        group = item['group']
        for details in item["configurations"]:
            condition = details["condition"]
            for comparison in details['metrics']:
                behavior = comparison["behavior"]
                data = parse_behaviors(comparison['data'], group)
                for metric in comparison["compute"]:
                    if metric['type'] == "single":
                        df_single_data.extend(compute_single_metrics(data, metric['apply_to'], group, condition, behavior))
                        continue

                    if metric['type'] == 'paired':
                        df_paired_data.extend(compute_paired_metrics(data, metric['apply_to'], group, condition, behavior))

    final_df_single_metrics = pd.DataFrame(columns=pd.MultiIndex.from_tuples(tuples_single), data=df_single_data)
    final_df_pair_metrics = pd.DataFrame(columns=pd.MultiIndex.from_tuples(tuples_pairs), data=df_paired_data)
    
    if output_file_path:
        final_df_single_metrics.to_csv("{}/SingleMetrics.csv".format(output_file_path))
        final_df_single_metrics.to_pickle("{}/SingleMetrics.pk".format(output_file_path))
        final_df_pair_metrics.to_csv("{}/PairedMetrics.csv".format(output_file_path))
        final_df_pair_metrics.to_pickle("{}/PairedMetrics.pk".format(output_file_path))
    else:
        print(final_df_single_metrics)
        print(final_df_pair_metrics)


if __name__ == '__main__':

    run_all_comparisons("data/input/analysis_config.json", "data/output")