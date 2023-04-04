# Copyright © 2022 Intel Corporation
#
# SPDX-License-Identifier: Apache License 2.0

import io

import pytest

from shell_lint import shell_lint


@pytest.mark.parametrize(
  "shebang,shebang_issues",
  [
    ("#!/usr/bin/env bash", 0),
    ("#!/usr/bin/env sh", 0),
    ("#!/usr/bin/env python3", 1),
    ("", 1),
  ],
)
@pytest.mark.parametrize(
  "sete,sete_issues",
  [
    ("set -e", 0),
    ("set +e", 0),
    ("# no_set_e", 0),
    ("", 1),
  ],
)
@pytest.mark.parametrize(
  "pipefail,pipefail_issues",
  [
    ("set -o pipefail", 0),
    ("# no_pipefail", 0),
    ("", 1),
  ],
)
@pytest.mark.parametrize(
  "script",
  [
    "echo testing\n",
  ],
)
def test_shell_lint(shebang, shebang_issues, sete, sete_issues, pipefail, pipefail_issues, script):
  content = "\n".join(
    [
      shebang,
      sete,
      pipefail,
      script,
    ]
  )
  file = io.StringIO(content)
  assert len(list(shell_lint(file))) == sum([shebang_issues, sete_issues, pipefail_issues])
