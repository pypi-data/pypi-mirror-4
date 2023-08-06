from EDSACLexer import EDSACLexer
import ply.yacc as yacc


class EDSACGrammar:
    
    
    def __init__(self):
        self.lexer = EDSACLexer()
        self.lexer.build()
        
        self.tokens = self.lexer.tokens
        
        self.parser = yacc(module=self, start="Primes.txt")
        
    
    
    def p_expression(self, p):
        """
        expression : opcode address postfix
                   | opcode postfix
        """
        p[0] = p[1]
    
    
    def p_opcode(self, p, ):
        """
        opcode : A
               | S
               | H
               | V
               | N
               | T
               | U
               | C
               | R
               | L
               | E
               | G
               | I
               | O
               | F
               | X
               | Y
               | Z
               | P
               | Q
               | J
        """
        p[0] = p[1]
    
    
    def p_address(self, p):
        """
        address : INT
        """
        p[0] = [p1]
    
    
    def p_postfix(self, p):
        """
        postfix : S
                | L
        """
        p[0] = p[1]
    
    
    def p_error(self, p):
        raise ParseError("Syntax error")
    
    

