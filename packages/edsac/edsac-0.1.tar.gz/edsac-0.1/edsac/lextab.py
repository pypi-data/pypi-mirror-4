# lextab.py. This file automatically created by PLY (version 3.4). Don't edit!
_tabversion   = '3.4'
_lextokens    = {'COMMENT': 1, 'SPACE': 1, 'POSTFIX': 1, 'INSTRUCTION': 1, 'OPCODE': 1, 'ADDRESS': 1}
_lexreflags   = 0
_lexliterals  = ''
_lexstateinfo = {'INITIAL': 'inclusive'}
_lexstatere   = {'INITIAL': [('(?P<t_COMMENT>//.*|\\[[^\\]]*\\])|(?P<t_OPCODE>A|S|H|V|N|T|U|C|R|L|E|G|I|O|F|X|Y|Z|\\.|\\&|\\#|\\!|\\@|\\*)|(?P<t_ADDRESS>[0-9]{1,4})|(?P<t_POSTFIX>[0-9]{1,4}S|[0-9]{1,4}L)|(?P<t_ignore_SPACE>\\ )|(?P<t_ignore_newline>\\n+)|(?P<t_INSTRUCTION>A|S|H|V|N|T|U|C|R|L|E|G|I|O|F|X|Y|Z|\\.|\\&|\\#|\\!|\\@|\\*[0-9]{1,4}?[0-9]{1,4}S|[0-9]{1,4}L*)', [None, ('t_COMMENT', 'COMMENT'), ('t_OPCODE', 'OPCODE'), ('t_ADDRESS', 'ADDRESS'), ('t_POSTFIX', 'POSTFIX'), ('t_ignore_SPACE', 'ignore_SPACE'), ('t_ignore_newline', 'ignore_newline'), ('t_INSTRUCTION', 'INSTRUCTION')])]}
_lexstateignore = {'INITIAL': ''}
_lexstateerrorf = {'INITIAL': 't_error'}
