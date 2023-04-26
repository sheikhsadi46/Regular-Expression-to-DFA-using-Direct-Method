from prettytable import PrettyTable
#Syntax Tree
def parse_tree(pattern):
    temp = []
    count = 0

    def concat(temp):
        while len(temp) > 1:
            right = temp.pop()
            left = temp.pop()
            temp.append(Concat(left, right))

    while count < len(pattern):
        word = pattern[count]
        if word in '1234567890':
            temp.append(Symbol(word))
            if count + 1 < len(pattern) and pattern[count+1] == '*':
                temp.append(asterisk(temp.pop()))
                count += 1

            concat(temp)

        elif word == '(':
            paren = 1
            start = count + 1
            count += 1

            while count < len(pattern) and paren > 0:
                if pattern[count] == '(':
                    paren += 1
                elif pattern[count] == ')':
                    paren -= 1
                count += 1

            sub_pattern = pattern[start:count - 1]
            sub_tree = parse_tree(sub_pattern)
            temp.append(sub_tree)
            if count < len(pattern) and pattern[count] == '*':
                temp.append(asterisk(temp.pop()))
                count += 1

            concat(temp)

        elif word == '|' or word == '+':
            left_one = temp.pop()
            count += 1
            right_one = parse_tree(pattern[count:])
            temp.append(Or(left_one, right_one))
            concat(temp)
            break
        count += 1
    return temp[0]


def print_parse_tree(node, prefix="", is_left=True):
    tree_string = ""
    if node is not None:
        label_node = f"{node.__class__.__name__}"
        if isinstance(node, Symbol):
            label_node += f"({node.symbol})"
        tree_string += f"{prefix}{'|' if not is_left else ''}{label_node}\n"

        if isinstance(node, (Concat, Or)):
            tree_string += print_parse_tree(node.left, prefix=prefix + ("| " if is_left else "| "), is_left=True)
            tree_string += print_parse_tree(node.right, prefix=prefix + ("| " if is_left else "  "), is_left=False)
        elif isinstance(node, asterisk):
            tree_string += print_parse_tree(node.child, prefix=prefix + ("| " if is_left else "| "), is_left=True)

    return tree_string


global value_firstpos, value_lastpos
value_firstpos = {}
value_lastpos = {}


class Symbol:
    def __init__(self, symbol):
        self.symbol = symbol

    def __repr__(self):
        return f"Symbol('{self.symbol}')"

    def first_pos(self):
        value_firstpos[self] = self.symbol
        return {self.symbol}

    def last_pos(self):
        value_lastpos[self] = self.symbol
        return {self.symbol}

    def nullable(self):
        return False

    def follow_pos(self, pos, follow_pos_table):
        return follow_pos_table.get(pos, set())


class Or:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Or({self.left}, {self.right})"

    def first_pos(self):
        first_pos_left = self.left.first_pos()
        first_pos_right = self.right.first_pos()
        first_pos = first_pos_left | first_pos_right
        value_firstpos[self] = first_pos
        return first_pos

    def last_pos(self):
        last_pos_left = self.left.last_pos()
        last_pos_right = self.right.last_pos()
        last_pos = last_pos_left | last_pos_right
        value_lastpos[self] = last_pos
        return last_pos

    def nullable(self):
        return self.left.nullable() or self.right.nullable()

    def follow_pos(self, pos, follow_pos_table):
        return self.left.follow_pos(pos, follow_pos_table) | self.right.follow_pos(pos, follow_pos_table)


class Concat:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Concat({self.left}, {self.right})"

    def first_pos(self):
        if self.left.nullable():
            first_pos_left = self.left.first_pos()
            first_pos_right = self.right.first_pos()
            first_pos = first_pos_left | first_pos_right
            value_firstpos[self] = first_pos
            return first_pos
        else:
            firstpos_left = self.left.first_pos()
            value_firstpos[self] = firstpos_left
            return firstpos_left

    def last_pos(self):
        if self.right.nullable():
            last_pos_left = self.left.last_pos()
            last_pos_right = self.right.last_pos()
            last_pos = last_pos_right | last_pos_left
            value_lastpos[self] = last_pos
            return last_pos
        else:
            last_pos = self.right.last_pos()
            value_lastpos[self] = last_pos
            return last_pos

    def nullable(self):
        return self.left.nullable() and self.right.nullable()

    def follow_pos(self, pos, follow_pos_table):
        if pos in self.left.last_pos():
            return self.right.first_pos() | follow_pos_table.get(pos, set())
        else:
            return self.left.follow_pos(pos, follow_pos_table) | self.right.follow_pos(pos, follow_pos_table)


class asterisk:
    def __init__(self, child):
        self.child = child

    def __repr__(self):
        return f"Star({self.child})"

    def first_pos(self):
        value_firstpos[self] = self.child.first_pos()
        return self.child.first_pos()

    def last_pos(self):
        value_lastpos[self] = self.child.last_pos()
        return self.child.last_pos()

    def nullable(self):
        return True

    def follow_pos(self, pos, follow_pos_table):
        if pos in self.child.last_pos():
            return self.child.first_pos() | follow_pos_table.get(pos, set())
        else:
            return self.child.follow_pos(pos, follow_pos_table)


def follow_table(tree):
    follow_pos_table = {}

    def traverse(node):
        if isinstance(node, Symbol):
            return
        elif isinstance(node, Concat):
            for pos in node.left.last_pos():
                follow_pos_table.setdefault(pos, set()).update(node.right.first_pos())
            traverse(node.left)
            traverse(node.right)
        elif isinstance(node, Or):
            traverse(node.left)
            traverse(node.right)
        elif isinstance(node, asterisk):
            for pos in node.child.last_pos():
                follow_pos_table.setdefault(pos, set()).update(node.child.first_pos())
            traverse(node.child)

    traverse(tree)
    return follow_pos_table

# BUILT DFA
def get_state(current_state, input_char, follow_pos_table, dict1):
    next_state = set()
    for pos in current_state:
        if dict1[int(pos)] == input_char:
            next_state.update(follow_pos_table[pos])
    return next_state


def final_state(state, last_position):
    return last_position in state


def dfa_build(tree, follow_pos_table, dict1):
    first_state = tree.first_pos()
    last_position = max(follow_pos_table, key=int)
    d_states = [first_state]
    d_transitions = {}
    marked_states = set()

    while d_states:
        new_state = d_states.pop(0)
        marked_states.add(tuple(sorted(new_state)))

        for input_char in set(dict1.values()):
            next_state = get_state(new_state, input_char, follow_pos_table, dict1)

            if next_state and tuple(sorted(next_state)) not in marked_states:
                d_states.append(next_state)
                marked_states.add(tuple(sorted(next_state)))

            d_transitions[(tuple(sorted(new_state)), input_char)] = tuple(sorted(next_state))

    final_states = {state for state in marked_states if final_state(state, last_position)}

    return marked_states, final_states, d_transitions

# Print DSTATE Table using Prettytable 
def print_dfa_table(d_transitions, input_chars):
    new_table = PrettyTable()
    new_table.field_names = ["Current State"] + [f"({char})" for char in input_chars]
    transitions_in_state = {}
    for (current_state, input_char), next_state in d_transitions.items():
        if current_state not in transitions_in_state:
            transitions_in_state[current_state] = {}
        transitions_in_state[current_state][input_char] = next_state
    for current_state, transitions in transitions_in_state.items():
        row = [current_state] + [transitions.get(char, ()) for char in input_chars]
        new_table.add_row(row)

    print("DSTATES:")
    print(new_table)


input_string = input('INPUT RE: ')
expression = input_string + '#'
# expression='(a|b)* abb#'
print(expression)

dict1 = {}
input_chars = []
re_in_numeric = ''
count = 1
for i in expression:
    if i.isalpha() or i == '#':
        re_in_numeric += str(count)
        dict1[count] = i
        if i != '#':
            input_chars.append(i)
        count += 1
    else:
        re_in_numeric += i
print(re_in_numeric)
print(dict1)

result = parse_tree(re_in_numeric)
print(result)

tree_str = print_parse_tree(result)
print(tree_str)
regex_tree = result

print("FIRSTPOS")

first_pos = regex_tree.first_pos()
for i, j in value_firstpos.items():
    print(f'{i}: {j}')
print(f"firstpos of the entire expression: {first_pos}")

print('--------------')
print("LASTPOS")

last_pos = regex_tree.last_pos()
for i, j in value_lastpos.items():
    print(f'{i}: {j}')
print(f"lastpos of the entire expression: {last_pos}")

follow_pos_table = {str(i): set() for i in range(1, len(dict1) + 1)}

follow_pos_table.update(follow_table(regex_tree))
print('--------------')
print("FOLLOWPOS")
for i in range(1, len(follow_pos_table) + 1):
    print(f"Followpos of {i}: {follow_pos_table[str(i)]}")

marked_states, final_states, d_transitions = dfa_build(regex_tree, follow_pos_table, dict1)

input_chars = set(input_chars)
print_dfa_table(d_transitions, input_chars)
print("Final States:")
for state in final_states:
    print(state)

# print(d_transitions)
# print(list(final_states))
file = open("420lab1.txt", "r")
lst = ''
for line in file:
    lst += line
a = lst.split(' ')

new_lst = []

for j in a:

    if ';\n' in j:
        for k in j.split(';\n'):
            new_lst.append(k)
    else:
        new_lst.append(j)

new_lst2 = []
for j in new_lst:

    if '\t' in j:
        k = j.split('\t')
        for k in j.split('\t'):
            if k == '':
                continue
            else:
                new_lst2.append(k)
        new_lst2.append(k)
    else:
        new_lst2.append(j)

new_lst1 = []
for j in new_lst2:

    if ',' in j and len(j) > 1:
        new_lst1.append(j[0:-1])
    elif '\n' in j:
        for k in j.split('\n'):
            if k == '':
                continue
            else:
                new_lst1.append(k)
    else:
        new_lst1.append(j)


def check_string(string):
    count = 0
    for char in string:
        if 65 <= ord(char) <= 90 or 97 <= ord(char) <= 122:
            count += 1
    if count == len(string):
        return True
    else:
        return False


def check_float(number):
    try:
        float(number)
        return True
    except ValueError:
        return False


Keywords = ['auto', 'double', 'int', 'struct', 'break', 'else', 'long', 'switch', 'case', 'enum', 'register', 'typedef',
            'char', 'extern', 'return', 'union', 'const', 'float', 'short', 'unsigned', 'continue', 'for', 'signed',
            'void', 'default', 'goto', 'sizeof', 'volatile', 'do', 'if', 'static', 'while', 'printf']
Identifiers = []
Math = ['+', '-', '=', '/', '*']
Logical = ['>', '<']
Numerical = []
Others = []

Keywords_token = []
Identifiers_token = []
Math_token = []
Logical_token = []
Numerical_token = []
Others_token = []
for i in new_lst1:
    if i in Keywords:
        Keywords_token.append(i)

    elif i in Math and i not in Math_token:
        Math_token.append(i)
    elif i in Logical and i not in Logical_token:
        Logical_token.append(i)
    elif i.isnumeric() or check_float(i):
        Numerical_token.append(i)
    elif check_string(i) and i not in Identifiers_token:
        Identifiers_token.append(i)
    elif i not in Keywords_token and i not in Identifiers_token and i not in Math_token and i not in Logical_token and i not in Numerical_token and i not in Others_token:
        Others_token.append(i)

print('Identifiers_token',Identifiers_token)


def accepts_dfa(dstate, input_str, final_states):
    current_state = list(dstate.keys())[0][0]
    for symbol in input_str:
        try:
            current_state = dstate[(current_state, symbol)]
        except KeyError:
            return False
    return current_state in list(final_states)


for input_str in Identifiers_token:
    if accepts_dfa(d_transitions, input_str, final_states):
        print(f"The input string '{input_str}' is accepted by the DFA.")
    else:
        print(f"The input string '{input_str}' is rejected by the DFA.")

# (a|b)* abb

