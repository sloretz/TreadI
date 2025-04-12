---
title: Custom Repository Lists
parent: Reference
---

* TOC
{:toc}

Want to use TreadI with your own list of repositories?
Create a new list in the `repository_lists.d/` directory.
TreadI creates this directory the first time it is run.
The location of the directory depends on your operating system.

**Linux:**

```
~/.config/TreadI/repository_lists.d
```

*Note, the location respects the value of `XDG_CONFIG_HOME` or `XDG_HOME`.*
*If you don't see `~/.config/TreadI` after you run TreadI once, then it has been created somewhere else according to the [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/latest/).*

**OSX:**

```
/Users/YOUR USERNAME/Library/Application Support/TreadI/repository_lists.d
```

**Windows:**

If you have a Windows machine, please run the following Python code to determine the config directory path.
Then, please [open a PR to update this documentation](https://github.com/sloretz/TreadI).

```python
from pathlib import Path
from platformdirs import user_config_dir

base = Path(user_config_dir("TreadI"))
print(base / Path("repository_lists.d"))
```

## Create a repository list

To create a custom repository list, create a file in `repository_lists.d/` with a name like this:

```
XX_Some_Name.txt
```

Replace `XX` with a two digit number [`00`, `01`, `02`, ...`99`].

Do not use spaces in the file name.
Use underscores `_` instead.
TreadI displays `04_Some_Name.txt` as `Some Name` in the repository list picker screen.

TreadI sorts repository lists so that lower numbers are first in the list.
If two lists have the same number, then TreadI sorts them alphabetically.

*Example valid file names*

```
01_My_Repo_List.txt
50_Yet_another.txt
50_Another_Another.txt
96_Another_One.txt
```

*How TreadI displays the example file names*

```
My Repo List
Another Another
Yet another
Another one
```

## Repository list syntax

A repository list is a file with one directive per line.
Each directive adds to the number of repositories included in the list.

### Comments
Use `#` to begin a comment.
TreadI ignores all text on the same line after a `#` character.

```
# This is a comment
foo/bar  # Comments can be after a directive
```

### Directive: One repository

To include a specifc repository in your repository list, use the format:

```
owner/repo
```

For example, to include issues and PRs from [TreadI's repository](https://github.com/sloretz/TreadI), put this line into your repository list:

```
sloretz/TreadI
```

### Directive: All repositories in an organization

To include all repositories in an organization in your repository list, use the format:

```
org:org_name
```

For example, to include issues and PRs from the [Gazebosim org](https://github.com/gazebosim), put this line into your repository list:

```
org:gazebosim
```

### Directive: All repositories owned by a user

To include all repositories owned by a Github user, use the format:

```
owned-by:username
```

### Directive: All repositories owned by the current user

To include all repositories owned by the Github user who launched TreadI, put this line into your repository list:

```
owned-by:@me
```

### Directive: vcstool URL

To include all repositories in a [vcstool](https://github.com/dirk-thomas/vcstool) repos file in your repository list, put an `https://` URL on one line with `vcstool:` as a prefix.

```
vcstool:https://www.example.com/some/list.repos
```

For example, to include all issues and PRs from [ros2/ros2](https://github.com/ros2/ros2)'s ROS Rolling repos file, put this line into your repository list:

```
vcstool:https://raw.githubusercontent.com/ros2/ros2/refs/heads/rolling/ros2.repos
```