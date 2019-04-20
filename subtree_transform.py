from Graph import *


def transform_node(node):
    # The tree is transformed from a bottom up approach
    # Before evaluating a node all the children of it are transformed
    for child in node.children:
        transform_node(child)

    # Both let and where have similar structures so they are treated equally
    if node.name == 'let' or node.name == 'where':
        child_1, child_2 = get_node(node, '=')

        Lambda = Node('lambda')
        Lambda.add_child(child_1.children[0].copy_node())
        Lambda.add_child(child_2.copy_node())

        Gamma = Node('gamma')
        Gamma.add_child(Lambda)

        Gamma.add_child(child_1.children[1].copy_node())

        node.replace_node(Gamma)

    elif node.name == 'function_form':
        l = len(node.children)
        P = node.children[0]
        E = node.children[-1]
        V = []
        # Function can have more than one variable, therefore all the variables are added
        for i in range(1, l - 1):
            V.append(node.children[i])

        ini = Node('=')
        ini.add_child(P.copy_node())
        current_node = ini

        # Then for each variable a different node is created
        for i in V:
            Lambda = Node('lambda')
            current_node.add_child(Lambda)
            Lambda.add_child(i.copy_node())
            current_node = Lambda

        current_node.add_child(E.copy_node())
        node.replace_node(ini)

    elif node.name == 'lambda':
        length = len(node.children)
        if length > 2:
            ini = Node('lambda')
            current_node = ini
            for i in range(length - 2):
                child = node.children[i]
                current_node.add_child(child.copy_node())
                Lambda = Node('lambda')
                current_node.add_child(Lambda)
                current_node = Lambda

            current_node.add_child(node.children[-2].copy_node())
            current_node.add_child(node.children[-1].copy_node())

            node.replace_node(ini)

    elif node.name == 'within':
        ini = Node('=')
        ini.add_child(node.children[1].children[0].copy_node())

        Lambda = Node('lambda')
        Lambda.add_child(node.children[0].children[0].copy_node())
        Lambda.add_child(node.children[1].children[1].copy_node())

        Gamma = Node('gamma')
        Gamma.add_child(Lambda)
        Gamma.add_child(node.children[0].children[1].copy_node())

        ini.add_child(Gamma)
        node.replace_node(ini)

    elif node.name == 'and':
        ini = Node('=')
        col = Node(',')
        tau = Node('tau')

        ini.add_child(col)
        ini.add_child(tau)

        for child in node.children:
            col.add_child(child.children[0].copy_node())
            tau.add_child(child.children[1].copy_node())

        node.replace_node(ini)

    elif node.name == '@':
        Gamma = Node('gamma')
        Gamma.add_child(node.children[1].copy_node())
        Gamma.add_child(node.children[0].copy_node())

        ini = Node('gamma')
        ini.add_child(Gamma)
        ini.add_child(node.children[2].copy_node())

        node.replace_node(ini)

    elif node.name == 'rec':
        Lambda = node.children[0].copy_node()
        Lambda.name = 'lambda'
        Ystar = Node('Y*')

        Gamma = Node('gamma')
        Gamma.add_child(Ystar)
        Gamma.add_child(Lambda)

        ini = Node('=')
        ini.add_child(Lambda.children[0].copy_node())
        ini.add_child(Gamma)

        node.replace_node(ini)

    return


def get_node(node, name, match=False):
    nodes = []
    for child in node.children:
        if child.name == name and not match:
            nodes = [child] + nodes
        else:
            nodes.append(child)
    return nodes
