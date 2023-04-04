import ast

import pytest

from python_lint import AvoidDatetimeNowRule, LintNodeRule, SafeIteratorRule, SafeRecursiveRule, get_problems


class TestBase:
  Rule: LintNodeRule

  def check_file(self, content):
    rule = self.Rule()
    tree = ast.parse(content, "test.py")
    return get_problems(tree, [rule], {})

  def assert_errors(self, content, count=None):
    errors = list(self.check_file(content))
    if count is None:
      assert errors
    else:
      assert len(errors) == count


class TestAvoidDatetimeNowRule(TestBase):
  Rule = AvoidDatetimeNowRule

  @pytest.mark.parametrize("module", ["dt", "datetime"])
  @pytest.mark.parametrize("function", ["datetime.now", "datetime.utcnow"])
  def test_rule_errors(self, module, function):
    self.assert_errors(f"{module}.{function}()\n", count=1)

  @pytest.mark.parametrize(
    "example",
    [
      "current_datetime()",
    ],
  )
  def test_rule_pass(self, example):
    self.assert_errors(f"{example}\n", count=0)


class TestSafeRecursiveRule(TestBase):
  Rule = SafeRecursiveRule

  example_rule_pass = "\n".join(
    [
      "def recursive(x, y):",
      "  return recursive(y, x-1)",
      "",
    ]
  )
  example_rule_fail = "\n".join(
    [
      "def recursive(x, y):",
      "  return recursive(y)",
      "",
    ]
  )

  @pytest.mark.parametrize(
    "example,errors",
    [
      (example_rule_pass, 0),
      (example_rule_fail, 1),
    ],
  )
  def test_rule(self, example, errors):
    self.assert_errors(example, count=errors)


class TestSafeIteratorRule(TestBase):
  Rule = SafeIteratorRule

  @pytest.mark.parametrize(
    "returned",
    [
      "range(x)",
      "zip(x, y)",
      "map(int, x)",
      "filter(bool, x)",
    ],
  )
  def test_rule_errors_single_return(self, returned):
    content = "\n".join(
      [
        "def returns_unsafe_iterator(x):",
        f"  return {returned}",
        "",
      ]
    )
    self.assert_errors(content, count=1)

  @pytest.mark.parametrize(
    "returned_first",
    [
      "range(x)",
      "zip(x, y)",
      "map(int, x)",
      "filter(bool, x)",
    ],
  )
  @pytest.mark.parametrize(
    "returned_second",
    [
      "range(x)",
      "zip(x, y)",
      "map(int, x)",
      "filter(bool, x)",
    ],
  )
  def test_rule_errors_multiple_return(self, returned_first, returned_second):
    content = "\n".join(
      [
        "def returns_unsafe_iterator(x):",
        "  if x:",
        f"    return {returned_first}",
        f"  return {returned_second}",
        "",
      ]
    )
    self.assert_errors(content, count=2)
