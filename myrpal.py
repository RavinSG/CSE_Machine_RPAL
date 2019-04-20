from Graph import *
import cse_rules as cse
import subtree_transform as st
import time
import sys

try:
    import matplotlib.pyplot as plt
    import networkx as nx

    drawable = True
except:
    drawable = False

sys.setrecursionlimit(20000)

t = time.time()


def generateSTree(node_num, node):
    global tree
    child = tree[node_num]
    c_depth = child[1]

    if node.depth < c_depth:
        c_node = Node(child[0], child[1])
        c_node.add_parent(node)
        node.add_child(c_node)
        if node_num == len(tree) - 1:
            return
        else:
            generateSTree(node_num + 1, c_node)
    else:
        generateSTree(node_num, node.parent)


def drawTree(node, G, counter):
    node_name = str(node.name) + '_' + str(counter)
    node.id = counter
    G.add_node(node_name)
    try:
        parent_name = str(node.parent.name) + '_' + str(node.parent.id)
    except:
        parent_name = 'parent'
    G.add_edge(node_name, parent_name)
    for child in node.children:
        counter += 1
        drawTree(child, G, counter)


# The file is read line by line and nodes are created according to the depth
def generate_tree_from_file(filename):
    file = filename
    file = open(file, 'r+', newline='')
    tree = []

    for line in file:
        line = line.strip()
        # Removing extra empty lines at the end of the file
        if line != '':
            depth = line.count('.')
            tree.append([line.strip('.'), depth])

    return Node(tree[0][0], tree[0][1]), tree


def draw_AST(start_node):
    if drawable:
        G = nx.Graph()
        drawTree(start_node, G, 0)
        nx.shell_layout(G)
        nx.draw(G, with_labels=True, font_size=10)

        plt.show()
    else:
        print('matplotlib and networkx Modules are needed to draw tree')


def draw_ST(start_node, show_st=False, show_control=False, show_stack=False):
    # First node of the tree is used to star traversing the tree
    # Then each node is transformed using the standardization
    st.transform_node(start_node)

    if show_st:
        if drawable:
            G = nx.Graph()
            drawTree(start_node, G, 0)
            nx.shell_layout(G)

            nx.draw(G, with_labels=True, font_size=10)

            plt.show()
        else:
            print('matplotlib and networkx Modules are needed to draw tree')

    # After the ST is created it is fed to the cse to create control structures
    a = cse.create_control_structures(start_node, 0)
    control = a[0][::]
    cse.control = ['e_0'] + control

    if show_control:
        for j, k in a.items():
            print(j, k)

    b, c = cse.evaluate()

    if show_stack:
        print(b)
        print(c)


def check_parent(node):
    for child in node.children:
        if node != child.parent:
            print(node.name, child.name)
        check_parent(child)


tree = None
start_node = None


def run_program(filename, sh_stack, sh_control, sh_st):
    global start_node, tree
    start_node, tree = generate_tree_from_file(filename)
    generateSTree(1, start_node)
    draw_ST(start_node, show_stack=sh_stack, show_control=sh_control, show_st=sh_st)

    # print(time.time() - t)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        file = '-h'
    else:
        file = sys.argv[1]
    other = sys.argv[2:]
    show_stack, show_control, show_st = False, False, False
    if '-stk' in other:
        show_stack = True
    if '-cnt' in other:
        show_control = True
    if '-st' in other:
        show_st = True
    if '-runtime' in other:
        cse.show_stack_control = True

    if file == '-h':
        print('usage: myrpal.py [filename] [options]\n'
              'Options and arguments\n'
              '-stk\t : show stack and environments at end of execution\n'
              '-cnt\t : show control structures of the program\n'
              '-st\t : draw standardized tree of the program\n'
              '-runtime : show stack and control during run time\n'
              '-h\t : help')
    else:
        try:
            run_program(file, show_stack, show_control, show_st)
        except FileNotFoundError:
            print('Please enter a valid file name')
        except RecursionError:
            print('Maximum recursion depth occurred, please enter a smaller values')
