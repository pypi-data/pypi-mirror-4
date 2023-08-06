import codecs
import re
import ply.lex as lex
from ply.lex import LexError


class EDSACLexer():
    
    
    # List of token names.
    tokens = (
        'COMMENT',
        'OPCODE',
        'ADDRESS',
        # 'POSTFIX',
        'SPACE',
    )
    
    
    def __init__(self):
        pass
    
    
    # Buid the lexer
    def build(self):
        re.DOTALL
        self.lexer = lex.lex(object=self)
    
    
    def input(self, data):
        self.lexer.input(data)
    
    
    # Compute column. 
    #     input is the input text string
    #     token is a token instance
    def find_column(self, input, token):
        last_cr = input.rfind('\n',0,token.lexpos)
        if last_cr < 0:
            last_cr = 0
        column = (token.lexpos - last_cr) + 1
        return column
    
    
    # A regular expression rule with some action code
    def t_COMMENT(self, t):
        r'//.*|\[[^\]]*\]'
        # or alternatively '\[(?:.|\s)*?\]|\[[^\]]*\]'
        # which refers to multiline OR multiline within //
        return t
    
    
    def t_OPCODE(self, t):
        r'A|S|H|V|N|T|U|C|R|L|E|G|I|O|F|X|Y|Z|\.|\&|\#|\!|\@|\*|P|Q|J'
        return t
    
    
    def t_ADDRESS(self, t):
        # r'[0-9]{1,4}'
        r'[0-9]{1,}'
        try:
            t.value = int(t.value)
        except ValueError:
            print("integer value too large",t.value)
            t.value = 0
        return t
    
    
    # def t_POSTFIX(self, t):
    #     r'[0-9]{1,4}S|[0-9]{1,4}L'
    #     return t
    
    
    def t_ignore_SPACE(self, t):
        r'\ '
    
    
    def t_ignore_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
    
    
    def t_error(self, t):
        print("Syntax Error (line %d): Illegal character '%s'" % (t.lexer.lineno, t.value[0]))
        # t.lexer.skip(1)
    
    


if __name__ == "__main__":
    edsaclexer = EDSACLexer()
    edsaclexer.build()
    f = codecs.open("Hello.txt")
    edsaclexer.input(f.read())
    valid = True
    try:
        for tok in iter(edsaclexer.lexer.token, None):
            pass
        #     if (repr(tok.type) == "'ADDRESS'" or repr(tok.type) == "'OPCODE'" or \
        #         repr(tok.type) == "'COMMENT'"): print repr(tok.type), repr(tok.value)
        #     else: pass
    except LexError:
        valid = False
    if valid: print("success")
    else:     print("failure")
    print(edsaclexer.error)

