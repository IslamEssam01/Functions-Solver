from typing import Callable
import numpy as np

from PySide2.QtCore import QObject, QRunnable, Signal

from ..calc.solver.solver import solve

from ..utils.helpers import parse_expression, evaluator_function, adaptive_sampling


class PlotWorker(QRunnable):
    """
    A worker class to handle plotting of functions and their intersections in a separate thread.
    """

    def __init__(self, f1_str: str, f2_str: str, xlim: list[float], ylim: list[float], intersection_points: list[float]):
        """
        Initialize the PlotWorker.

        Args:
            f1_str (str): The string representation of the first function.
            f2_str (str): The string representation of the second function.
            xlim (list[float]): The x-axis limits as [xmin, xmax].
            ylim (list[float]): The y-axis limits as [ymin, ymax].
            intersection_points (list[float]): A list of x-coordinates of intersection points.
        """
        super().__init__()
        self.f1_str: str = f1_str
        self.f2_str: str = f2_str

        self.f1_evaluator: Callable[[int | float], int | float] | None = None

        self.xlim: list[float] = xlim
        self.ylim: list[float] = ylim
        self.intersection_points: list[float] = intersection_points
        self.signals = PlotSignals()

    def run(self):
        """
        The main execution method for the worker. Handles function parsing, sampling, and data preparation.
        """

        # Calculate the maximum x-scale limit based on the x-axis limits
        x_scale_max_limit = int(
            max(abs(self.xlim[0]), abs(self.xlim[1])))
        if self.intersection_points:
            x_scale_max_limit = int(
                max(max(map(abs, self.intersection_points))+100, x_scale_max_limit))

        x_scale_min_limit = -x_scale_max_limit

        num_points = int(500*(x_scale_max_limit-x_scale_min_limit))

        # Calculate the maximum y-scale limit based on the y-axis limits
        y_scale_max_limit = max(abs(self.ylim[0]), abs(self.ylim[1]))

        plot_data = {
            'x1': None, 'y1': None,
            'x2': None, 'y2': None,
            'xlim': self.xlim,
            'ylim': self.ylim,
            'x_scale_max_limit': x_scale_max_limit,
            'y_scale_max_limit': y_scale_max_limit
        }

        if self.intersection_points:
            x_center = float(np.mean(self.intersection_points))
            x_spread = max(abs(max(self.intersection_points) - x_center),
                           abs(min(self.intersection_points) - x_center))
            plot_data["xlim"][0] = int(x_center - max(x_spread * 2, 10))
            plot_data["xlim"][1] = int(x_center + max(x_spread * 2, 10))

        if self.f1_str:
            try:
                f1_ast = parse_expression(self.f1_str)
                self.f1_evaluator = evaluator_function(f1_ast)

                # Sample the function using adaptive sampling
                x, y1 = adaptive_sampling(
                    self.f1_evaluator, x_scale_min_limit, x_scale_max_limit,
                    num_points, self.intersection_points)

                # Update the y-scale limit based on the sampled y-values
                plot_data['y_scale_max_limit'] = max(
                    abs(np.nanmax(y1)), plot_data['y_scale_max_limit'])
                plot_data['x1'] = x
                plot_data['y1'] = y1
            except Exception as e:
                self.signals.error.emit((e, "f1"))

        if self.f2_str:
            try:
                f2_ast = parse_expression(self.f2_str)
                f2_evaluator = evaluator_function(f2_ast)

                # Sample the function using adaptive sampling
                x, y2 = adaptive_sampling(
                    f2_evaluator, x_scale_min_limit, x_scale_max_limit,
                    num_points, self.intersection_points)

                # Update the y-scale limit based on the sampled y-values
                plot_data['y_scale_max_limit'] = max(
                    abs(np.nanmax(y2)), plot_data['y_scale_max_limit'])
                plot_data['x2'] = x
                plot_data['y2'] = y2
            except Exception as e:
                self.signals.error.emit((e, "f2"))

        self.signals.finished.emit(
            (plot_data, self.intersection_points, self.f1_evaluator))


class PlotSignals(QObject):
    """
    A class to define signals for communication between the PlotWorker and the main thread.
    """
    finished = Signal(tuple)
    error = Signal(tuple)


class SolverWorker(QRunnable):
    """
    A worker class to handle solving for intersection points in a separate thread.
    """

    def __init__(self, f1_str: str, f2_str: str):
        """
        Initialize the SolverWorker.

        Args:
            f1_str (str): The string representation of the first function.
            f2_str (str): The string representation of the second function.
        """
        super().__init__()
        self.f1_str = f1_str
        self.f2_str = f2_str
        self.signals = SolverSignals()

    def run(self):
        """
        The main execution method for the worker. Solves for intersection points.
        """
        intersection_points, is_same = [], False
        try:
            intersection_points, is_same = solve(self.f1_str, self.f2_str)
        except:
            pass
        self.signals.finished.emit((intersection_points, is_same))


class SolverSignals(QObject):
    """
    A class to define signals for communication between the SolverWorker and the main thread.
    """
    finished = Signal(tuple)
