import lark
import pathlib

from treadi.data import Issue

GRAMMAR = (pathlib.Path(__file__).parent.resolve() / "filter.lark").read_text()
PARSER = lark.Lark(GRAMMAR, parser="lalr")


def require_pr(issue: Issue):
    """Return True if the issue is a PR."""
    return issue.is_pr


def require_issue(issue: Issue):
    """Return True if the issue is an issue."""
    return not issue.is_pr


class RequireAuthor:

    def __init__(self, author):
        self._author = author

    def __call__(self, issue: Issue):
        """Return True if the issue is authored by this author."""
        return self._author.lower() == issue.author.lower()


class RequireRepo:

    def __init__(self, owner, name):
        self._owner = owner
        self._name = name

    def __call__(self, issue: Issue):
        """Return True if the issue belongs to the given repo."""
        return (
            self._owner.lower() == issue.repo.owner.lower()
            and self._name.lower() == issue.repo.name.lower()
        )


class InvertRequirement:

    def __init__(self, requirement):
        self._requirement = requirement

    def __call__(self, issue: Issue):
        """Return the opposite of what the requirement returns."""
        return not self._requirement(issue)


class RequireAll:

    def __init__(self, requirements):
        self._requirements = tuple(requirements)

    def __call__(self, issue: Issue):
        """Return True iff all requirements are met."""
        for requirement in self._requirements:
            if not requirement(issue):
                return False
        return True


class FilterTransformer(lark.Transformer):
    """Turn a lark parse tree into a callable that filters issues."""

    def start(self, args):
        return RequireAll(args)

    def statement(self, args):
        return args[0]

    def maybe_negated_statement(self, args):
        if args[0] == "-":
            return InvertRequirement(args[1])
        return args[0]

    def type_stmt(self, args):
        if args[0] == "pr":
            return require_pr
        return require_issue

    def author_stmt(self, args):
        return RequireAuthor(args[0].value)

    def assignee_stmt(self, args):
        raise NotImplementedError

    def is_stmt(self, args):
        if args[0] == "pr":
            return require_pr
        if args[0] == "issue":
            return require_issue
        raise NotImplementedError

    def review_stmt(self, args):
        raise NotImplementedError

    def repo_stmt(self, args):
        return RequireRepo(args[0].value, args[1].value)


def parse(filter: str):
    tree = PARSER.parse(filter)
    return FilterTransformer().transform(tree)
