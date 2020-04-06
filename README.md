# GitHub Statistics

## clones

For counting clones, excluding ours. Maintains a database of clones,
updating with last fortnight's clones from the GitHub API.

### Provides

- bash:`clone_count_decrement`

### Usage

In e.g. `.travis.yml`:

```yml
# for counting clones, excluding ours
- git clone https://$GITHUB_API_TOKEN@github.com/SynerBI/github-stats \
    --branch $TRAVIS_REPO_SLUG
# update with last fortnight's clones from GitHub API
- source github-stats/setup.sh
# decrement to skip counting travis' clone, and print total number of clones
- clone_count_decrement
```

### Requirements

| env | description  |
|:--|:--|
| `GITHUB_API_TOKEN`  | used for access to clone stats & push permissions |
| `TRAVIS_REPO_SLUG`  | used for repository identifier |
| `PY_EXE`            | path to python (supporting `-m pip install --user`) |
| `TRAVIS_JOB_NUMBER` | added to push commit message |

### Viewing

To view statistics, run `./clones.py $TRAVIS_REPO_SLUG`, for example:

```bash
$ git clone https://github.com/SynerBI/github-stats --branch CCPPETMR/SIRF-SuperBuild
$ cd github-stats
$ ./clones.py CCPPETMR/SIRF-SuperBuild
```

or simply run `./summary.py`
