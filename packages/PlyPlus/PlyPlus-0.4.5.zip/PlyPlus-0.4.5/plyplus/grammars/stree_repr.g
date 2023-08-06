start: node;

node: name LPAR node_or_token (',' node_or_token)* RPAR;

@node_or_token: node | token;

token: '\'[^\']*\'';

name: '[a-z_]+';

LPAR: '\(';
RPAR: '\)';

WS: '[\t \f]+' (%ignore);
