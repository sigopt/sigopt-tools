#!/usr/bin/env python3
# Copyright © 2022 Intel Corporation
#
# SPDX-License-Identifier: Apache License 2.0

import argparse
import sys


required_directives = [
  ("set -e", ("set +e", "# no_set_e")),
  ("set -o pipefail", ("set +o pipefail", "# no_pipefail")),
  ("#!/usr/bin/env bash", ("#!/usr/bin/env sh",)),
]


def shell_lint(file):
  lines = file.readlines()
  for directive, alternatives in required_directives:
    for line in lines:
      line = line.strip()
      if line == directive or line in alternatives:
        break
    else:
      yield f"error: Missing `{directive}` directive."


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("files", type=str, nargs="+", help="File to lint")
  args = parser.parse_args()
  responses = []
  for path in args.files:
    with open(path) as fp:
      responses.extend([f"{path}: {error}" for error in shell_lint(fp)])
  if responses:
    print("\n".join(responses))  # noqa: T001
    sys.exit(1)
