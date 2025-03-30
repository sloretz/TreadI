from treadi.data import Issue
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
    is_read=False,
    is_pr=False,
)
PR_ROS_ROSDISTRO = Issue(
    repo=REPO_ROS_ROSDITRO,
    author="ghost",
    created_at=None,
    updated_at=None,
    number=1,
    title="break stuff",
    url="",
    is_read=False,
    is_pr=True,
)


def test_require_pr():
    assert tf.require_pr(PR_ROS_ROSDISTRO)
    assert not tf.require_pr(ISSUE_ROS_ROSDISTRO)


def test_require_issue():
    assert tf.require_issue(ISSUE_ROS_ROSDISTRO)
    assert not tf.require_issue(PR_ROS_ROSDISTRO)


def test_require_author():
    assert tf.RequireAuthor("sloretz")(ISSUE_ROS_ROSDISTRO)
    assert not tf.RequireAuthor("bob")(ISSUE_ROS_ROSDISTRO)


def test_require_repo():
    assert tf.RequireRepo("ros", "rosdistro")(ISSUE_ROS_ROSDISTRO)
    assert not tf.RequireRepo("ros2", "ros2")(ISSUE_ROS_ROSDISTRO)


def test_require_repo():
    assert tf.RequireOrg("ros")(ISSUE_ROS_ROSDISTRO)
    assert not tf.RequireOrg("ros2")(ISSUE_ROS_ROSDISTRO)


def test_invert_requirement():
    assert not tf.InvertRequirement(tf.require_pr)(PR_ROS_ROSDISTRO)
    assert tf.InvertRequirement(tf.require_pr)(ISSUE_ROS_ROSDISTRO)


def test_require_all():
    assert tf.RequireAll([tf.RequireAuthor("sloretz"), tf.require_issue])(
        ISSUE_ROS_ROSDISTRO
    )
    assert not tf.RequireAll([tf.RequireAuthor("ghost"), tf.require_issue])(
        PR_ROS_ROSDISTRO
    )
    assert not tf.RequireAll([tf.RequireAuthor("sloretz"), tf.require_issue])(
        PR_ROS_ROSDISTRO
    )
