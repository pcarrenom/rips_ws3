from apted import Config
from nodes import BTLeaf, BTLogic, NodeType, BTPrimitive
from anytree import PreOrderIter
import numpy as np

'''
This method extends the basic edit tree distance computation of the apted package to RIZE-like trees.
The edit tree distance is defined as the minimal-cost sequence of node edit operations that transforms one tree into another. 
Three edit operations are considered in this implementation:
    - delete a node and connect its children to its parent maintaining the order.
    - insert a node between an existing node and a subsequence of consecutive children of this node.
    - rename the label of a node (changes to primitives-input pairs).  
'''

class CustomTEDConfig(Config):
    def rename(self, node1, node2):
        """Compares attribute primitive values of trees"""

        if type(node1) != type(node2) or (node1.id, node1.node_type) != (node2.id, node2.node_type):
            return 1

        if isinstance(node1, BTPrimitive) and isinstance(node2, BTPrimitive):
                return 1 if node1 != node2 else 0
        else:
            return 0

    def mapping_cost(self, mapping):
        """Calculates the cost of an edit mapping. It traverses the mapping and
        sums up the cost of each operation. The costs are taken from the cost
        model."""
        delete, insert = self.delete, self.insert
        rename = self.rename
        delete_cost = 0
        insert_cost = 0
        rename_cost = 0
        cost = 0
        for node1, node2 in mapping:
            if node1 is None: # insertion
                cost += insert(node2)
                insert_cost += insert(node2)
            elif node2 is None: # deletion
                cost += delete(node1)
                delete_cost += delete(node1)
            else:
                cost += rename(node1, node2)
                rename_cost += rename(node1, node2)
        return {'total_cost': cost, 'insert_cost': insert_cost, 'delete_cost': delete_cost, 'rename_cost': rename_cost}

def compute_tree_complexity(tree):
    """
    Computes complexity of behaviour tree. Current implementation iterates over all nodes and counts the total number of flow nodes 
    (i.e., sequences and selectors)
    """

    counts = {NodeType.SEQUENCE: 0, NodeType.SELECTOR: 0, NodeType.CONDITION: 0}

    for node in PreOrderIter(tree):
        if not node.is_root and node.node_type not in (NodeType.ACTION, NodeType.PRIMITIVE):
            counts[node.node_type] += 1
 
    ret_dict = {k.value: v for k, v in counts.items()}
    ret_dict["total"] = np.sum(list(counts.values()))            

    return ret_dict


def compute_tree_primitives_count(tree, social_primitives=None, functional_primitives=None):
    """
    Computes total number of social and functional primitives in a behaviour tree
    """
    if not social_primitives:
        social_primitives = ['human_detected', 'say', ['animation', 'wave'], ['animation', 'disco'], 'track_people_with',
                            ['walk_toward', 'People']]
    
    if not functional_primitives:
        functional_primitives = ['object_detected', ['animation', 'picknput'], ['animation', 'pick-and-place'], 'walk', 'turn', 'wait',
                                ['walk_toward', 'RedBall'], 'track_redball_with', 'close_hand']

    counts = {'total': 0, 'social': 0, 'functional': 0}

    for node in PreOrderIter(tree):
        if node.is_leaf and isinstance(node, BTPrimitive):
            counts['total'] += 1
            parameters = list(node.as_dict().values())
            if parameters[0] in social_primitives or parameters[:2] in social_primitives:
                counts['social'] +=1
            elif parameters[0] in functional_primitives or parameters[:2] in functional_primitives:
                counts['functional'] +=1
            else:
                raise RuntimeError('Primitive in leaf node {} is either social nor functional'.format(parameters))

            
    return counts          