# Regular-Expression-to-DFA-using-Direct-Method

## Input:
```bash
(a|b)* abb
 ```
## Output:
```bash
(a|b)* abb#
(1|2)* 3456
{1: 'a', 2: 'b', 3: 'a', 4: 'b', 5: 'b', 6: '#'}
Concat(Concat(Concat(Concat(Star(Or(Symbol('1'), Symbol('2'))), Symbol('3')), Symbol('4')), Symbol('5')), Symbol('6'))
Concat
| Concat
| | Concat
| | | Concat
| | | | asterisk
| | | | | Or
| | | | | | Symbol(1)
| | | | | | |Symbol(2)
| | | | |Symbol(3)
| | | |Symbol(4)
| | |Symbol(5)
| |Symbol(6)

FIRSTPOS
Symbol('1'): 1
Symbol('2'): 2
Or(Symbol('1'), Symbol('2')): {'2', '1'}
Star(Or(Symbol('1'), Symbol('2'))): {'2', '1'}
Symbol('3'): 3
Concat(Star(Or(Symbol('1'), Symbol('2'))), Symbol('3')): {'2', '1', '3'}
Concat(Concat(Star(Or(Symbol('1'), Symbol('2'))), Symbol('3')), Symbol('4')): {'2', '1', '3'}
Concat(Concat(Concat(Star(Or(Symbol('1'), Symbol('2'))), Symbol('3')), Symbol('4')), Symbol('5')): {'2', '1', '3'}
Concat(Concat(Concat(Concat(Star(Or(Symbol('1'), Symbol('2'))), Symbol('3')), Symbol('4')), Symbol('5')), Symbol('6')): {'2', '1', '3'}
firstpos of the entire expression: {'2', '1', '3'}
--------------
LASTPOS
Symbol('6'): 6
Concat(Concat(Concat(Concat(Star(Or(Symbol('1'), Symbol('2'))), Symbol('3')), Symbol('4')), Symbol('5')), Symbol('6')): {'6'}
lastpos of the entire expression: {'6'}
--------------
FOLLOWPOS
Followpos of 1: {'2', '1', '3'}
Followpos of 2: {'2', '1', '3'}
Followpos of 3: {'4'}
Followpos of 4: {'5'}
Followpos of 5: {'6'}
Followpos of 6: set()
DSTATES:
+----------------------+----------------------+----------------------+
|    Current State     |         (a)          |         (b)          |
+----------------------+----------------------+----------------------+
|   ('1', '2', '3')    | ('1', '2', '3', '4') |   ('1', '2', '3')    |
| ('1', '2', '3', '4') | ('1', '2', '3', '4') | ('1', '2', '3', '5') |
| ('1', '2', '3', '5') | ('1', '2', '3', '4') | ('1', '2', '3', '6') |
| ('1', '2', '3', '6') | ('1', '2', '3', '4') |   ('1', '2', '3')    |
+----------------------+----------------------+----------------------+
Final States:
('1', '2', '3', '6')
Identifiers_token ['a', 'b', 'c', 'd', 'e', 'abb', 'babb', 'bbbbbabb']
The input string 'a' is rejected by the DFA.
The input string 'b' is rejected by the DFA.
The input string 'c' is rejected by the DFA.
The input string 'd' is rejected by the DFA.
The input string 'e' is rejected by the DFA.
The input string 'abb' is accepted by the DFA.
The input string 'babb' is accepted by the DFA.
The input string 'bbbbbabb' is accepted by the DFA.
```
