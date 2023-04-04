import ast

import pytest

from python_lint import (
  AddingStringsRule,
  AvoidDatetimeNowRule,
  ForbidTestSuiteInheritanceRule,
  GeneratorExpressionRule,
  LintNodeRule,
  ProtobufMethodsRule,
  SafeIteratorRule,
  SafeRecursiveRule,
  SafeYieldRule,
  TrailingCommaRule,
  get_problems,
)


class Base:
  Rule: LintNodeRule

  def check(self, content):
    rule = self.Rule()
    tree = ast.parse(content, "test.py")
    return get_problems(tree, [rule], {})

  def assert_errors(self, content, count=None):
    errors = list(self.check(content))
    if count is None:
      assert errors
    else:
      assert len(errors) == count


class TestAvoidDatetimeNowRule(Base):
  Rule = AvoidDatetimeNowRule

  @pytest.mark.parametrize("module", ["dt", "datetime"])
  @pytest.mark.parametrize("function", ["datetime.now", "datetime.utcnow"])
  def test_rule_fail(self, module, function):
    self.assert_errors(f"{module}.{function}()\n", count=1)

  @pytest.mark.parametrize(
    "example",
    [
      "current_datetime()",
    ],
  )
  def test_rule_pass(self, example):
    self.assert_errors(f"{example}\n", count=0)


class TestSafeRecursiveRule(Base):
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


class TestSafeIteratorRule(Base):
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
  def test_rule_fail_single_return(self, returned):
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
  def test_rule_fail_multiple_return(self, returned_first, returned_second):
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

  @pytest.mark.parametrize(
    "returned",
    [
      "range(x)",
      "zip(x, y)",
      "map(int, x)",
      "filter(bool, x)",
    ],
  )
  def test_rule_pass_safe_iterator_wrap(self, returned):
    content = "\n".join(
      [
        "def returns_safe_iterator(x):",
        f"  return safe_iterator({returned})",
        "",
      ]
    )
    self.assert_errors(content, count=0)

  @pytest.mark.parametrize(
    "returned",
    [
      "range(x)",
      "zip(x, y)",
      "map(int, x)",
      "filter(bool, x)",
    ],
  )
  def test_rule_pass_safe_yield_from(self, returned):
    content = "\n".join(
      [
        "def returns_safe_iterator(x):",
        f"  yield from {returned}",
        "",
      ]
    )
    self.assert_errors(content, count=0)


class TestProtobufMethodsRule(Base):
  Rule = ProtobufMethodsRule

  @pytest.mark.parametrize(
    "method",
    [
      "CopyFrom",
      "MergeFrom",
    ],
  )
  def test_rule_fail(self, method):
    content = f"x.{method}(y)\n"
    self.assert_errors(content, count=1)

  @pytest.mark.parametrize(
    "method",
    [
      "CopyFrom",
      "MergeFrom",
    ],
  )
  def test_rule_pass(self, method):
    content = f"{method}(x, y)\n"
    self.assert_errors(content, count=0)


class TestSafeYieldRule(Base):
  Rule = SafeYieldRule

  @pytest.mark.parametrize(
    "decorator",
    [
      "generator_to_list",
      "generator_to_dict",
      "generator_to_safe_iterator",
      "unsafe_generator",
      "contextmanager",
      "fixture",
      "hookimpl",
    ],
  )
  @pytest.mark.parametrize(
    "statement",
    [
      "yield 1",
      "yield from range(10)",
    ],
  )
  def test_rule_pass_with_decorator(self, decorator, statement):
    content = "\n".join(
      [
        f"@{decorator}",
        "def generator():",
        f"  {statement}",
      ]
    )
    self.assert_errors(content, count=0)

  @pytest.mark.parametrize(
    "statement",
    [
      "yield 1",
      "yield from range(10)",
    ],
  )
  def test_rule_fail(self, statement):
    content = "\n".join(
      [
        "def generator():",
        f"  {statement}",
      ]
    )
    self.assert_errors(content, count=1)

  def test_rule_fail_mixed_yield_return(self):
    content = "\n".join(
      [
        "def generator():",
        "  if True:",
        "    yield 1",
        "  return []",
      ]
    )
    problems = list(self.check(content))
    assert len(problems) == 1
    assert problems[0][0].startswith("Do not mix ")


class TestTrailingCommaRule(Base):
  Rule = TrailingCommaRule

  @pytest.mark.parametrize(
    "example",
    [
      "x = 1,",
      "x += 1,",
      "print(1),",
      "1,",
      "def func(x):\n  return x,\n",
      "def func(x):\n  yield x,\n",
    ],
  )
  def test_rule_fail(self, example):
    self.assert_errors(example, count=1)

  @pytest.mark.parametrize(
    "example",
    [
      "x = tuple((1,))",
      "x += tuple((1,))",
      "tuple((print(1),))",
      "tuple((1,))",
      "def func(x):\n  return tuple((x,))\n",
      "def func(x):\n  yield tuple((x,))\n",
    ],
  )
  def test_rule_pass(self, example):
    self.assert_errors(example, count=0)


class TestAddingStringsRule(Base):
  Rule = AddingStringsRule

  @pytest.mark.parametrize(
    "example",
    [
      "'test adding' + 'strings'\n",
    ],
  )
  def test_rule_fail(self, example):
    self.assert_errors(example, count=1)

  @pytest.mark.parametrize(
    "example",
    [
      "('test'\n'adding'\n'strings')\n",
    ],
  )
  def test_rule_pass(self, example):
    self.assert_errors(example, count=0)


class TestGeneratorExpressionRule(Base):
  Rule = GeneratorExpressionRule

  @pytest.mark.parametrize("builtin", ["map", "filter"])
  def test_rule_fail(self, builtin):
    content = f"{builtin}(int, range(10))\n"
    self.assert_errors(content, count=1)

  @pytest.mark.parametrize(
    "example",
    [
      "[int(x) for x in range(10)]\n",
      "[x for x in range(10) if int(x)]\n",
    ],
  )
  def test_rule_pass(self, example):
    self.assert_errors(example, count=0)


class TestForbidTestSuiteInheritanceRule(Base):
  Rule = ForbidTestSuiteInheritanceRule

  @pytest.mark.parametrize(
    "example",
    [
      "class TestClass(TestBase):\n  pass\n",
    ],
  )
  def test_rule_fail(self, example):
    self.assert_errors(example, count=1)

  @pytest.mark.parametrize(
    "example",
    [
      "class TestClass(Base):\n  pass\n",
    ],
  )
  def test_rule_pass(self, example):
    self.assert_errors(example, count=0)
