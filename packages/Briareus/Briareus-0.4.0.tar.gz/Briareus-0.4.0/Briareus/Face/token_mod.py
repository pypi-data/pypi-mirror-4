import tokenize
import token

class TokenModifier(object):
    def __init__(self, f):
        self.tokens = tokenize.generate_tokens(f.readline)
        self.offset = 0

    def visit(self):
        modified = []
        for toknum, tokval, tokbegin, tokend, tokline in self.tokens:
            if toknum != tokenize.COMMENT:
                modified.append((toknum, tokval))
            else:
                tokval = tokval.strip(" \t#")
                tokbegin = tokbegin[0] + self.offset, tokbegin[1]
                tokend = tokend[0] + self.offset, tokend[1]
                handler_name = "%s_handler" % tokval.split()[0]
                handler = getattr(self, handler_name, None)
                if handler:
                    new_tokens = handler(toknum, tokval, tokbegin, tokend, tokline)
                    self.offset += sum([1 for x in new_tokens if x[0]==tokenize.NEWLINE])
                    modified.extend(new_tokens)
        return tokenize.untokenize(modified)

    def parallelize_handler(self, toknum, tokval, tokbegin, tokend, tokline):
        new_tokens = []
        offset = 1
        for arg in tokval.split("with"):
            if arg.strip().startswith("const") or arg.strip().startswith("cached"):
                args = [x.strip(" \t,") for x in arg.strip().split()]
                args = [x for x in args if x not in ["and", "const", "consts", "cached"]]
                for v in args:
                    new_tokens.extend([
                                    (tokenize.NAME, v),
                                    (tokenize.OP, "="),
                                    (tokenize.NAME, "_cached"),
                                    (tokenize.OP, "("),
                                    (tokenize.NAME, v),
                                    (tokenize.OP, ")"),
                                    (tokenize.NEWLINE, "\n"),
                                    ])
                offset += len(args)
        if not hasattr(self, "parallel_token"):
            self.parallel_token = set()
        self.parallel_token.add(tokbegin[0]+offset)
        return new_tokens

    def remote_handler(self, toknum, tokval, tokbegin, tokend, tokline):
        return [
               (tokenize.OP, '@'),
               (tokenize.NAME, "_cloud"),
               (tokenize.NEWLINE, "\n"),
               (tokenize.OP, '@'),
               (tokenize.NAME, "_cached"),
               ]

    def async_handler(self, toknum, tokval, tokbegin, tokend, tokline):
        return [
               (tokenize.OP, '@'),
               (tokenize.NAME, "_async"),
               ]

