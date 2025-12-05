import os, sys
from lexer import lex
from parser import Parser
from visualizer import draw_tree

def ensure_trees():
    if not os.path.exists("trees"):
        os.makedirs("trees")

def run_file(path: str):
    print(f"\n--- Processando: {path}")

    
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

   
    tokens, lex_errors = lex(code)

    print("Tokens:")
    for t in tokens:
        print(f"  {t.type:8s} '{t.lex}'  ({t.line}:{t.col})")

    if lex_errors:
        print("\nErros lexicos:")
        for e in lex_errors:
            print(" ", e)
        print("Pulando analise sintatica por erros lexicos.\n")
        return  # DO NOT parse or generate AST

    
    parser = Parser(tokens)
    program, errors = parser.parse_program()

    if errors:
        print("\nErros sintaticos:")
        for er in errors:
            print(" ", er)
        print("Pulando geracao da AST por erros sintaticos.\n")
        return

   
    print("\nParse concluido. Gerando imagens da AST...")
    ensure_trees()
    fname = os.path.splitext(os.path.basename(path))[0]
    out = f"trees/{fname}_program.png"
    draw_tree(program, out)
    print("Salvo:", out)

def run_examples_folder():
    examples_dir = os.path.join(os.path.dirname(__file__), "examples")
    files = sorted(os.listdir(examples_dir))
    for f in files:
        if f.endswith(".c"):
            run_file(os.path.join(examples_dir, f))

def main():
    if len(sys.argv) >= 2:
        run_file(sys.argv[1])
    else:
        run_examples_folder()

if __name__ == "__main__":
    main()
