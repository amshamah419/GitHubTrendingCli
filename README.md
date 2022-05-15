# GitHubTrendingCli
This project will analyze a given number of the top trending python repositories on GitHub, check to see what dependencies are added, but not used 
and then return a risk score

## Usage
To use the GitHubTrendingCli analysis tool, you must first generate a GitHub personal access token with repository read rights.

```bash
Options:
  -h, --help                      Show this message and exit.
  -n, --num_to_search TEXT        The number of repositories to inspect.
                                  [required]
  -g, --github_access_token TEXT  Your personal access token from Github.
                                  [required]
 ```
