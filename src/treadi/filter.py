# Implemenation of filtering of displayed issuses, like a github filter
# https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/filtering-and-searching-issues-and-pull-requests
# Usage:
# f = Filter('type:issue label:"bug"')
# cache.most_recent_issues(n=5, filter=f)


# Query parsing
# AND, OR, Paretheses - figure out later
# Use a BNF grammar because that's the most principled
# Start with type:issue or type:pr
# Also do author:foobar because that's useful to me
# Lark parser b/c I'm used to it

import lark
import pathlib

GRAMMAR = (pathlib.Path(__file__).parent.resolve() / "filter.lark").read_text()
PARSER = lark.Lark(GRAMMAR, parser="lalr", strict=True)


def parse(filter: str):
    tree = PARSER.parse(filter)


class Query:

    def __init__(self, query: str):
        # TODO parse the query
        pass

    # Maybe classmethod for from string, with args to __init__ being implementation details
    @classmethod
    def from_string(cls, query: str) -> "Query":
        # TODo parse the query
        pass


class Filter:

    def __init__(self, query: str):
        # TODO Validate query
        self._query = Query(query)

    def __call__(self, issue) -> bool:
        """
        Return True if the issue passes the filter
        """
        raise NotImplementedError
        return False
