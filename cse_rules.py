from collections import defaultdict
from Graph import *

bi_ops = ['+', '-', '*', '/']
uni_ops = ['not', 'neg']
boolean_exp = ['or', '&', 'gr', 'ge', 'ls', 'le', 'eq', 'ne']
built_in = ['Print', 'Stern', 'Order', 'Stem', 'Isstring', 'Istruthvalue', 'Isinteger', 'Istuple', 'Null']
stack = ['e_0']

envs = defaultdict(list)
var_val = defaultdict(dict)
env_tree = Graph(0)

h_env = 0
h_control = 0
control = None

show_stack_control = False


# Used to extract variable names from keywords
def get_variable(variable):
    vars = variable.split(':')
    vars = vars[-1].split('>')
    if 'STR' in variable:
        vars = vars[0][1:-1]
        return vars
    return vars[0]


# Variables are looked up from the corresponding environment
def lookup(rands, control_stack):
    global var_val
    return_vals = [None] * len(rands)
    for i in range(len(rands)):
        rand = rands[i]

        # If the variable is not a string the integer value can be returned
        if type(rand) != int and type(rand) != bool and '<' in rand:
            var = get_variable(rand)
            if 'INT' in rand:
                var = int(var)
                return_vals[i] = var
                break
            elif var in built_in:
                return_vals[i] = var
            else:

                # First the variable is looked in the current environment
                for j in range(len(control_stack) - 1, -1, -1):
                    node = control_stack[j]
                    node = node.split('_')
                    if node[0] == 'e':
                        if var in var_val[int(node[1])].keys():
                            return_vals[i] = var_val[int(node[1])][var]
                            break

                # If no value is found in the current environment, parent environments are checked for the variable
                if return_vals[i] is None:
                    start = 0
                    for j in range(len(control_stack) - 1, -1, -1):
                        node = control_stack[j]
                        node = node.split('_')
                        if node[0] == 'e':
                            start = int(node[1])
                            break

                    while start >= 0:
                        if var in var_val[start].keys():
                            return_vals[i] = var_val[start][var]
                            break
                        start = start - 1

                # Still if no value is found it's put back to the stack for later evaluation
                if return_vals[i] is None:
                    return_vals[i] = get_variable(rands[i])

        # If the variable is an integer or a boolean value the same value is put back
        else:
            return_vals[i] = rand
    return return_vals


# Reading the standardized tree control structures are created
def create_control_structures(node, env_no, prev=0):
    global h_env

    # Lambda's first child is the variable name for the next environment, it is skipped when evaluating lambda
    # n decides the starting point of the child list, for lambda it is set to 1 and 0 for other nodes except '->'
    n = 1

    # These nodes are added to the structure by their parents
    # Therefore no need of adding them back to the structure when the node is evaluated
    if node.name != 'lambda' and node.name != 'tau' and node.name != '->':
        envs[env_no].append(node.name)
        n = 0

    if node.name == 'tau':
        n = 0

    # For the node '->' since it's not standardized in the ST, Therefore, each node is evaluated separately
    # If the parent node is also a '->' node, the children also should be evaluated again
    if node.name == '->':
        n = 0
        if prev == 2:
            n = 2
        elif prev == 1:
            node.children = [node.children[1]]
            n = 0

    # Each child node in the current node is evaluated
    for child in node.children[n:]:
        if child.name == 'lambda':
            # If ',' node is present in the children of lambda this should be considered as a multi parameter function
            # and evaluate differently from a normal lambda
            if ',' not in [x.name for x in child.children]:
                h_env = h_env + 1
                name = get_variable(child.children[0].name)
                # Create lambda variable with the current environment and the variable corresponding to it
                envs[env_no].append(child.name + '_' + name + '_' + str(h_env))
                create_control_structures(child, h_env)
            else:
                # A new environment is created for every lambda node
                h_env = h_env + 1
                a = [x.name for x in child.children[0].children]
                var = []
                for i in a:
                    name = get_variable(i)
                    var.append(name)
                name = '_'.join(var)
                envs[env_no].append(child.name + '_' + name + '_' + str(h_env))
                create_control_structures(child, h_env)

        elif child.name == '->':
            # Placeholders are placed to nodes since the control stack number cannot be determined
            # until the rest of the nodes are evaluated
            envs[env_no].append('pl1')
            envs[env_no].append('pl2')
            envs[env_no].append('beta')
            create_control_structures(child.children[0], env_no)
            h_env = h_env + 1
            # After nodes are evaluated the placeholders are replaced
            envs[env_no][envs[env_no].index('pl1')] = 'delta_' + str(h_env)
            if child.children[1].name != '->':
                create_control_structures(child.children[1], h_env, prev=1)
            else:
                child_copy = child.children
                create_control_structures(child, h_env, prev=1)
                child.children = child_copy
            h_env = h_env + 1
            envs[env_no][envs[env_no].index('pl2')] = 'delta_' + str(h_env)
            create_control_structures(child, h_env, prev=2)
        elif child.name == 'tau':
            l = len(child.children)
            envs[env_no].append(child.name + '_' + str(l))
            create_control_structures(child, env_no)

        else:
            create_control_structures(child, env_no)

    return envs


def evaluate():
    global stack, var_val, h_control, envs, control
    if len(control) > 0:
        if show_stack_control:
            print('C - ', control)
            print('S - ', stack, '\n')

        node = control.pop()

        if node == 'gamma':
            eval_node = stack.pop(0)
            # If the eval_node is a list then it should be treated as a tuple selection
            if type(eval_node) != list:
                eval_node = eval_node.split('_')
            else:
                ind = int(stack.pop(0))
                val = eval_node[ind - 1]
                stack = [val] + stack

            # When a lambda node is encountered a new control & environment are created and added to the control stack
            if 'lambda' in eval_node:
                h_control = h_control + 1
                new_env = h_control
                new_num = int(eval_node[-1])
                variables = eval_node[1:-1]
                var_stack = stack.pop(0)
                if len(variables) == 1:
                    var_stack = [var_stack]
                for variable in variables:
                    # If lambda has more than one variable they all should be assigned a number
                    var = var_stack.pop(0)
                    if type(var) == int:
                        var = var
                    elif 'INT' in var:
                        var = int(get_variable(var))
                    elif 'lambda' in var or type(var) == list:
                        var = var
                    else:
                        var = get_variable(var)

                    var_val[new_env][variable] = var
                e_num = 'e_{}'.format(h_control)
                control = control + [e_num] + envs[new_num]
                stack = [e_num] + stack

                evaluate()

            elif 'eta' in eval_node:
                control = control + ['gamma'] * 2
                Eta = '_'.join(eval_node)
                eval_node[0] = 'lambda'
                Lambda = '_'.join(eval_node)
                stack = [Lambda, Eta] + stack
                evaluate()

            elif eval_node[0] == 'Y*':
                Lambda = stack.pop(0)
                Lambda = Lambda.split('_')
                Lambda[0] = 'eta'
                eta = '_'.join(Lambda)
                stack = [eta] + stack
                evaluate()

            # The built in RPAL functions are evaluated here
            elif eval_node[0] in built_in:
                node = eval_node[0]
                rand = stack.pop(0)
                if node == 'Stern':
                    try:
                        val = rand[1:]
                    except:
                        val = ''

                elif node == 'Order':
                    val = len(rand)

                elif node == 'Stem':
                    try:
                        val = rand[0]
                    except:
                        val = ''

                elif node == 'Isstring':
                    val = type(rand) == str

                elif node == 'Isinteger':
                    val = type(rand) == int

                elif node == 'Istruthvalue':
                    val = type(rand) == bool

                elif node == 'Istuple':
                    val = type(rand) == list

                elif node == 'Null':
                    val = len(rand) == 0

                else:
                    print(rand)
                    val = None

                stack = [val] + stack

        elif get_variable(node) == 'Conc':
            control.pop()
            control.pop()
            rand_1 = stack.pop(0)
            rand_2 = stack.pop(0)
            rand = str(rand_1) + str(rand_2)
            stack = [rand] + stack

        # Rule No.5 of CSE
        elif node.split('_')[0] == 'e':
            value = [stack.pop(0)]
            while True:
                e_node = stack.pop(0)
                if type(e_node) != str:
                    value.append(e_node)
                elif e_node.split('_')[0] == 'e' and e_node.split('_')[1] == node.split('_')[1]:
                    stack = value + stack
                    break
                else:
                    value.append(e_node)

        elif 'tau' in node:
            num_variables = int(node.strip('_')[-1])
            tup = []
            while num_variables > 0:
                var = stack.pop(0)
                tup.append(var)
                num_variables = num_variables - 1

            stack = [tup] + stack

        elif node == 'aug':

            rand_1 = stack.pop(0)
            rand_2 = stack.pop(0)

            if type(rand_1) == list and type(rand_2) == list:
                for i in rand_2:
                    rand_1.append(i)
            elif type(rand_1) == list:
                rand = rand_1 + [rand_2]
            elif type(rand_2) == list:
                rand = [rand_1] + rand_2
            else:
                rand = [rand_1, rand_2]

            try:
                for i in range(len(rand)):
                    rand.remove('<nil>')
            except:
                pass
            stack = [rand] + stack

        elif node == 'beta':
            eval_node = stack.pop(0)
            else_node = control.pop()
            then_node = control.pop()
            if eval_node:
                new_num = int(then_node.split('_')[1])
                control = control + envs[new_num]
                evaluate()
            else:
                new_num = int(else_node.split('_')[1])
                control = control + envs[new_num]
                evaluate()

        elif 'ID' in node:
            value = lookup([node], control)
            stack = value + stack

        # Boolean expressions are evaluated
        elif node in boolean_exp:
            rand_1 = stack.pop(0)
            rand_2 = stack.pop(0)
            rand_1, rand_2 = lookup([rand_1, rand_2], control)

            if node == 'or':
                value = rand_1 or rand_2
            elif node == '&':
                value = rand_1 and rand_2
            elif node == 'gr':
                value = rand_1 > rand_2
            elif node == 'ge':
                value = rand_1 >= rand_2
            elif node == 'ls':
                value = rand_1 < rand_2
            elif node == 'le':
                value = rand_1 <= rand_2
            elif node == 'eq':
                value = rand_1 == rand_2
            elif node == 'ne':
                value = rand_1 != rand_2
            else:
                value = 'not defined'

            stack = [value] + stack

        elif node in uni_ops:
            rand_1 = stack.pop(0)
            rand_1 = lookup([rand_1], control)[0]
            if node == 'neg':
                val = -1 * rand_1
            else:
                val = not rand_1

            stack = [val] + stack

        elif node in bi_ops:
            rand_1 = stack.pop(0)
            rand_2 = stack.pop(0)
            rand_1, rand_2 = lookup([rand_1, rand_2], control)

            if node == '+':
                stack = [rand_1 + rand_2] + stack

            elif node == '-':
                stack = [rand_1 - rand_2] + stack

            elif node == '*':
                stack = [rand_1 * rand_2] + stack

            elif node == '/':
                stack = [rand_1 / rand_2] + stack

        elif 'INT' in node:
            node = int(get_variable(node))
            stack = [node] + stack

        elif '<STR:' in node:
            node = str(get_variable(node))
            stack = [node] + stack

        else:
            stack = [node] + stack

        evaluate()

    return stack, var_val
