import io

import pytest

from bash_lint import bash_lint


@pytest.mark.parametrize(
  "shebang,shebang_issues",
  [
    ("#!/usr/bin/env bash", 0),
    ("#!/usr/bin/env sh", 0),
    ("", 1),
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
def test_bash_lint(shebang, shebang_issues, sete, sete_issues, pipefail, pipefail_issues, script):
  content = "\n".join(
    [
      shebang,
      sete,
      pipefail,
      script,
    ]
  )
  file = io.StringIO(content)
  assert len(list(bash_lint(file))) == sum([shebang_issues, sete_issues, pipefail_issues])
