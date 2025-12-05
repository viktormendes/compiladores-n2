int main() {
    for (i = 0; i < 5; i++) {
        // i++ not supported in parser -> but lexer will tokenize ++ as + +, causing syntax issue
        // cause an error: unexpected '++' pattern or parse failure
    }
    return 0;
}
