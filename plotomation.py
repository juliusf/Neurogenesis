#!/usr/bin/env python

import git
import sys

from neurogenesis.plotter import plot_simulations


def main():
	repo_path = '/Users/jules/dev/simulation_configs'

	meta_files = get_latest_meta_files(repo_path)

	for file in meta_files:
		print(file)


def get_latest_meta_files(repo_path):
	git.cmd.Git(repo_path).pull()
	repo = git.Repo(repo_path)
	changed_files = repo.git.diff('HEAD~1..HEAD', name_only=True).split('\n')
	meta_files = []
	for file in changed_files:
		if 'meta.pickle' in file:
			meta_files.append(file)
	return meta_files

if __name__ == "__main__":
    main()