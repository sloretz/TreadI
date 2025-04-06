# Use a personal access token

TreadI must authenticate with Github so that it can query issues and pull requests through [Github's API](https://docs.github.com/en/graphql).

By default, TreadI prompts you to authenticate with Github using TreadI's [Github App](https://docs.github.com/en/apps/overview).
However, this way of authenticating only gives TreadI read access to public repositories.

If you want to use TreadI to manage issues and pull requests in a private repository, you must give it a personal access token instead.

TODO
* Create a fine-grained access token with no permissions except read-access to the private repo private repositories
* Save it in the system keyring with `keyring set TreadI GithubPersonalAccessToken`
* If you've authed with both, TreadI will only use the PAT
* If you want to stop using the PAT, you must run `keyring del TreadI GithubPersonalAccessToken` to remove the PAT from the keyring