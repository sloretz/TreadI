import lark
import pathlib

from treadi.data import Issue

GRAMMAR = (pathlib.Path(__file__).parent.resolve() / "filter.lark").read_text()
PARSER = lark.Lark(GRAMMAR, parser="lalr")


class Requirement:

    def __call__(self, issue_or_pr) -> bool:
        """Return True if the requirement is met."""
        raise NotImplementedError

    def invert(self, issue_or_pr) -> bool:
        """Return False if the requirement is met."""
        # Some requirments ignore issues,
        # so the inverse must also return True for issues
        return not self(issue_or_pr)


class RequirePR(Requirement):
    """Return True if the issue is a PR."""

    def __call__(self, issue_or_pr) -> bool:
        return issue_or_pr.is_pr


class RequireIssue(Requirement):
    """Return True if the issue is an issue."""

    def __call__(self, issue_or_pr) -> bool:
        return not issue_or_pr.is_pr


class RequireDraftIfPR(Requirement):
    """Return True if it is an Issue or a draft PR."""

    def __call__(self, issue_or_pr) -> bool:
        if issue_or_pr.is_pr:
            return issue_or_pr.draft
        return True

    def invert(self, issue_or_pr) -> bool:
        if issue_or_pr.is_pr:
            return not issue_or_pr.draft
        return True


class RequireApprovedIfPR(Requirement):
    """Return True if it is an Issue or an approved PR."""

    def __call__(self, issue_or_pr) -> bool:
        if issue_or_pr.is_pr:
            return issue_or_pr.approved
        return True

    def invert(self, issue_or_pr) -> bool:
        if issue_or_pr.is_pr:
            return not issue_or_pr.approved
        return True


class RequireChangesRequestedIfPR(Requirement):
    """Return True if it is an Issue or a PR with changes requested."""

    def __call__(self, issue_or_pr) -> bool:
        if issue_or_pr.is_pr:
            return issue_or_pr.changes_requested
        return True

    def invert(self, issue_or_pr) -> bool:
        if issue_or_pr.is_pr:
            return not issue_or_pr.changes_requested
        return True


class RequireNoReviewIfPR(Requirement):
    """Return True if it is an Issue or a PR with no reviews."""

    def __call__(self, issue_or_pr) -> bool:
        if issue_or_pr.is_pr:
            return not issue_or_pr.changes_requested and not issue_or_pr.approved
        return True

    def invert(self, issue_or_pr) -> bool:
        if issue_or_pr.is_pr:
            return issue_or_pr.changes_requested or issue_or_pr.approved
        return True


class RequireAuthor(Requirement):

    def __init__(self, author):
        self._author = author

    def __call__(self, issue_or_pr):
        """Return True if the issue is authored by this author."""
        return self._author.lower() == issue_or_pr.author.lower()


class RequireRepo(Requirement):

    def __init__(self, owner, name):
        self._owner = owner
        self._name = name

    def __call__(self, issue_or_pr):
        """Return True if the issue belongs to the given repo."""
        return (
            self._owner.lower() == issue_or_pr.repo.owner.lower()
            and self._name.lower() == issue_or_pr.repo.name.lower()
        )


class RequireOrg(Requirement):

    def __init__(self, org):
        self._org = org

    def __call__(self, issue_or_pr):
        """Return True if the issue belongs to the given organization."""
        return self._org.lower() == issue_or_pr.repo.owner.lower()


class RequireBaseBeginsWith(Requirement):

    def __init__(self, base_prefix):
        self._base_prefix = base_prefix

    def __call__(self, issue_or_pr) -> bool:
        if issue_or_pr.is_pr:
            return issue_or_pr.base_ref.startswith(self._base_prefix)
        return True

    def invert(self, issue_or_pr) -> bool:
        if issue_or_pr.is_pr:
            return not self(issue_or_pr)
        return True


class Invert(Requirement):

    def __init__(self, requirement):
        self._requirement = requirement

    def __call__(self, issue_or_pr):
        """Return the opposite of what the requirement returns."""
        return self._requirement.invert(issue_or_pr)


class RequireAll(Requirement):

    def __init__(self, requirements):
        self._requirements = tuple(requirements)

    def __call__(self, issue_or_pr):
        """Return True iff all requirements are met."""
        for requirement in self._requirements:
            if not requirement(issue_or_pr):
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
            return Invert(args[1])
        return args[0]

    def type_stmt(self, args):
        if args[0] == "pr":
            return RequirePR()
        return RequireIssue()

    def author_stmt(self, args):
        return RequireAuthor(args[0].value)

    def assignee_stmt(self, args):
        raise NotImplementedError

    def is_stmt(self, args):
        if args[0] == "pr":
            return RequirePR()
        if args[0] == "issue":
            return RequireIssue()
        if args[0] == "draft":
            return RequireDraftIfPR()

    def review_stmt(self, args):
        if args[0] == "approved":
            return RequireApprovedIfPR()
        if args[0] == "changes_requested":
            return RequireChangesRequestedIfPR()
        if args[0] == "none":
            return RequireNoReviewIfPR()

    def repo_stmt(self, args):
        return RequireRepo(args[0].value, args[1].value)

    def org_stmt(self, args):
        return RequireOrg(args[0].value)

    def base_stmt(self, args):
        return RequireBaseBeginsWith(args[0].value)


def parse(filter: str):
    tree = PARSER.parse(filter)
    return FilterTransformer().transform(tree)
