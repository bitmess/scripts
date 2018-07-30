# Copyright 2017 The Fuchsia Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import collections
import os
import os.path
import re
import subprocess


def _get_diff_base():
    """Returns the newest local commit that is also in the upstream branch, or
    "HEAD" if no such commit can be found. If no upstream branch is set, assumes
    that origin/master is the upstream.
    """
    try:
        with open(os.devnull, 'w') as devnull:
            try:
                upstream = subprocess.check_output([
                    "git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"
                ], stderr = devnull).strip()
            except subprocess.CalledProcessError:
                upstream = "origin/master"
            # Get local commits not in upstream.
            local_commits = filter(
                len,
                subprocess.check_output(
                    ["git", "rev-list", "HEAD", "^" + upstream, "--"]).split("\n"))
            if not local_commits:
                return "HEAD"

            # Return parent of the oldest commit.
            return subprocess.check_output(
                ["git", "rev-parse", local_commits[-1] + "^"],
                stderr = devnull).strip()

    except subprocess.CalledProcessError:
        return "HEAD"


def get_git_root():
    """Returns the path of the root of the git repository."""
    return subprocess.check_output(["git", "rev-parse",
                                    "--show-toplevel"]).strip()


def get_diff_files():
    """Returns absolute paths to files that are locally modified, staged or
    touched by any commits introduced on the local branch.
    """

    list_command = [
        "git", "diff-index", "--name-only",
        _get_diff_base()
    ]
    git_root_path = get_git_root()
    paths = filter(len, subprocess.check_output(list_command).split("\n"))
    return [ os.path.join(git_root_path, x) for x in paths ]


def get_modified_lines(paths):
    """Returns ranges of lines modified in the specified files.

    Args:
        paths: A sequence of filenames to check for modified lines. Typically
               a subset of the paths returned by get_diff_files().

    Returns:
        A dict mapping elements of `paths` to sequences of 1-indexed
        (start-line-number, num-modified-lines) tuples.
    """
    # For a line like |+++ b/path/to/file.py|, extracts the filename
    # "path/to/file.py" in group 1, intentionally skipping the 'b/' component.
    filename_line_re = re.compile(r'^\+\+\+ [^/]+/(.*)')

    # For lines like
    #     @@ -9,1 +10,2 @@ Trailing text
    # or
    #     @@ -11,0 +12 @@ Trailing text
    # extracts the second field ('10,2' or '12' in the examples) in group 1.
    line_number_re = re.compile(r'^@@ -[0-9,]+ \+([0-9,]+) @@')

    git_root_path = get_git_root()

    # Diff output may be large, so stream the output rather than using
    # communicate().
    diff_command = ["git", "diff-index", "-U0", _get_diff_base()] + paths
    p = subprocess.Popen(diff_command, stdout=subprocess.PIPE)

    # Set up return dict. All input paths should have entries even if there
    # are no diffs.
    paths_to_ranges = collections.OrderedDict()
    for path in paths:
        paths_to_ranges[path] = []

    ranges = None  # Pointer to the current file's entry in `paths_to_ranges`
    with p.stdout:  # 'with' will close stdout on any exception
        for line in p.stdout:
            m = filename_line_re.match(line)
            if m:
                # Use absolute paths as keys.
                fname = os.path.join(git_root_path, m.group(1))
                ranges = paths_to_ranges[fname]
                continue
            m = line_number_re.match(line)
            if m:
                fields = m.group(1).split(',')
                if len(fields) == 1:
                    # If there's only one number,
                    # the range contains a single line.
                    fields.append('1')
                start = int(fields[0])
                count = int(fields[1])
                if count > 0:  # If zero, the range was deleted.
                    ranges.append((start, count))
    if p.wait():
        # Non-zero exit status.
        raise subprocess.CalledProcessError(p.returncode, diff_command)

    return paths_to_ranges


def get_all_files():
    """Returns absolute paths to all files in the git repo under the current
    working directory.
    """
    list_command = ["git", "ls-files"]
    paths = filter(len, subprocess.check_output(list_command).split("\n"))
    return [ os.path.abspath(x) for x in paths ]
