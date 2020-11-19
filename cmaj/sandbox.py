from cmaj.syntax.parser import SyntaxDef, SyntaxDefParser


def create_parser(syntax: str) -> SyntaxDef:
    parser = SyntaxDefParser()
    return parser.parse(syntax)


def main():
    syntax = create_parser('x = c , "0" | c\n'
                           'c = "0" | "1"\n')

    root = syntax.parse('10', rule=syntax.rules['x'])
    print(f'{root}')


if __name__ == '__main__':
    main()
