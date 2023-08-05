from ebcompiler import EBCompiler, EBSyntaxError
import unittest

class EBCompilerTestCase(unittest.TestCase):
    def test_small(self):
        input = 'a || (!b && !c)'
        output = EBCompiler.convert(input)

        self.assertEqual(output, 'a IS TRUE || (b IS FALSE && c IS FALSE)')

    def test_large(self):
        input = '(a! && b!? && !?c && d!? && e!? && !?f && g!?) || (a && b? && c? && e? && f? && ?g)'
        output = EBCompiler.convert(input)

        self.assertEqual(output, '(a IS FALSE && b IS NULL && c IS NULL && d IS NULL && e IS NULL && f IS NULL && g IS NULL) || (a IS TRUE && b IS NOT NULL && c IS NOT NULL && e IS NOT NULL && f IS NOT NULL && g IS NOT NULL)')

    def test_syntax_error(self):
        input = '!a < b'
        with self.assertRaises(EBSyntaxError):
            output = EBCompiler.convert(input)

if __name__ == '__main__':
    unittest.main()
