from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Any


# Tokens e Erros


@dataclass
class Token:
    type: str
    lex: str
    line: int
    col: int

@dataclass
class LexError:
    message: str
    line: int
    col: int

    def __str__(self):
        return f"{self.message} @ {self.line}:{self.col}"

@dataclass
class SyntaxErrorInfo:
    message: str
    line: int
    col: int

    def __str__(self):
        return f"{self.message} @ {self.line}:{self.col}"


# AST Base


class ASTNode:
    pass

@dataclass
class Program(ASTNode):
    body: List[ASTNode]


# Declarações

@dataclass
class FunctionDecl(ASTNode):
    ret_type: str
    name: str
    params: List[tuple]
    body: Optional['Block']   

@dataclass
class VarDecl(ASTNode):
    var_type: str
    name: str
    init: Optional[ASTNode] = None

# Statements

@dataclass
class Assign(ASTNode):
    target: ASTNode
    value: ASTNode

@dataclass
class If(ASTNode):
    test: ASTNode
    then: Optional['Block']          
    otherwise: Optional['Block'] = None 

@dataclass
class While(ASTNode):
    test: ASTNode
    body: Optional['Block']          

@dataclass
class For(ASTNode):
    init: Optional[ASTNode]
    cond: Optional[ASTNode]
    step: Optional[ASTNode]
    body: Optional['Block']

@dataclass
class Return(ASTNode):
    value: Optional[ASTNode] = None

@dataclass
class Block(ASTNode):
    body: List[ASTNode]

# Expressões

@dataclass
class BinOp(ASTNode):
    op: str
    left: ASTNode
    right: ASTNode

@dataclass
class Call(ASTNode):
    callee: ASTNode
    args: List[ASTNode]

@dataclass
class Index(ASTNode):
    target: ASTNode
    index: ASTNode

@dataclass
class Var(ASTNode):
    name: str

@dataclass
class Num(ASTNode):
    value: str

@dataclass
class Char(ASTNode):
    value: str

@dataclass
class Str(ASTNode):
    value: str
