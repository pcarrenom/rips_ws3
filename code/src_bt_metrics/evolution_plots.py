import seaborn as sns 
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as tick


def plot_behavior_evolution_per_group(data, group="Pepper_1", save_path=""):

    fig = plt.figure(figsize=(10, 2))
    gs = fig.add_gridspec(1, 4, left=0.06, right=0.89, top=0.95, bottom=0.25, wspace=0.31, hspace=0.1)
    axs = [fig.add_subplot(gs[i, j]) for i in range(1) for j in range(4)]
   
    # Select data for specified group
    mask = data['general']['group'].apply(lambda x: group==x)
    pos = np.flatnonzero(mask)

    # Remove first level of column multi-index
    plot_data = data.loc[pos].T.reset_index(level=0, drop=True).T

    # Set metric columns to numerical type
    metrics = ["overall", "depth", "social", "functional"]
    metrics_labels = ["Complexity", "Tree depth", "N. Social primitives", "N. Funct. primitives"]
    metrics_lims = [(-0.5, 14), (-0.5, 13), (-0.5, 20), (-0.5, 20)]
    
    for ax, metric, label, lims in zip(axs, metrics, metrics_labels, metrics_lims):
        plot_data = plot_data.astype({metric: 'int32'})
        sns.pointplot(x="iteration", y=metric, hue="behavior", data=plot_data, palette="mako_r", markers=["o", "x", "^", "*"], linestyles=["-", "--", "-.", ":"],
                      ax=ax)
        ax.set_ylabel(label)
        ax.set_ylim(lims)
        ax.set_xlabel("")
        ax.tick_params(axis='x', labelsize=8, rotation=15)

    for i in range(3):
        axs[i].get_legend().remove()

    handles, labels = axs[-1].get_legend_handles_labels()
    axs[-1].get_legend().remove()
    plt.legend(handles=handles, loc='center', bbox_to_anchor=(1.2, 0.7),
               labels=labels, ncol=1, title="Group {}".format(group), fontsize=9)
    axs[2].set_xlabel('Iteration', position=(-0.10, 1e6), horizontalalignment='center', fontsize=12, fontweight='bold')
    
    if save_path:
        plt.savefig("{}/{}".format(save_path, group.replace("_","")), dpi=1000, facecolor='w', edgecolor='w', bbox_inches="tight")
    else:
        plt.show()


def plot_cost_evolution_per_group(data, group="Pepper_1", save_path=""):

    fig = plt.figure(figsize=(10, 2))
    gs = fig.add_gridspec(1, 4, left=0.06, right=0.89, top=0.95, bottom=0.25, wspace=0.31, hspace=0.1)
    axs = [fig.add_subplot(gs[i, j]) for i in range(1) for j in range(4)]
   
    # Select data for specified group
    mask = data['general']['group'].apply(lambda x: group==x)
    pos = np.flatnonzero(mask)

    # Remove first level of column multi-index
    plot_data = data.loc[pos].T.reset_index(level=0, drop=True).T

    # Set metric columns to numerical type
    metrics = ["total", "insert", "delete", "rename"]
    metrics_labels = ["Total cost", "Insertion cost", "Delete cost", "Rename cost"]
    metrics_lims = [(-1.0, 60), (-1.0, 32), (-1.0, 25), (-1.0, 20)]

        
    for ax, metric, label, lims in zip(axs, metrics, metrics_labels, metrics_lims):
        plot_data = plot_data.astype({metric: 'int32'})
        sns.pointplot(x="condition", y=metric, hue="behavior", data=plot_data, palette="mako_r", markers=["o", "x", "^", "*"], linestyles=["-", "--", "-.", ":"],
                      ax=ax, dodge=0.01)
        ax.set_ylabel(label)
        ax.set_ylim(lims)
        ax.set_xlabel("")
        ax.tick_params(axis='x', labelsize=8, rotation=15)
        new_labels = [l.get_text().split("-")[-1] for l in ax.get_xticklabels()]
        ax.set_xlim(0,ax.get_xticks()[-1]+0.25)
        ax.set_xticklabels(new_labels)
        
    for i in range(3):
        axs[i].get_legend().remove()

    handles, labels = axs[-1].get_legend_handles_labels()
    axs[-1].get_legend().remove()
    plt.legend(handles=handles, loc='center', bbox_to_anchor=(1.2, 0.7),
               labels=labels, ncol=1, title="Group {}".format(group), fontsize=9)
    axs[2].set_xlabel('Iteration', position=(-0.10, 1e6), horizontalalignment='center', fontsize=12, fontweight='bold')
    
    if save_path:
        plt.savefig("{}/{}".format(save_path, group.replace("_","")), dpi=1000, facecolor='w', edgecolor='w', bbox_inches="tight")
    else:
        plt.show()


if __name__ == '__main__':
    df = pd.read_pickle("data/output/SingleMetrics.pk")
    groups = np.unique(df['general']['group'])
    for gr in groups:
        plot_behavior_evolution_per_group(df, group=gr, save_path="data/figures/Tree_Single")

    df2 = pd.read_pickle("data/output/PairedMetrics.pk")
    
    groups = np.unique(df2['general']['group'])
    for gr in groups:
        plot_cost_evolution_per_group(df2, group=gr, save_path="data/figures/Tree_Paired")