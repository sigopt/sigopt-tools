# Copyright © 2023 Intel Corporation
#
# SPDX-License-Identifier: Apache License 2.0
import io

import pytest

from check_copyright_and_license_disclaimers import COPYRIGHT, LICENSE, file_has_disclaimer


js_disclaimer = "\n".join(
  [
    "/**",
    f" * {COPYRIGHT}",
    " *",
    f" * {LICENSE}",
    " */",
    "",
  ]
)
js_example_1 = "\n".join(
  [
    "/**",
    "* top comment",
    "*/",
    "",
  ]
)
js_example_2 = 'import _ from "underscore";\n'

python_disclaimer = "\n".join(
  [
    f"# {COPYRIGHT}",
    "#",
    f"# {LICENSE}",
    "",
  ]
)

python_example_1 = "# top comment\n"
python_example_2 = "\n".join(
  [
    "'''",
    "Docstring",
    "'''",
    "",
  ]
)
python_example_3 = "from sys import stdout\n"

shell_disclaimer = python_disclaimer

shell_example_1 = "# top comment\n"
shell_example_2 = 'exec "$@"\n'

dockerfile_disclaimer = python_disclaimer

dockerfile_example_1 = "# top comment\n"
dockerfile_example_2 = "FROM debian:buster-slim\n"

markdown_disclaimer = "\n".join(
  [
    "<!--",
    f"{COPYRIGHT}",
    "",
    f"{LICENSE}",
    "-->",
    "",
  ]
)

markdown_example_1 = "\n".join(
  [
    "<!--",
    "top comment",
    "-->",
  ]
)

markdown_example_2 = "# Title\n"

less_disclaimer = js_disclaimer

less_example_1 = "\n".join(
  [
    "/**",
    "* top comment",
    "*/",
    "",
  ]
)
less_example_2 = '@import "../lib/constants.less";\n'


@pytest.mark.parametrize(
  "disclaimer,content,filetype",
  [
    (dockerfile_disclaimer, dockerfile_example_1, "Dockerfile"),
    (dockerfile_disclaimer, dockerfile_example_2, "Dockerfile"),
    (less_disclaimer, less_example_1, ".less"),
    (less_disclaimer, less_example_2, ".less"),
    (markdown_disclaimer, markdown_example_1, ".md"),
    (markdown_disclaimer, markdown_example_2, ".md"),
  ],
)
def test_file_has_disclaimer(disclaimer, content, filetype):
  file = io.StringIO(content)
  assert not file_has_disclaimer(file, filetype)
  file = io.StringIO(f"{disclaimer}{content}")
  assert file_has_disclaimer(file, filetype)


@pytest.mark.parametrize(
  "disclaimer,content,filetype,exc",
  [
    (js_disclaimer, js_example_1, ".js", "node"),
    (js_disclaimer, js_example_2, ".js", "node"),
    (python_disclaimer, python_example_1, ".py", "python3"),
    (python_disclaimer, python_example_2, ".py", "python3"),
    (python_disclaimer, python_example_3, ".py", "python3"),
    (shell_disclaimer, shell_example_1, ".sh", "bash"),
    (shell_disclaimer, shell_example_2, ".sh", "bash"),
  ],
)
@pytest.mark.parametrize("with_shebang", (False, True))
def test_file_has_disclaimer_maybe_with_shebang(disclaimer, content, filetype, exc, with_shebang):
  if with_shebang:
    content = f"#!/usr/bin/env {exc}\n{content}"
    content_with_disclaimer = f"#!/usr/bin/env {exc}\n{disclaimer}{content}"
  else:
    content_with_disclaimer = f"{disclaimer}{content}"
  file = io.StringIO(content)
  assert not file_has_disclaimer(file, filetype)
  file = io.StringIO(content_with_disclaimer)
  assert file_has_disclaimer(file, filetype)
