#!/usr/bin/env python3
# Copyright © 2022 Intel Corporation
#
# SPDX-License-Identifier: Apache License 2.0

import argparse
import datetime
import os
import re
import sys


parser = argparse.ArgumentParser()
parser.add_argument("files", action="extend", nargs="+", type=str)
parser.add_argument("--fix-in-place", "-f", action="store_true")
parser.add_argument("--license", required=True)
parser.add_argument("--owner", default="Intel Corporation")
parser.add_argument("--verbose", "-v", action="store_true")


YEAR = datetime.datetime.now().year
COPYRIGHT = f"Copyright © {YEAR} {{owner}}"
SPDX_LICENSE = "SPDX-License-Identifier: {license}"

DISCLAIMER_RE_LINES = [
  re.compile(r"^[ *#]*Copyright © [0-9]{4} .*$"),
  re.compile(r"^[ *#]*$"),
  re.compile(r"^[ *#]*SPDX-License-Identifier: .*$"),
]


class Filetype:
  dockerfile = "Dockerfile"
  js = ".js"
  less = ".less"
  markdown = ".md"
  python = ".py"
  shell = ".sh"


FILETYPES = (
  Filetype.dockerfile,
  Filetype.js,
  Filetype.less,
  Filetype.markdown,
  Filetype.python,
  Filetype.shell,
)

COMMENT_BLOCKS = {
  Filetype.dockerfile: ("", ""),
  Filetype.js: ("/**\n", " */\n\n"),
  Filetype.less: ("/**\n", " */\n"),
  Filetype.markdown: ("<!--\n", "-->\n\n"),
  Filetype.python: ("", ""),
  Filetype.shell: ("", ""),
}

COMMENT_LINES = {
  Filetype.dockerfile: "# ",
  Filetype.js: " * ",
  Filetype.less: " * ",
  Filetype.markdown: "",
  Filetype.python: "# ",
  Filetype.shell: "# ",
}


def guess_filetype(filename):
  for filetype in FILETYPES:
    if filename.endswith(filetype):
      return filetype
    # Filenames like "Dockerfile.api" are allowed
    if os.path.basename(filename).startswith(Filetype.dockerfile):
      return Filetype.dockerfile
  return None


def generate_disclaimer(filetype, license_, owner):
  opener, closer = COMMENT_BLOCKS[filetype]
  separator = COMMENT_LINES[filetype]
  copyright_line = COPYRIGHT.format(owner=owner)
  spdx_line = SPDX_LICENSE.format(license=license_)
  return "\n".join(
    [
      f"{opener}{separator}{copyright_line}",
      separator.rstrip(" "),
      f"{separator}{spdx_line}",
      f"{closer}",
    ]
  )


def file_has_disclaimer(file, filetype):
  to_check = []
  line = next(file)
  if line.startswith("#!"):
    line = next(file)
  if line in ("/**\n", "<!--\n"):
    line = next(file)
  to_check.append(line)
  to_check.extend(l for l, _ in zip(file, range(len(DISCLAIMER_RE_LINES) - 1)))

  to_check = "".join(to_check).split("\n")
  if len(to_check) < len(DISCLAIMER_RE_LINES):
    return False

  return all(regex.match(line) for regex, line in zip(DISCLAIMER_RE_LINES, to_check))


def file_needs_disclaimer(filename, verbose=False):
  filetype = guess_filetype(filename)
  if not filetype or os.stat(filename).st_size == 0:
    return False
  if verbose:
    print(f"Checking: {filename}")  # noqa: T001
  with open(filename) as fp:
    return not file_has_disclaimer(fp, filetype)


def fix_in_place(file, filetype, license_, owner):
  disclaimer = generate_disclaimer(filetype, license_, owner)
  maybe_shebang = file.readline()
  remaining = file.read()

  file.seek(0)

  if maybe_shebang.startswith("#!"):
    file.write(maybe_shebang + disclaimer + remaining)
  else:
    file.write(disclaimer + maybe_shebang + remaining)


def fix_all(filenames, license_, owner, verbose=False):
  failed_to_fix = []
  for filename in filenames:
    filetype = guess_filetype(filename)
    try:
      if verbose:
        print(f"Fixing {filename}")  # noqa: T001
      with open(filename, "r+") as fp:
        fix_in_place(fp, filetype, license_, owner)
    except Exception as e:
      print(f"failed to fix {filename}: {e}")  # noqa: T001
      failed_to_fix.append(filename)
    with open(filename) as fp:
      if not file_has_disclaimer(fp, filetype):
        print(f"fix did not work for {filename}")  # noqa: T001
        failed_to_fix.append(filename)
  return failed_to_fix


def main():
  args = parser.parse_args()
  missing = []
  for filename in args.files:
    if file_needs_disclaimer(filename, verbose=args.verbose):
      missing.append(filename)
  if args.fix_in_place:
    missing = fix_all(missing, license_=args.license, owner=args.owner, verbose=args.verbose)
  if missing:
    print(  # noqa: T001
      "\nThe following files failed the copyright + license check:\n\t" + "\n\t".join(f for f in missing)
    )
    sys.exit(1)
  elif args.verbose:
    print("\nAll files have disclaimer")  # noqa: T001


if __name__ == "__main__":
  main()
