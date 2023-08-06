from .plyplus import Grammar, Str
from . import grammars

from_repr_grammar = Grammar(grammars.open('stree_repr.g'))
def from_repr(s):
    r = from_repr_grammar.parse(s)
    for token in r.select('token'):
        token_str = token.tail[0]
        assert token_str[0] == token_str[-1] == "'"
        token.parent().tail[token.index_in_parent] = Str(token_str[1:-1])
    for node, name in r.select('=node > =name'):
        node.head = name.tail[0]
        node.remove_kid_by_id(id(name))
    return r.tail[0]

