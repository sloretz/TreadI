import lark

import pytest

from treadi.filter import GRAMMAR


@pytest.fixture
def parser():
    return lark.Lark(GRAMMAR, parser="lalr", debug=True, strict=True)


def test_negation(parser):
    parser.parse("-type:issue")
    parser.parse("-author:slorretz")
    parser.parse("-repo:ros/rosdistro")


def test_multiple(parser):
    parser.parse("-type:issue author:sloretz -repo:ros/rodistro")


def test_type(parser):
    parser.parse("type:issue")
    parser.parse("type:pr")
    with pytest.raises(lark.UnexpectedToken):
        parser.parse("type:foo")
    with pytest.raises(lark.UnexpectedToken):
        parser.parse("type: issue")


def test_author(parser):
    parser.parse("author:sloretz")
    with pytest.raises(lark.UnexpectedToken):
        parser.parse("author:-sloretz")


def test_assignee(parser):
    parser.parse("assignee:sloretz")
    with pytest.raises(lark.UnexpectedCharacters):
        parser.parse("assignee:*sloretz")


def test_is(parser):
    parser.parse("is:draft")
    with pytest.raises(lark.UnexpectedToken):
        parser.parse("is:candy")


def test_review(parser):
    parser.parse("review:none")
    parser.parse("review:approved")
    parser.parse("review:changes_requested")
    with pytest.raises(lark.UnexpectedToken):
        parser.parse("review:candy")


def test_repo(parser):
    parser.parse("repo:sloretz/TreadI")
    parser.parse("repo:sloretz/rmw_zenow")
    parser.parse("repo:sloretz/..--__Hello1")
    with pytest.raises(lark.UnexpectedToken):
        parser.parse("repo:sloretz")
