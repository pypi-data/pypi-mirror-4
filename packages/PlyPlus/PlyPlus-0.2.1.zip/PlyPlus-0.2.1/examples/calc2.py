import sys, os
sys.path.append('..')

from pprint import pprint
from operator import itemgetter, add, sub, mul, div, neg

from plyplus import Grammar, STransformer

calc_grammar = Grammar("""
    start: expression;
    @expression: bin_op | un_op | parenthesis | number ;
    parenthesis: '\(' expression '\)';
    bin_op: expression ('\+'|'-'|'\*'|'/') expression;
    un_op: '-' expression;

    number: '[\d.]+';
    PLUS: '\+';
    MINUS: '-';
    MUL: '\*';
    DIV: '/';

    WS: '[ \t]+' (%ignore);

###
self.precedence = (
    ('left','PLUS','MINUS'),
    ('left','MUL','DIV'),
)
""")

class Calc(STransformer):
    unary_operator_mapping = {
            '-': neg,
        }

    bin_operator_mapping = {
            '+': add,
            '-': sub,
            '*': mul,
            '/': div,
        }

    start = itemgetter(1)   # start only has one member: expression
    parenthesis = itemgetter(2) # get the expression between the parenthesis

    def number(self, exp):
        return float(exp.tail[0])

    def un_op(self, exp):
        operator_symbol, arg = exp.tail

        operator = self.unary_operator_mapping[operator_symbol]
        return operator(arg)

    def bin_op(self, exp):
        arg1, operator_symbol, arg2 = exp.tail

        operator = self.bin_operator_mapping[operator_symbol]
        return operator(arg1, arg2)


def main():
    calc = Calc()
    while True:
        try:
            s = raw_input('> ')
        except EOFError:
            break
        if s == '':
            break
        tree = calc_grammar.parse(s)
        print calc.transform(tree)

def _test():
    s="4.5-2+3*(-1/-2)"
    tree = calc_grammar.parse(s)
    pprint(tree)
    res = Calc().transform(tree)
    print s,"=",res
    assert res == 4


#_test()
main()
