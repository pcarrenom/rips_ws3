from anytree import NodeMixin, PostOrderIter
from enum import Enum, auto

class NodeType(Enum):
    SEQUENCE = "sequence"
    SELECTOR = "selector"
    CONDITION = "condition"
    ACTION = "action"
    PRIMITIVE = "primitive"

    @classmethod
    def from_str(cls, label):
        if label in ("sequence", "sequ"):
            return NodeType.SEQUENCE
        elif label in ("condition", "cond"):
            return NodeType.CONDITION
        elif label in ("selector"):
            return NodeType.SELECTOR
        elif label in ("action", "acti"):
            return NodeType.ACTION
        elif label in ("primitive"):
            return NodeType.PRIMITIVE
        else:
            raise NotImplementedError

class BTBase(object):
    def __init__(self, id='0', node_type=NodeType.ACTION):
        self.id = id
        self.node_type = node_type

    def __str__(self):
        return '(' + str(self.id) + '/' + str(self.node_type) + ')'

    def __repr__(self):
        return 'BT Base Node (' + str(self.id) + ',' + str(self.node_type) + ')'

    def __eq__(self, other):
        return ((self.id, self.node_type) == (other.id, other.node_type))

    def __ne__(self, other):
        return not (self == other)

    def __has_child__(self, new_id):
        return len([node.id for node in PostOrderIter(self, stop=lambda n: n.id == new_id)]) > 0


class BTPrimitive(BTBase, NodeMixin):
    def __init__(self, id='0', primitive_name='say', node_type=NodeType.PRIMITIVE, parent=None, **kwargs):
        super(BTPrimitive, self).__init__(id, node_type)
        self.name = primitive_name
        self.input = kwargs['input']
        self.options = None if 'options' not in kwargs else kwargs['options']
        self.parent = parent
        self.children = []

    def __str__(self):
        return '(' + str(self.node_type) + ' ' + str(self.name) + ', with input ' + str(self.input) + ' and options ' + str(self.options) + ')'

    def __repr__(self):
        return 'BTPrimitive (' + str(self.name) + ' ' + str(self.id) + ', with input ' + str(self.input) + ' and options ' + str(self.options) + ')'

    def __eq__(self, other):
        return (super(BTPrimitive, self).__eq__(other) and self.input == other.input and self.name == other.name and self.options == other.options)

    def __ne__(self, other):
        return not (self == other)

    def as_dict(self):
        my_dict = {'primitive': self.name, 'input': self.input}
        if self.options:
            my_dict.update({'options': self.options})
        return my_dict


class BTLeaf(BTBase, NodeMixin):
    def __init__(self, id='0', node_type=NodeType.ACTION, parent=None, primitives=None):
        super(BTLeaf, self).__init__(id, node_type)       
        self.children = []
        if primitives:
            self.children = primitives
        
        self.parent = parent

    def add_primitive(self, primitive_id=None, primitive_name=None, **kwargs):
        if primitive_id is None:
            return
        prim = BTPrimitive(id=primitive_id, primitive_name=primitive_name, node_type=NodeType.PRIMITIVE, parent=self, **kwargs)
        if not self.__has_child__(primitive_id):
            self.children.append(prim)

    def get_primitives(self):
        if not self.children:
            return []
        
        primitives = []
        for prim in self.children:
            primitives.append(prim.as_dict())
        return primitives

    def __str__(self):
        return '(' + str(self.id) + ', ' + str(self.node_type) + ' with ' + str(len(self.children)) + ' primitives )'

    def __repr__(self):
        return 'BT Leaf (' + str(self.id) + ', ' + str(self.node_type) + ' with ' + str(len(self.children)) + ' primitives )'

    def __eq__(self, other):
        return (super(BTLeaf, self).__eq__(other) and self.children == other.children)

    def __ne__(self, other):
        return not (self == other)
    

class BTLogic(BTBase, NodeMixin):
    def __init__(self, id='0', node_type=NodeType.SEQUENCE, parent=None, children=None):
        super(BTLogic, self).__init__(id, node_type)
        self.parent = parent
        self.children = []
        
        if children:
            self.children = children

    def add_children(self, new_child=None):
        if new_child:
            if not self.__has_child__(new_child.id):
                self.children.append(new_child)

    def add_multiple_children(self, new_children=None):
        if new_children:
            for child in new_children:
                self.add_children(child)

    def __str__(self):
        return '(' + str(self.id) + ', ' + str(self.node_type) + ',  with ' + str(len(self.children)) + ' children)'

    def __repr__(self):
        return 'BT Logic (' + str(self.id) + ', ' + str(self.node_type) + ' with ' + str(len(self.children)) + ' children)'
    
    def __eq__(self, other):
        
        if not super(BTLogic, self).__eq__(other):
            return False

        if not super(BTLogic, self.parent).__eq__(other.parent):
            return False        
                
        if not len(self.children) == len(other.children):
            return False

        children_equal = True
        for c1, c2 in zip(self.children, other.children):
            children_equal &= c1 == c2
        
        return children_equal

    def __ne__(self, other):
        return not (self == other)