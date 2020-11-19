from unittest import TestCase

from cmaj.syntax.parser import SyntaxDefParser


class TestParser(TestCase):

    def test_given_empty_definition_then_empty_result(self):
        parser = SyntaxDefParser()
        syntax = parser.parse('')
        self.assertEqual(0, len(syntax.identifiers))

    def test_given_multiple_empty_lines_then_no_rules(self):
        parser = SyntaxDefParser()
        syntax = parser.parse('\n \n   \n\n  ')
        self.assertEqual(0, len(syntax.rules))

    def test_given_comments_then_no_rules(self):
        parser = SyntaxDefParser()
        syntax = parser.parse('# comment \n  # other comment\n\n#   last comment')
        self.assertEqual(0, len(syntax.rules))

    def test_given_token_then_rule_accepts_token(self):
        parser = SyntaxDefParser()
        syntax = parser.parse('a-valid-identifier = "1"\n'
                              'A-VALID-IDENTIFIER = "2"')
        self.assertEqual('1', syntax.rules['a-valid-identifier']('1'))
        self.assertEqual('2', syntax.rules['A-VALID-IDENTIFIER']('2'))

    def test_given_end_of_line_then_rule_accepts_line_break(self):
        parser = SyntaxDefParser()
        syntax = parser.parse('value = $')
        self.assertEqual('\n', syntax.rules['value']('\n'))

    def test_given_options_then_rule_accepts_first_match(self):
        parser = SyntaxDefParser()
        syntax = parser.parse('value = "tokenizer" | "token" | "tokenize"')
        self.assertEqual('token', syntax.rules['value']('tokenize'))
        self.assertEqual('tokenizer', syntax.rules['value']('tokenizer'))

    def test_given_sequence_then_rule_requires_order(self):
        parser = SyntaxDefParser()
        syntax = parser.parse('value = "to-" , "ken-" , "iz-" , "er"')
        self.assertEqual('to-ken-iz-er', syntax.rules['value']('to-ken-iz-er'))
        self.assertIsNone(syntax.rules['value']('to-ken-'))
        self.assertIsNone(syntax.rules['value']('to-iz-ken-er'))

    def test_given_maybe_then_rule_can_skip_token(self):
        parser = SyntaxDefParser()
        syntax = parser.parse('value = "call me" , [ " maybe" ] , "!"')
        self.assertEqual('call me!', syntax.rules['value']('call me!'))
        self.assertEqual('call me maybe!', syntax.rules['value']('call me maybe!'))

    def test_given_repetition_then_rule_repeats(self):
        parser = SyntaxDefParser()
        syntax = parser.parse('value = { "pa-" } , "poker face"')
        self.assertEqual('pa-pa-pa-poker face', syntax.rules['value']('pa-pa-pa-poker face'))
        self.assertEqual('pa-pa-poker face', syntax.rules['value']('pa-pa-poker face'))
        self.assertEqual('poker face', syntax.rules['value']('poker face'))

    def test_given_token_with_control_symbol_then_rule_matches_control_symbol(self):
        parser = SyntaxDefParser()
        syntax = parser.parse('value = "$" , "," , "|" | "[", "]" , "{" , "}"')
        self.assertEqual('$,|', syntax.rules['value']('$,|[]{}'))
        self.assertEqual('[]{}', syntax.rules['value']('[]{}$,|'))

    def test_given_ref_then_rule_resolves_ref(self):
        parser = SyntaxDefParser()
        syntax = parser.parse('index = "0" | "1"\n'
                              'variable = "x" , index')
        self.assertEqual('x0', syntax.rules['variable']('x0'))
        self.assertEqual('x1', syntax.rules['variable']('x1'))
        self.assertIsNone(syntax.rules['variable']('x'))
        self.assertIsNone(syntax.rules['variable']('x2'))

    def test_given_self_ref_then_rule_resolves_ref(self):
        parser = SyntaxDefParser()
        syntax = parser.parse('dots = "." , dots | ""')
        self.assertEqual('', syntax.rules['dots'](''))
        self.assertEqual('.', syntax.rules['dots']('.'))
        self.assertEqual('...', syntax.rules['dots']('...'))

    def test_well_behaved_circular_ref_then_rule_resolves_ref(self):
        parser = SyntaxDefParser()
        syntax = parser.parse('sender   = "Marco?" , receiver | "_"\n'
                              'receiver = " Polo! " , sender')
        self.assertEqual('Marco? Polo! _', syntax.rules['sender']('Marco? Polo! _'))
        self.assertEqual('Marco? Polo! Marco? Polo! _', syntax.rules['sender']('Marco? Polo! Marco? Polo! _'))
        self.assertIsNone(syntax.rules['sender']('Marco? Polo! Marco? _'))
