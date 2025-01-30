from typing import Callable, Any

import numpy as np
from numpy.typing import NDArray


from ..calc.lexer.lexer import Lexer
from ..calc.ast.ast import ASTNode
from ..calc.parser.parser import Parser
from ..calc.evaluator.evaluator import Evaluator
from ..calc.evaluator.evaluator import EvaluatorError


def evaluator_function(ast: ASTNode) -> Callable[[int | float], int | float]:
    return Evaluator(ast).evaluate


def parse_expression(expr: str) -> ASTNode:
    lexer = Lexer(expr)
    parser = Parser(lexer.tokens)
    return parser.parse()


def safe_evaluate(func: Callable[[int | float], int | float], x_values: NDArray[np.floating[Any]]):
    y: list[float] = []
    for x in x_values:
        try:
            y.append(func(x))
        except EvaluatorError:
            y.append(np.nan)  # Mark undefined points as NaN
    return np.array(y)


def adaptive_sampling(func: Callable[[int | float], int | float], x_min: int, x_max: int, num_points: int = 1000, must_evaluate_points: list[float | int] = [], tolerance: float = 1e-3):
    must_evaluate_points = must_evaluate_points.copy()
    must_evaluate_points.append(0)
    x: NDArray[np.floating[Any]] = np.union1d(np.linspace(min(x_min, -100),
                                                          max(x_max, 100), num_points), must_evaluate_points)
    y = safe_evaluate(func, x)

    dy = np.abs(np.diff(y))
    high_curvature = np.where(dy > tolerance)[0]

    new_x: list[float] = []
    for i in high_curvature:
        new_x.extend(np.linspace(x[i], x[i + 1], 10))
    x: NDArray[np.floating[Any]] = np.sort(np.union1d(x, new_x))

    return x, safe_evaluate(func, x)
