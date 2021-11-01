# computing causual realtions between labels
# requirement: cdt (https://fentechsolutions.github.io/CausalDiscoveryToolbox/html/index.html), rpy2
# Python 3.7.0 [MSC v.1914 64 bit (AMD64)] on win32

#import libraries
import networkx as nx
import cdt
import gc
from cdt.data import load_dataset
import pandas as pd
import random
from rpy2.robjects.packages import importr
from matplotlib import pyplot as plt
import rpy2.robjects as robjects
import math

# import algorithms
from cdt.causality.graph import GIES, MMPC, PC, CGNN

# indenpendence test 
from scipy import stats

cdt.SETTINGS.rpath = 'C:/Program Files/R/R-4.0.5/bin/x64/Rscript'
cdt.SETTINGS.verbose = True

# import required R packages
importr('pcalg')
importr('kpcalg')
importr('RCIT')
importr('bnlearn')

# annotations to be processed
anno_fs= ['Fetch_1','Fetch_2','Fetch_3','Fetch_4','Pepper_1','Pepper_2','Pepper_3','Pepper_4']
session = ['Simulator','Robot']
role = ['R','P']
event = ['demonstration','none']
percept = ['<robot limitation>','<social context>','<spatial context>','<user context>','<liability concern>',
           '<safety concern>','<ethical concern>','<resources - setup limitation>','<positive>','<indifferent>',
           '<anthropomorphize>','<unsuitable goal>','<interaction - engagement failure>','<performance failure>',
           '<inappropriate behavior>','<unexpected behavior>','<refer to simulation>']
action = ['<propose role>','<propose behavior>','<propose action>','<choose behavior>','<explain proposed behavior>',
          '<clarification reasoning>','<refer to experience>','<identify failure>','<propose replacement>',
          '<propose fixes>','<propose addition>','<propose removal>','<identify limitation>']


# timeout decorator
from threading import Thread
import functools

def timeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [Exception('function [%s] timeout [%s seconds] exceeded!' % (func.__name__, timeout))]
            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e
            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception as je:
                print ('error starting thread')
                raise je
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret
        return wrapper
    return deco


# define function to run GIES where input data is numerical
# Timeout after 10 minutes
@timeout(600)
def cause_effect(data, label, alg, algname, fname, cat):
    # segment data to 1 current label with all previous labels
    anno_data = pd.DataFrame(data[data[cat] == label])
    one_hot = pd.get_dummies(anno_data)

    figname = []
    logname = []
    if cat == 'CurLabel':
        figname = 'CausalGraphs/' + fname + '/' + algname + label[1:-1] + '.png'
        logname = 'CausalGraphs/' + fname + '/' + algname + label[1:-1] + '.txt'
    else:
        figname = 'CausalGraphs/' + fname + '/' + algname + label + '.png'
        logname = 'CausalGraphs/' + fname + '/' + algname + label + '.txt'
	
    # apply the causal discovery algorithm
    obj = alg()
    try:
        output = obj.predict(one_hot)
    except Exception as error:
        print(error)
        pass
	
    
    # remove nodes not connecting with others
    for i in list(output.degree):
        if i[1] == 0:
            output.remove_node(i[0])

    # To view the graph created
    plt.figure(figsize=(20, 10), dpi=100)
    g = nx.draw_networkx(output, with_labels=True, node_size=220, width=2, arrowsize=20, font_size=11)
    #print(nx.adjacency_matrix(output).todense())
    plt.savefig(figname)
    plt.close('all')
	
    l = []
    l = list(output.nodes())  # list of nodes in the graph
    e = []
    e = list(output.edges())  # list of edges in the graph
    
    # calculate the dependencies between each pair of causal relation
    dependency = []
    for i in list(e):
        node1 = one_hot[i[0]]
        node2 = one_hot[i[1]]
        crosstab = pd.crosstab(node1,node2)
        try:
            fisher = stats.fisher_exact(crosstab)[1]
        except Exception as error:
            print(error)
            fisher = 0
            pass
        dependency.append(fisher)
    
    causation = pd.DataFrame(e, columns=['Cause', 'Effect'])
    causation['dependency'] = dependency
    # sort dataframe based on dependencies and print to log file
    causation.sort_values(by=['dependency'], ascending=True)
    causation.to_csv(logname, encoding='utf-8', index=False) # save to file
    
    # free memory
    del g
    del obj
    del anno_data
    gc.collect()
    
    return causation

random.seed(123)


for anno_fd in anno_fs:
	input_f = 'ws3all_processed/' + anno_fd + '.csv'
	anno_f = pd.read_csv(input_f, usecols=['Session','Role','PreLabel','CurLabel','NxtLabel','PreEvent','CurEvent','NxtEvent'])

	# perform causal discovery for simulation / robot sessions
	for ses_label in session:
		print('=== GIES: Session label ' + ses_label + ' ===')
		try:
			cause_effect(anno_f, ses_label, GIES, 'GIES_', anno_fd, 'Session') # Greedy Interventional Equivalence Search
		except Exception as error:
			print(error)
			pass

		print('=== PC: Session label ' + ses_label + ' ===')
		try:
			cause_effect(anno_f, ses_label, PC, 'PC_', anno_fd, 'Session') # Peter - Clark
		except Exception as error:
			print(error)
			pass

	# perform causal discovery for participant / researcher roles
	for rol_label in role:
		print('=== GIES: Role label ' + rol_label + ' ===')
		try:
			cause_effect(anno_f, rol_label, GIES, 'GIES_', anno_fd, 'Role') # Greedy Interventional Equivalence Search
		except Exception as error:
			print(error)
			pass

		print('=== PC: Role label ' + rol_label + ' ===')
		try:
			cause_effect(anno_f, rol_label, PC, 'PC_', anno_fd, 'Role') # Peter - Clark
		except Exception as error:
			print(error)
			pass

	# perform causal discovery for demonstration events
	for eve_label in event:
		print('=== GIES: Event label ' + eve_label + ' ===')
		try:
			cause_effect(anno_f, eve_label, GIES, 'GIES_', anno_fd, 'CurEvent') # Greedy Interventional Equivalence Search
		except Exception as error:
			print(error)
			pass

		print('=== PC: Event label ' + eve_label + ' ===')
		try:
			cause_effect(anno_f, eve_label, PC, 'PC_', anno_fd, 'CurEvent') # Peter - Clark
		except Exception as error:
			print(error)
			pass

	# perform causal discovery for each perception label
	for per_label in percept:
		print('=== GIES: Perception label ' + per_label + ' ===')
		try:
			cause_effect(anno_f, per_label, GIES, 'GIES_', anno_fd, 'CurLabel') # Greedy Interventional Equivalence Search
		except Exception as error:
			print(error)
			pass

		print('=== PC: Perception label ' + per_label + ' ===')
		try:
			cause_effect(anno_f, per_label, PC, 'PC_', anno_fd, 'CurLabel') # Peter - Clark
		except Exception as error:
			print(error)
			pass

	# perform causal discovery for each action label
	for act_label in action:
		print('=== GIES: Action label ' + act_label + ' ===')
		try:
			cause_effect(anno_f, act_label, GIES, 'GIES_', anno_fd, 'CurLabel') # Greedy Interventional Equivalence Search
		except Exception as error:
			print(error)
			pass

		print('=== PC: Action label ' + act_label + ' ===')
		try:
			cause_effect(anno_f, act_label, PC, 'PC_', anno_fd, 'CurLabel') # Peter - Clark
		except Exception as error:
			print(error)
			pass

	print('Finished processing ',anno_fd)

