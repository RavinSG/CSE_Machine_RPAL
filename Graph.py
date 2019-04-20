class Node:
    def __init__(self, name, depth=0):
        self.name = name
        self.depth = depth
        self.parent = None
        self.children = []
        self.id = None

    def copy_node(self):
        new_node = Node(self.name, 0)
        new_node.children = self.children[::]
        for child in new_node.children:
            child.parent = new_node
        return new_node

    def replace_node(self, new):
        self.name = new.name
        self.children = new.children
        for child in new.children:
            child.parent = self

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def add_parent(self, parent):
        self.parent = parent


class Graph:
    def __init__(self, num):
        start_node = Node(num)
        self.start_node = start_node
        self.nodes = [start_node]

    def add_node(self, node):
        self.nodes.append(node)

    def get_node(self, num):
        for node in self.nodes:
            if node.name == num:
                return node