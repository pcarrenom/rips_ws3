import json
from nodes import BTLeaf, BTLogic, NodeType
import numpy as np

def load_json_from_file(file_path):
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    return data

def parse_tree(file_path):

    json_data = load_json_from_file(file_path)
    counters = {'condition': 0, 'action': 0, 'selector': 0, 'sequence': 0, 'reaction': 0, 'primitive':0}

    def get_id(entry_type):
        current_value = counters[entry_type]
        counters[entry_type] += 1
        return current_value

    def parse_leaf_condition(parent_node, json_entry):
        new_node = BTLeaf(id="cond{}".format(get_id("condition")), node_type=NodeType.CONDITION, parent=parent_node)
        new_node.add_primitive(primitive_id="prim{}".format(get_id("primitive")), 
                               primitive_name=json_entry['primitive'], input=json_entry['input'])
        return new_node

    def parse_leaf_action(parent_node, json_entry):
        new_node = BTLeaf(id="act{}".format(get_id("action")), node_type=NodeType.ACTION, parent=parent_node)
        primitives = [json_entry['primitives']] if isinstance(json_entry['primitives'], dict) else json_entry['primitives']
        for prim in primitives:
            if bool(prim):
                new_node.add_primitive(primitive_id="prim{}".format(get_id("primitive")),
                                       primitive_name=prim['primitive'], input=prim['input'], options=prim["options"])
        return new_node

    def parse_children_node(parent_node, json_children):
        if not json_children:
            return
        children = []
        for node_child in json_children:
            if not node_child:
                continue
            if node_child["node"] == "condition":
                new_node = parse_leaf_condition(parent_node, node_child)
            elif node_child["node"] == "action":
                new_node = parse_leaf_action(parent_node, node_child)
            else:
                new_node = parse_flow_node(parent_node, node_child)
            children.append(new_node)

        return children

    def parse_flow_node(parent_node, json_entry):
        keyword = "sel" if json_entry["node"] == "selector" else "seq"
        new_node = BTLogic(id="{}{}".format(keyword, get_id(json_entry["node"])), node_type=NodeType.from_str(json_entry["node"]),
                    parent=parent_node)
        children = parse_children_node(new_node, json_entry["children"])
        new_node.add_multiple_children(children)
        return new_node

    # Parse trigger sequence node
    root = BTLogic(id="react{}".format(get_id("reaction")), node_type=NodeType.SEQUENCE)

    if json_data['activate']:
        if 'children' in json_data['activate']:
            new_child = parse_flow_node(root, json_data["activate"])
        else:
            new_child = parse_leaf_condition(root, json_data["activate"])
        root.add_children(new_child)
        
    if json_data["bt"]:
        new_child = parse_flow_node(root, json_data["bt"])
        root.add_children(new_child)
    
    return root





