import _ast

from .mccabe import get_code_complexity
from .pep8 import BaseReport, StyleGuide
from .pyflakes import checker


__all__ = 'pep8', 'mccabe', 'pyflakes'


class PEP8Report(BaseReport):

    def init_file(self, filename, lines, expected, line_offset):
        super(PEP8Report, self).init_file(
            filename, lines, expected, line_offset)
        self.errors = []

    def error(self, line_number, offset, text, check):
        code = super(PEP8Report, self).error(
            line_number, offset, text, check)

        self.errors.append(dict(
            text=text,
            type=code,
            col=offset + 1,
            lnum=line_number,
        ))

    def get_file_results(self):
        return self.errors

P8Style = StyleGuide(reporter=PEP8Report)


def pep8(path, code=None, **meta):
    " PEP8 code checking. "

    return P8Style.input_file(path)


def mccabe(path, code=None, complexity=8, **meta):
    " MCCabe code checking. "

    return get_code_complexity(code, complexity, filename=path)


def pyflakes(path, code=None, **meta):
    " PyFlakes code checking. "

    errors = []
    tree = compile(code, path, "exec", _ast.PyCF_ONLY_AST)
    w = checker.Checker(tree, path)
    w.messages.sort(lambda a, b: cmp(a.lineno, b.lineno))
    for w in w.messages:
        errors.append(dict(
            lnum=w.lineno,
            col=w.col,
            text=w.message % w.message_args,
            type='E'
        ))
    return errors
