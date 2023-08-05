from ebcompiler import EBCompiler, EBSyntaxError
import unittest

class EBCompilerTestCase(unittest.TestCase):
    def test_small(self):
        input = 'a || (!b && !c)'
        output = EBCompiler.convert(input)

        self.assertEqual(output, 'a IS TRUE OR (b IS FALSE AND c IS FALSE)')

    def test_large(self):
        input = '(a! && b!? && !?c && d!? && e!? && !?f && g!?) || (a && b? && c? && e? && f? && ?g)'
        output = EBCompiler.convert(input)

        self.assertEqual(output, '(a IS FALSE AND b IS NULL AND c IS NULL AND d IS NULL AND e IS NULL AND f IS NULL AND g IS NULL) OR (a IS TRUE AND b IS NOT NULL AND c IS NOT NULL AND e IS NOT NULL AND f IS NOT NULL AND g IS NOT NULL)')

    def test_trailing_unary(self):
        input = 'a && b && c?'
        output = EBCompiler.convert(input)

        self.assertEqual(output, 'a IS TRUE AND b IS TRUE AND c IS NOT NULL')

    def test_syntax_error(self):
        input = '!a < b'
        with self.assertRaises(EBSyntaxError):
            output = EBCompiler.convert(input)

if __name__ == '__main__':
    unittest.main()
