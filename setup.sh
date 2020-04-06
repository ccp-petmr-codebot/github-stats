#!/usr/bin/env bash

## For counting clones, excluding ours. Maintains a database of clones,
# updating with last fortnight's clones from the GitHub API
#
# Provides:
# - clone_count_decrement
#
# Usage:
# In e.g. `.travis.yml`:
# # for counting clones, excluding ours
# - git clone https://$GITHUB_API_TOKEN@github.com/SynerBI/github-stats \
#     --branch $TRAVIS_REPO_SLUG
# # update with last fortnight's clones from GitHub API
# - source github-stats/setup.sh
# # decrement to skip counting travis' clone
# - clone_count_decrement
#
# env requirements:
# - GITHUB_API_TOKEN  : used for access to clone stats & push permissions
# - TRAVIS_REPO_SLUG  : used for repository identifier
# - PY_EXE            : path to python (supporting `-m pip install --user`)
# - TRAVIS_JOB_NUMBER : added to push commit message
##

this=$(dirname "${BASH_SOURCE[0]}")
pushd "$this"
export GITHUB_STATS="$PWD"
${PY_EXE:-python} -m pip install --user -U -r requirements.txt
popd

gh_stats_count(){
  pushd "$GITHUB_STATS"
  while [ 1 ]; do
    git fetch
    git reset --hard origin/$TRAVIS_REPO_SLUG
    ${PY_EXE:-python} clones.py "${@}" $TRAVIS_REPO_SLUG
    ${PY_EXE:-python} summary.py  # update total
    git commit -am "update $TRAVIS_JOB_NUMBER"
    git push && break
  done
  popd
}
alias clones_count='gh_stats_count'
alias clones_count_decrement='gh_stats_count --decrement'
alias cloners_count='gh_stats_count -k uniques'
alias cloners_count_decrement='gh_stats_count -k uniques --decrement'
