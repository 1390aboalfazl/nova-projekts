from .tokens import Token
from .errors import NovaSyntaxError

KEYWORDS = {
    "forge": "FORGE", "program": "PROGRAM", "begin": "BEGIN", "end": "END",
    "let": "LET", "show": "SHOW", "true": "TRUE", "false": "FALSE",
    "Int": "TYPE", "Float": "TYPE", "Bool": "TYPE", "Text": "TYPE",
}
SINGLE = {":": "COLON", "=": "EQUAL", "+": "PLUS", "-": "MINUS",
          "*": "STAR", "/": "SLASH", "(": "LPAREN", ")": "RPAREN"}

def tokenize(source: str) -> list[Token]:
    out = []
    i, line, col = 0, 1, 1
    while i < len(source):
        ch = source[i]
        if ch in " \t\r":
            i += 1; col += 1; continue
        if ch == "\n":
            out.append(Token("NEWLINE", "\\n", line, col))
            i += 1; line += 1; col = 1; continue
        if ch == "#":
            while i < len(source) and source[i] != "\n":
                i += 1; col += 1
            continue
        if ch == '"':
            sl, sc = line, col
            i += 1; col += 1; chars = []
            while i < len(source) and source[i] != '"':
                if source[i] == "\n":
                    raise NovaSyntaxError(f"Line {line}, column {col}: newline in string")
                if source[i] == "\\":
                    i += 1; col += 1
                    if i >= len(source):
                        raise NovaSyntaxError(f"Line {line}, column {col}: unfinished escape")
                    chars.append({"n":"\n", "t":"\t", '"':'"', "\\":"\\"}.get(source[i], source[i]))
                    i += 1; col += 1
                else:
                    chars.append(source[i]); i += 1; col += 1
            if i >= len(source):
                raise NovaSyntaxError(f"Line {sl}, column {sc}: unterminated string")
            i += 1; col += 1
            out.append(Token("STRING", "".join(chars), sl, sc)); continue
        if ch.isdigit():
            start, sc = i, col
            while i < len(source) and source[i].isdigit():
                i += 1; col += 1
            kind = "INT"
            if i + 1 < len(source) and source[i] == "." and source[i+1].isdigit():
                kind = "FLOAT"; i += 1; col += 1
                while i < len(source) and source[i].isdigit():
                    i += 1; col += 1
            out.append(Token(kind, source[start:i], line, sc)); continue
        if ch.isalpha() or ch == "_":
            start, sc = i, col
            while i < len(source) and (source[i].isalnum() or source[i] == "_"):
                i += 1; col += 1
            word = source[start:i]
            out.append(Token(KEYWORDS.get(word, "IDENT"), word, line, sc)); continue
        if ch in SINGLE:
            out.append(Token(SINGLE[ch], ch, line, col))
            i += 1; col += 1; continue
        raise NovaSyntaxError(f"Line {line}, column {col}: unexpected character {ch!r}")
    out.append(Token("EOF", "", line, col))
    return out
