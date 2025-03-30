# TreadI repository_lists.d/

TreadI's repo-picker screen displays repository lists that it finds in `repository_lists.d` directory.
When you click on a repository list, TreadI will only display issues and PRs from repositories in that list.

## Create a repository list

To make TreadI display your own custom repository list, create a file in `repository_lists.d/` with a name like this:

```
XX_Some_Name.txt
```

Replace `XX` with a two digit number [`00`, `01`, `02`, ...`99`].
TreadI displays repository lists with lower numbers first, and it sorts repositories with equal numbers alphabetically.

Do not use spaces in the file name.
TreadI displays `04_Some_Name.txt` as `Some Name` in the repo-picker screen.

## Repository list syntax

### Comments
Use `#` to begin a comment.
TreadI ignores all text on the same line after a `#` character.

### Directives

Repository lists must have only one directive per line.

#### Directive: One repository

To include a specifc repository in your repository list, use the format:

```
owner/repo
```

For example, to include issues and PRs from [TreadI's repository](https://github.com/sloretz/TreadI), put this line into your repository list:

```
sloretz/TreadI
```

#### Directive: All repositories in an organization

To include all repositories in an organization in your repository list, use the format:

```
org:org_name
```

For example, to include issues and PRs from the [Gazebosim org](https://github.com/gazebosim), put this line into your repository list:

```
org:gazebosim
```

#### Directive: All repositories owned by a user

To include all repositories owned by a Github user, use the format:

```
owned-by:username
```

#### Directive: All repositories owned by the current user

To include all repositories owned by the Github user who launched TreadI, put this line into your repository list:

```
owned-by:@me
```

#### Directive: vcstool URL

To include all repositories in a [vcstool](https://github.com/dirk-thomas/vcstool) repos file in your repository list, put an `https://` URL on one line with `vcstool:` as a prefix.

```
vcstool:https://www.example.com/some/list.repos
```

For example, to include all issues and PRs from [ros2/ros2](https://github.com/ros2/ros2)'s ROS Rolling repos file, put this line into your repository list:

```
vcstool:https://raw.githubusercontent.com/ros2/ros2/refs/heads/rolling/ros2.repos
```
