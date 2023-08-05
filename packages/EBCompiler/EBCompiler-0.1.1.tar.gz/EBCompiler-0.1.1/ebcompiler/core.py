import re
import itertools

class TokenIterator:
    def __init__(self, tokens):
        self.tokens = tokens
        self.filter = None
        self.i = 0 # the index of the next token

    def __iter__(self):
        return self

    def __next__(self):
        # seek to the next token
        while True:
            if self.i >= len(self.tokens):
                raise StopIteration
            
            filter_matches = self._filter_matches()
            self.i += 1

            if not filter_matches:
                continue

            name, token = self.tokens[self.i - 1]

            return name, token

    # Python 2.x compatibility
    def next(self):
        return self.__next__()

    def _filter_matches(self):
        if self.filter is None:
            return True

        for i in range(len(self.filter)):
            if self.filter[i] != self.tokens[self.i + i][0]:
                return False

        return True

    def peek_name(self, i=0):
        return self.peek(i)[0]

    def peek(self, i=0):
        return self.tokens[self.i + (i - 1)]

    def move(self, from_i, to_i):
        from_i += self.i - 1
        to_i += self.i - 1

        if from_i < to_i:
            to_i -= 1
        if from_i < self.i:
            self.i -= 1
        if to_i < self.i:
            self.i += 1

        item = self.tokens.pop(from_i)
        self.tokens.insert(to_i, item)

    def insert(self, i, name, token):
        self.tokens.insert(self.i + (i - 1), (name, token))

        if i < 0:
            self.i += 1

    def replace(self, i=0, name=None, token=None):
        new_tuple = list(self.tokens[self.i + (i - 1)])
        if name:
            new_tuple[0] = name
        if token:
            new_tuple[1] = token
        if name or token:
            self.tokens[self.i + (i - 1)] = tuple(new_tuple)

    def remove(self, i=0):
        self.tokens.pop(self.i + (i - 1))

        if i < 0:
            self.i -= 1

    def reset(self):
        self.i = 0

class EBSyntaxError(Exception):
    pass

# existential boolean compiler
class EBCompiler:
    unary_to_sql = {
        '!': 'IS FALSE',
        '?': 'IS NOT NULL',
        '!?': 'IS NULL',
    }

    token_checks = [
        ('NAME', r'([a-zA-Z][a-zA-Z0-9_]*)'),
        ('WHITESPACE', r'(\s+)'),
        ('LOGICAL_OPERATOR', r'(\|\||&&)'),
        ('UNARY_OPERATOR', r'(!\?|!|\?)'),
        ('OPEN_PARENTHESIS', r'\('),
        ('CLOSE_PARENTHESIS', r'\)'),
    ]

    def tokenize(self, s):
        checks_tried = 0
        for name, regex in itertools.cycle(EBCompiler.token_checks):
            # if the string is empty, we are done
            if not s:
                return

            # try the current token check
            m = re.match(regex, s)

            # if the check was successful, return the token
            if m:
                yield (name, m.group(0))
                s = s[len(m.group(0)):]
                checks_tried = 0

            # have we tried all of the checks on the upcoming token?
            checks_tried += 1
            if checks_tried == len(EBCompiler.token_checks) + 1:
                raise EBSyntaxError('Invalid token: ' + s)

    def parser(self, tokens):
        tokens = list(tokens)
        
        ti = TokenIterator(tokens)

        # converted prefix unary operators to suffix
        ti.filter = ['UNARY_OPERATOR', 'NAME']
        ti.reset()
        for name, token in ti:
            ti.move(0, 2)

        # convert unary operators to their real SQL counterparts
        ti.reset()
        ti.filter = ['NAME']
        for name, token in ti:
            next_name, next_token = ti.peek(1)

            if next_name == 'UNARY_OPERATOR' and next_token in EBCompiler.unary_to_sql:
                ti.replace(i=1, name='SQL_OPERATOR', token=EBCompiler.unary_to_sql[next_token])
            elif next_name == 'UNARY_OPERATOR':
                raise Exception('Unexpected UNARY_OPERATOR: ' + next_token)
            else:
                ti.insert(i=1, name='SQL_OPERATOR', token='IS TRUE')

            ti.insert(i=1, name='WHITESPACE', token=' ')
        
        return tokens

    def compile(self, tokens):
        tokens = map(lambda token: token[1], tokens)
        return ''.join(tokens)

    @staticmethod
    def convert(s):
        compiler = EBCompiler()
        tokens = compiler.tokenize(s)
        tokens = compiler.parser(tokens)
        return compiler.compile(tokens)
