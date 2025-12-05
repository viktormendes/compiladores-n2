from typing import List, Optional, Tuple
from ast_nodes import (
    Token,
    Program,
    FunctionDecl,
    VarDecl,
    Assign,
    If,
    While,
    For,
    Return,
    Block,
    BinOp,
    Call,
    Index,
    Var,
    Num,
    Char,
    Str,
    SyntaxErrorInfo,
)

class Parser:

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.errors: List[SyntaxErrorInfo] = []
        self.had_error = False

    
    def current(self) -> Token:
        if self.pos >= len(self.tokens):
            return Token("EOF", "", 0, 0)
        return self.tokens[self.pos]

    def advance(self) -> Token:
        tok = self.current()
        if self.pos < len(self.tokens):
            self.pos += 1
        return tok

    def match(self, *types: str) -> bool:
        return self.current().type in types

    def expect(self, ttype: str) -> Optional[Token]:
        if self.match(ttype):
            return self.advance()
        cur = self.current()
        self._error(f"Esperado {ttype} mas encontrado '{cur.lex or cur.type}'", cur.line, cur.col)
        return None

    def _error(self, message: str, line: int, col: int):
        if not self.had_error:
            self.errors.append(SyntaxErrorInfo(message, line, col))
            self.had_error = True





    def parse_program(self) -> Tuple[Optional[Program], List[SyntaxErrorInfo]]:
        decls: List = []
        while not self.match("EOF"):
            if self.had_error:
                break  # para no primeiro erro

            if self.match("INT", "FLOAT", "CHAR_TYPE", "VOID"):
                node = self.parse_function_or_vardecl()
                if self.had_error:
                    break
                if node:
                    decls.append(node)
                else:
                    
                    if not self.match("EOF"):
                        self.advance()
            elif self.match("EOL"):
                self.advance()
            else:
                
                stmt = self.parse_statement()
                if self.had_error:
                    break
                if stmt:
                    decls.append(stmt)
                else:
                    cur = self.current()
                    self._error(f"Unexpected token '{cur.lex or cur.type}'", cur.line, cur.col)
                    break

        if self.had_error:
            return None, self.errors
        return Program(decls), self.errors

    
    
    def parse_function_or_vardecl(self):
        typ_tok = self.advance()  # type token
        if self.had_error:
            return None

        if not self.match("ID"):
            self._error("Esperado identificador apos tipo", typ_tok.line, typ_tok.col)
            return None
        name_tok = self.advance()

        if self.match("LPAREN"):
            self.advance()  # consume '('
            params: List[tuple] = []
            if not self.match("RPAREN"):
                while True:
                    if self.had_error:
                        return None
                    if self.match("INT", "FLOAT", "CHAR_TYPE", "ID"):
                        t = self.advance()
                        if self.match("ID"):
                            pname = self.advance()
                            ptype = t.lex if t.type in ("INT", "FLOAT", "CHAR_TYPE") else "int"
                            params.append((ptype, pname.lex))
                        else:
                            params.append(("int", t.lex))
                    if self.match("COMMA"):
                        self.advance()
                        continue
                    break
            if not self.expect("RPAREN"):
                return None
            body = self.parse_block()
            if self.had_error:
                return None
            return FunctionDecl(typ_tok.lex, name_tok.lex, params, body)

        init = None
        if self.match("EQUAL"):
            self.advance()
            init = self.parse_expression()
            if init is None:
                        cur = self.current()
                        self._error("Esperado expressao apos '='", cur.line, cur.col)
            return None
        if not self.expect("SEMI"):
            return None
        return VarDecl(typ_tok.lex, name_tok.lex, init)

    
    # Block
    
    def parse_block(self) -> Optional[Block]:
        if self.match("LBRACE"):
            self.advance()
            stmts: List = []
            while not self.match("RBRACE", "EOF"):
                if self.had_error:
                    return None
                if self.match("EOL"):
                    self.advance()
                    continue
                stmt = self.parse_statement()
                if self.had_error:
                    return None
                if stmt:
                    stmts.append(stmt)
                else:
                    cur = self.current()
                    self._error(f"Token inesperado no bloco: '{cur.lex or cur.type}'", cur.line, cur.col)
                    return None
            if not self.expect("RBRACE"):
                return None
            return Block(stmts)
        else:
            stmt = self.parse_statement()
            if self.had_error:
                return None
            if stmt:
                return Block([stmt])
            cur = self.current()
            self._error(f"Esperado bloco ou instrucao mas encontrado '{cur.lex or cur.type}'", cur.line, cur.col)
            return None

    
    
    def parse_statement(self):
        if self.match("INT", "FLOAT", "CHAR_TYPE", "VOID"):
            return self.parse_vardecl_statement()

        if self.match("IF"):
            return self.parse_if()
        if self.match("WHILE"):
            return self.parse_while()
        if self.match("FOR"):
            return self.parse_for()
        if self.match("RETURN"):
            self.advance()
            if self.match("SEMI"):
                self.advance()
                return Return(None)
            v = self.parse_expression()
            if v is None:
                cur = self.current()
                self._error("Esperado expressao apos 'return'", cur.line, cur.col)
                return None
            if not self.expect("SEMI"):
                return None
            return Return(v)

        if self.match("ID"):
            cur_pos = self.pos
            id_tok = self.advance()
            if self.match("EQUAL"):
                self.advance()
                val = self.parse_expression()
                if val is None:
                    cur = self.current()
                    self._error("Expected expression after '='", cur.line, cur.col)
                    return None
                if not self.expect("SEMI"):
                    return None
                return Assign(Var(id_tok.lex), val)
            self.pos = cur_pos

        expr = self.parse_expression()
        if expr:
            if not self.expect("SEMI"):
                return None
            return expr

        cur = self.current()
        self._error(f"Unexpected token in statement: '{cur.lex or cur.type}'", cur.line, cur.col)
        return None

    
    
    def parse_vardecl_statement(self) -> Optional[VarDecl]:
        type_tok = self.advance()
        if self.had_error:
            return None
        if not self.match("ID"):
            cur = self.current()
            self._error("Expected identifier after type", cur.line, cur.col)
            return None
        name_tok = self.advance()

        init = None
        if self.match("EQUAL"):
            self.advance()
            init = self.parse_expression()
            if init is None:
                cur = self.current()
                self._error("Expected expression after '='", cur.line, cur.col)
                return None

        if not self.expect("SEMI"):
            return None

        return VarDecl(type_tok.lex, name_tok.lex, init)

    
    
    def parse_if(self):
        self.advance() 
        if not self.expect("LPAREN"):
            return None
        cond = self.parse_expression()
        if cond is None:
            cur = self.current()
            self._error("Expected expression in 'if' condition", cur.line, cur.col)
            return None
        if not self.expect("RPAREN"):
            return None
        then_block = self.parse_block()
        if then_block is None and self.had_error:
            return None
        otherwise = None
        if self.match("ELSE"):
            self.advance()
            if self.match("LBRACE"):
                otherwise = self.parse_block()
                if otherwise is None and self.had_error:
                    return None
            else:
                stmt = self.parse_statement()
                if self.had_error:
                    return None
                if stmt:
                    otherwise = Block([stmt])
                else:
                    cur = self.current()
                    self._error("Expected statement after 'else'", cur.line, cur.col)
                    return None
        return If(cond, then_block, otherwise)

    def parse_while(self):
        self.advance()
        if not self.expect("LPAREN"):
            return None
        cond = self.parse_expression()
        if cond is None:
            cur = self.current()
            self._error("Expected expression in 'while' condition", cur.line, cur.col)
            return None
        if not self.expect("RPAREN"):
            return None
        body = self.parse_block()
        if body is None and self.had_error:
            return None
        return While(cond, body)

    def parse_for(self):
        self.advance()
        if not self.expect("LPAREN"):
            return None

        init = None
        if not self.match("SEMI"):
            if self.match("INT", "FLOAT", "CHAR_TYPE", "VOID"):
                init = self.parse_vardecl_statement()
            elif self.match("ID"):
                id_tok = self.advance()
                if not self.expect("EQUAL"):
                    return None
                val = self.parse_expression()
                if val is None:
                    cur = self.current()
                    self._error("Esperado expressao na atribuicao do for-init", cur.line, cur.col)
                    return None
                init = Assign(Var(id_tok.lex), val)
                if not self.expect("SEMI"):
                    return None
            else:
                init = self.parse_expression()
                if init is None:
                    cur = self.current()
                    self._error("Esperado expressao ou atribuicao em for-init", cur.line, cur.col)
                    return None
                if not self.expect("SEMI"):
                    return None
        else:
            if not self.expect("SEMI"):
                return None

        cond = None
        if not self.match("SEMI"):
            cond = self.parse_expression()
            if cond is None:
                cur = self.current()
                self._error("Esperado expressao na condicao do for", cur.line, cur.col)
                return None
        if not self.expect("SEMI"):
            return None

        step = None
        if not self.match("RPAREN"):
            step = self.parse_expression()
            if step is None:
                cur = self.current()
                self._error("Esperado expressao no passo do for", cur.line, cur.col)
                return None
        if not self.expect("RPAREN"):
            return None

        body = self.parse_block()
        if body is None and self.had_error:
            return None
        return For(init, cond, step, body)

    
    
    def parse_expression(self):
        return self.parse_assignment()
    
    def parse_assignment(self):
        """
        assignment → ID '=' assignment | or
        This allows things like: i = i + 1 inside for-step
        """
        left = self.parse_or()
        if left is None:
            return None

        if self.match("EQUAL"):
            op_tok = self.advance()
            right = self.parse_assignment()
            if right is None:
                cur = self.current()
                self._error("Esperado expressao apos '='", cur.line, cur.col)
                return None

            if not isinstance(left, Var):
                cur = self.current()
                self._error("Left side of assignment must be a variable", cur.line, cur.col)
                return None

            return Assign(left, right)

        return left

    def parse_or(self):
        left = self.parse_and()
        if left is None:
            return None
        while self.match("OR"):
            op = self.advance().lex
            right = self.parse_and()
            if right is None:
                cur = self.current()
                self._error("Esperado expressao apos operador", cur.line, cur.col)
                return None
            left = BinOp(op, left, right)
        return left

    def parse_and(self):
        left = self.parse_equality()
        if left is None:
            return None
        while self.match("AND"):
            op = self.advance().lex
            right = self.parse_equality()
            if right is None:
                cur = self.current()
                self._error("Esperado expressao apos operador", cur.line, cur.col)
                return None
            left = BinOp(op, left, right)
        return left

    def parse_equality(self):
        left = self.parse_relational()
        if left is None:
            return None
        while self.match("EQ", "NE"):
            op = self.advance().lex
            right = self.parse_relational()
            if right is None:
                cur = self.current()
                self._error("Esperado expressao apos operador", cur.line, cur.col)
                return None
            left = BinOp(op, left, right)
        return left

    def parse_relational(self):
        left = self.parse_add()
        if left is None:
            return None
        while self.match("LT", "LE", "GT", "GE"):
            op = self.advance().lex
            right = self.parse_add()
            if right is None:
                cur = self.current()
                self._error("Esperado expressao apos operador", cur.line, cur.col)
                return None
            left = BinOp(op, left, right)
        return left

    def parse_add(self):
        left = self.parse_mul()
        if left is None:
            return None
        while self.match("PLUS", "MINUS"):
            op = self.advance().lex
            right = self.parse_mul()
            if right is None:
                cur = self.current()
                self._error("Esperado expressao apos '+' ou '-'", cur.line, cur.col)
                return None
            left = BinOp(op, left, right)
        return left

    def parse_mul(self):
        left = self.parse_unary()
        if left is None:
            return None
        while self.match("STAR", "SLASH"):
            op = self.advance().lex
            right = self.parse_unary()
            if right is None:
                cur = self.current()
                self._error("Esperado expressao apos '*' ou '/'", cur.line, cur.col)
                return None
            left = BinOp(op, left, right)
        return left

    def parse_unary(self):
        if self.match("MINUS"):
            op = self.advance().lex
            node = self.parse_unary()
            if node is None:
                cur = self.current()
                self._error("Esperado expressao apos unario '-'", cur.line, cur.col)
                return None
            return BinOp(op, Num("0"), node)
        return self.parse_postfix()

    def parse_postfix(self):
        node = self.parse_primary()
        if node is None:
            return None

        while True:
            if self.match("LPAREN"):
                self.advance()
                args = []
                if not self.match("RPAREN"):
                    a = self.parse_expression()
                    if a is None:
                        cur = self.current()
                        self._error("Esperado expressao no argumento da chamada", cur.line, cur.col)
                        return None
                    args.append(a)
                    while self.match("COMMA"):
                        self.advance()
                        a = self.parse_expression()
                        if a is None:
                            cur = self.current()
                            self._error("Esperado expressao no argumento da chamada", cur.line, cur.col)
                            return None
                        args.append(a)
                if not self.expect("RPAREN"):
                    return None
                node = Call(node, args)

            elif self.match("LBRACK"):
                self.advance()
                idx = self.parse_expression()
                if idx is None:
                    cur = self.current()
                    self._error("Esperado expressao dentro de []", cur.line, cur.col)
                    return None
                if not self.expect("RBRACK"):
                    return None
                node = Index(node, idx)
            else:
                break

        return node

    def parse_primary(self):
        if self.match("NUM"):
            return Num(self.advance().lex)
        if self.match("CHAR"):
            return Char(self.advance().lex)
        if self.match("STRING"):
            return Str(self.advance().lex)
        if self.match("ID"):
            return Var(self.advance().lex)
        if self.match("LPAREN"):
            self.advance()
            e = self.parse_expression()
            if e is None:
                cur = self.current()
                self._error("Esperado expressao entre parenteses", cur.line, cur.col)
                return None
            if not self.expect("RPAREN"):
                return None
            return e
        return None
