"""Anti-pattern audit.

Verifies, by static AST analysis, that the agentic loop does NOT:
- use string-membership tests against text content to drive control flow
- use an integer-literal iteration cap as its primary stopping mechanism
- omit reference to `stop_reason` as the loop-breaking signal

And that the package broadly does not branch on `claim_type` equality
outside of the tool-schema definitions and the cost-estimate module.

Each test parses the relevant file with `ast` and walks the tree. There are
no runtime imports of claims_intake here — the audit is static, so it works
even if loop.py / tools.py do not run end-to-end.
"""

from __future__ import annotations

import ast
from pathlib import Path

PKG = Path(__file__).resolve().parents[1] / "claims_intake"
LOOP_PY = PKG / "loop.py"


def _parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


# ---------------------------------------------------------------------------
# Anti-pattern 1 — no string-membership tests against assistant text in the loop
# ---------------------------------------------------------------------------
def test_no_string_membership_against_text_in_loop() -> None:
    """No `"some_token" in <something>` expressions in loop.py."""
    tree = _parse(LOOP_PY)
    offenders: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            if any(isinstance(op, ast.In) for op in node.ops):
                if isinstance(node.left, ast.Constant) and isinstance(
                    node.left.value, str
                ):
                    offenders.append(ast.unparse(node))

    assert not offenders, (
        "Found string-membership control flow in loop.py: "
        + ", ".join(offenders)
    )


# ---------------------------------------------------------------------------
# Anti-pattern 2 — no integer-literal iteration cap as the primary stop mechanism
# ---------------------------------------------------------------------------
def test_no_integer_literal_iteration_cap_in_loop() -> None:
    """No `for _ in range(<int literal>)` or `while <var> < <int literal>`."""
    tree = _parse(LOOP_PY)
    offenders: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            iterator = node.iter

            if (
                isinstance(iterator, ast.Call)
                and isinstance(iterator.func, ast.Name)
                and iterator.func.id == "range"
                and any(
                    isinstance(arg, ast.Constant)
                    and isinstance(arg.value, int)
                    and not isinstance(arg.value, bool)
                    for arg in iterator.args
                )
            ):
                offenders.append(ast.unparse(node))

        elif isinstance(node, ast.While):
            test = node.test

            if isinstance(test, ast.Compare):
                if any(
                    isinstance(op, (ast.Lt, ast.LtE, ast.Gt, ast.GtE))
                    for op in test.ops
                ):
                    if any(
                        isinstance(comparator, ast.Constant)
                        and isinstance(comparator.value, int)
                        and not isinstance(comparator.value, bool)
                        for comparator in test.comparators
                    ):
                        offenders.append(ast.unparse(node))

    assert not offenders, (
        "Found integer-literal iteration cap in loop.py; "
        "use a Budget instead: "
        + ", ".join(offenders)
    )


# ---------------------------------------------------------------------------
# Positive evidence — stop_reason is the value that breaks the while loop
# ---------------------------------------------------------------------------
def test_stop_reason_is_loop_control() -> None:
    """loop.py references stop_reason and uses it to exit the while loop."""
    tree = _parse(LOOP_PY)

    has_stop_reason_reference = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == "stop_reason":
            has_stop_reason_reference = True
            break

        if isinstance(node, ast.Attribute) and node.attr == "stop_reason":
            has_stop_reason_reference = True
            break

    assert has_stop_reason_reference, (
        "loop.py must reference stop_reason as the loop control signal"
    )

    while_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.While)]

    assert while_nodes, "loop.py must contain a while loop"

    stop_reason_controls_loop = False

    for while_node in while_nodes:
        body_text = ast.unparse(while_node)

        if "stop_reason" in body_text and (
            "return" in body_text or "raise" in body_text
        ):
            stop_reason_controls_loop = True
            break

    assert stop_reason_controls_loop, (
        "A while loop must exit via return/raise based on stop_reason"
    )


# ---------------------------------------------------------------------------
# Decision-tree-in-Python — no `if claim_type == "..."` branches in the package
# ---------------------------------------------------------------------------
def test_no_claim_type_equality_branching_in_package() -> None:
    """Decision logic about claim type lives in the model, not in Python."""
    offenders: list[str] = []

    for path in PKG.rglob("*.py"):
        if path.name in {"tools.py", "pricing.py", "__init__.py"}:
            continue

        tree = _parse(path)

        for node in ast.walk(tree):
            if not isinstance(node, ast.Compare):
                continue

            if not any(isinstance(op, ast.Eq) for op in node.ops):
                continue

            left = node.left

            left_is_claim_type = (
                isinstance(left, ast.Name) and left.id == "claim_type"
            ) or (
                isinstance(left, ast.Attribute) and left.attr == "claim_type"
            )

            if not left_is_claim_type:
                continue

            if any(
                isinstance(comparator, ast.Constant)
                and isinstance(comparator.value, str)
                for comparator in node.comparators
            ):
                offenders.append(
                    f"{path.name}:{node.lineno}: {ast.unparse(node)}"
                )

    assert not offenders, (
        "Do not branch on claim_type in Python. "
        "Move the decision into the model via tool calls: "
        + ", ".join(offenders)
    )