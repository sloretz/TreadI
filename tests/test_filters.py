import copy

from treadi.data import Issue
from treadi.data import PullRequest
from treadi.data import Repository
import treadi.filter as tf

REPO_ROS_ROSDITRO = Repository(
    owner="ros",
    name="rosdistro",
)
REPO_ROS2_ROS2 = Repository(
    owner="ros2",
    name="ros2",
)
ISSUE_ROS_ROSDISTRO = Issue(
    repo=REPO_ROS_ROSDITRO,
    author="sloretz",
    created_at=None,
    updated_at=None,
    number=42,
    title="fix stuff",
    url="",
    is_pr=False,
)
PR_ROS_ROSDISTRO = PullRequest(
    repo=REPO_ROS_ROSDITRO,
    author="ghost",
    created_at=None,
    updated_at=None,
    number=1,
    title="break stuff",
    url="",
    is_pr=True,
    base_ref="rolling",
)
DRAFT_PR_ROS_ROSDISTRO = PullRequest(
    repo=REPO_ROS_ROSDITRO,
    author="ghost",
    created_at=None,
    updated_at=None,
    number=1,
    title="break stuff",
    url="",
    is_pr=True,
    draft=True,
    base_ref="main",
)
APPROVED_PR_ROS_ROSDISTRO = PullRequest(
    repo=REPO_ROS_ROSDITRO,
    author="ghost",
    created_at=None,
    updated_at=None,
    number=1,
    title="break stuff",
    url="",
    is_pr=True,
    approved=True,
    base_ref="master",
)
CHANGES_REQUESTED_PR_ROS_ROSDISTRO = PullRequest(
    repo=REPO_ROS_ROSDITRO,
    author="ghost",
    created_at=None,
    updated_at=None,
    number=1,
    title="break stuff",
    url="",
    is_pr=True,
    changes_requested=True,
    base_ref="rolling",
)


def test_require_pr():
    for f in [tf.parse("is:pr"), tf.parse("type:pr")]:
        assert f(PR_ROS_ROSDISTRO)
        assert not f(ISSUE_ROS_ROSDISTRO)


def test_require_issue():
    for f in [tf.parse("is:issue"), tf.parse("type:issue")]:
        assert f(ISSUE_ROS_ROSDISTRO)
        assert not f(PR_ROS_ROSDISTRO)


def test_require_author():
    f = tf.parse("author:sloretz")
    assert f(ISSUE_ROS_ROSDISTRO)
    f = tf.parse("author:bob")
    assert not f(ISSUE_ROS_ROSDISTRO)


def test_require_repo():
    assert tf.RequireRepo("ros", "rosdistro")(ISSUE_ROS_ROSDISTRO)
    assert not tf.RequireRepo("ros2", "ros2")(ISSUE_ROS_ROSDISTRO)


def test_require_draft_if_pr():
    f = tf.parse("is:draft")
    assert f(ISSUE_ROS_ROSDISTRO)
    assert not f(PR_ROS_ROSDISTRO)
    assert f(DRAFT_PR_ROS_ROSDISTRO)


def test_require_base_if_pr():
    f = tf.parse("base:roll")
    fnot = tf.parse("-base:roll")

    rolling_pr = copy.deepcopy(PR_ROS_ROSDISTRO)
    main_pr = copy.deepcopy(PR_ROS_ROSDISTRO)
    rolling_pr.base_ref = "rolling"
    main_pr.base_ref = "main"

    assert f(ISSUE_ROS_ROSDISTRO)
    assert fnot(ISSUE_ROS_ROSDISTRO)
    assert f(rolling_pr)
    assert not fnot(rolling_pr)
    assert not f(main_pr)
    assert fnot(main_pr)


def test_invert_require_draft_if_pr():
    f = tf.parse("-is:draft")
    assert f(ISSUE_ROS_ROSDISTRO)
    assert f(PR_ROS_ROSDISTRO)
    assert not f(DRAFT_PR_ROS_ROSDISTRO)


def test_require_approved_if_pr():
    f = tf.parse("review:approved")
    assert f(ISSUE_ROS_ROSDISTRO)
    assert not f(PR_ROS_ROSDISTRO)
    assert f(APPROVED_PR_ROS_ROSDISTRO)


def test_invert_require_approved_if_pr():
    f = tf.parse("-review:approved")
    assert f(ISSUE_ROS_ROSDISTRO)
    assert f(PR_ROS_ROSDISTRO)
    assert not f(APPROVED_PR_ROS_ROSDISTRO)


def test_require_changes_requested_if_pr():
    f = tf.parse("review:changes_requested")
    assert f(ISSUE_ROS_ROSDISTRO)
    assert not f(PR_ROS_ROSDISTRO)
    assert f(CHANGES_REQUESTED_PR_ROS_ROSDISTRO)


def test_invert_require_changes_requested_if_pr():
    f = tf.parse("-review:changes_requested")
    assert f(ISSUE_ROS_ROSDISTRO)
    assert f(PR_ROS_ROSDISTRO)
    assert not f(CHANGES_REQUESTED_PR_ROS_ROSDISTRO)


def test_require_no_review_if_pr():
    f = tf.parse("review:none")
    assert f(ISSUE_ROS_ROSDISTRO)
    assert f(PR_ROS_ROSDISTRO)
    assert not f(APPROVED_PR_ROS_ROSDISTRO)
    assert not f(CHANGES_REQUESTED_PR_ROS_ROSDISTRO)


def test_multiple():
    f = tf.parse("author:sloretz is:issue")
    assert f(ISSUE_ROS_ROSDISTRO)
    assert not f(PR_ROS_ROSDISTRO)
