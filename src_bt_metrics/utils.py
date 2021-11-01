from anytree import RenderTree, ContStyle

def render_basic(root):
    for pre, _, node in RenderTree(root):
        treestr = u"%s%s" % (pre, node.id)
        children = "Node has {} children".format(len(node.children))
        primitives = "and has {} primitives".format(len(node.primitives) if hasattr(node, "primitives") else "no")
    print(treestr.ljust(8), node.node_type.name, children, primitives)