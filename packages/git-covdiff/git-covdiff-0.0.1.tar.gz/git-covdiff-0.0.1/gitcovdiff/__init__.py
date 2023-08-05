from __future__ import print_function
import os
import sys

import pygit2
import coverage


def collect_addition(hunk):
    result = []
    context_or_addition = filter(lambda l: l[1] in (pygit2.GIT_DIFF_LINE_CONTEXT,
                                                    pygit2.GIT_DIFF_LINE_ADDITION),
                                 hunk.data)
    for index, line in enumerate(context_or_addition):
        if line[1] == pygit2.GIT_DIFF_LINE_ADDITION:
            result.append(hunk.new_start + index)
    return result


def find_missing_appear(cov, repo):
    head = repo.head
    for parent in head.parents:
        diff = parent.tree.diff(head.tree)
        for hunk in diff.changes['hunks']:
            try:
                missing = cov.analysis(os.path.join(repo.workdir, hunk.new_file))[2]
            except coverage.misc.NotPython:
                continue
            addition = collect_addition(hunk)
            missing_appear = set(missing) & set(addition)
            if missing_appear:
                yield hunk, missing_appear


FAIL = '\033[91m'
ENDC = '\033[0m'


def report(cov, repo):
    head = repo.head
    for hunk, missing_appear in find_missing_appear(cov, repo):
        missing_index = map(lambda num: num - hunk.new_start + 1,
                            missing_appear)
        print(hunk.new_file)
        print(hunk.header)
        i = 0
        for line in hunk.data:
            line_stat = line[1]
            if line_stat in (pygit2.GIT_DIFF_LINE_CONTEXT,
                             pygit2.GIT_DIFF_LINE_ADDITION):
                i += 1
            if line_stat == pygit2.GIT_DIFF_LINE_CONTEXT:
                prefix = " "
            elif line_stat == pygit2.GIT_DIFF_LINE_ADDITION:
                prefix = "+"
            elif line_stat == pygit2.GIT_DIFF_LINE_DELETION:
                prefix = "-"
            else:
                # XXX maybe some unknown stats..
                print("Unknown stat: {}".format(line_stat), file=sys.stderr)
                continue

            line_data = line[0].rstrip()

            if i in missing_index and line_stat != pygit2.GIT_DIFF_LINE_DELETION:
                # found the line missing appear
                print(FAIL + "{0}{1}".format(prefix, line_data) + ENDC)
            else:
                print("{0}{1}".format(prefix, line_data))


def main():
    if len(sys.argv) > 1:
        target_repository = sys.argv[1]
    else:
        target_repository = os.getcwd()

    _git = os.path.join(target_repository, '.git')
    _coverage = os.path.join(target_repository, '.coverage')
    if not os.path.isdir(_git):
        raise IOError(".git not exists")
    if not os.path.exists(_coverage):
        raise IOError(".coverage not exists")

    repo = pygit2.Repository(_git)
    cov = coverage.coverage(_coverage)
    cov.load()

    report(cov, repo)


if __name__ == '__main__':
    main()
