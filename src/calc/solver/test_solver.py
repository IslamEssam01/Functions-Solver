import pytest
from .solver import solve


def test_solver():
    test_cases = [
        (
            "2x + 1",
            "x - 3",
            [-4.0],
            False,
            "Linear equation with root in interval"
        ),
        (
            "x^2",
            "4",
            [-2.0, 2.0],
            False,
            "Quadratic equation (negative root)"
        ),
        (
            "log10(x)",
            "1",
            [10.0],
            False,
            "Logarithmic equation"
        ),
        (
            "x^3 - 5*x",
            "0",
            [2.2361,
             -2.2361, 0],  # Root ≈ √5
            False,
            "Cubic equation"
        ),
        (
            "x^2+4",
            "0",
            [],
            False,
            "No roots in real domain"
        ),
        (
            "x^2+3",
            "--3+x^2",
            [],
            True,
            "Same function"
        ),

    ]
    for f1_str, f2_str, expected_roots, expected_is_same, test_name in test_cases:
        roots, is_same = solve(f1_str, f2_str)
        roots.sort()
        expected_roots.sort()
        assert len(roots) == len(expected_roots), f"Test failed: {test_name}"
        assert is_same == expected_is_same, f"Test failed: {test_name}"

        for i in range(len(roots)):
            assert round(roots[i], 4) == pytest.approx(
                expected_roots[i], abs=1e-6), f"Test failed: {test_name}"
